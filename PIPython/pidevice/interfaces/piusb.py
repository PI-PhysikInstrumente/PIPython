#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide a USB Interface over LibUSB."""

import re

# Unable to import pylint: disable=E0401
import usb.core
import usb.util
import usb.backend.libusb1

from ...PILogger import PIDebug, PIError
from ..interfaces.pigateway import PIGateway, PI_CONTROLLER_CODEPAGE
from .. import GCSError, gcserror

__signature__ = 0x5f3da84b398b5a507ec2402b4cd59f40


class PIUSB(PIGateway):
    """Provide a PIUSB, can be used as context manager."""

    def __init__(self):
        """Provide a PIUSB."""
        PIDebug('create an instance of PIUSB()')
        self._timeout = 7000  # milliseconds
        self._ifnum = None
        self._reattach = False
        self._ep_out = None
        self._ep_in = None
        self._dev = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'PIUSB()'

    @property
    def timeout(self):
        """Return timeout in milliseconds."""
        return self._timeout

    def settimeout(self, value):
        """Set timeout to 'value' in milliseconds."""
        self._timeout = value

    def read(self):
        """Return the answer to a GCS query command.
        @return : Answer as string.
        """
        received = self._ep_in.read(self._ep_in.wMaxPacketSize, timeout=self.timeout).tobytes()
        PIDebug('PIUSB.read: %r', received)
        received = received.rstrip(b'\0')  # some controllers return their answer in a size of modulus 2
        return received.decode(encoding=PI_CONTROLLER_CODEPAGE, errors='ignore')

    @property
    def connected(self):
        """Return True if a device is connected."""
        return self._ifnum is not None

    @property
    def connectionid(self):
        """Get ID of current connection as integer or -1 if not connected."""
        if self._ifnum is None:
            return -1
        return self._ifnum

    @staticmethod
    def enumerate(vid=0x1a72, pid=None):
        """Enumerate all USB devices matching 'vid'.
        @param vid : USB Vendor ID as integer.
        @return : List of dicts with device info, all values as strings.
        """
        PIDebug('PIUSB.enumerate(vid=%#x)', vid)
        devicesinfo = []
        if not pid:
            devices = usb.core.find(find_all=True, idVendor=vid)
        else:
            devices = usb.core.find(find_all=True, idVendor=vid, idProduct=pid)

        for dev in devices:
            deviceinfo = {}
            deviceinfo.update({'Manufacturer': getdevinfo(dev, dev.iManufacturer)})
            deviceinfo.update({'Product': getdevinfo(dev, dev.iProduct)})
            deviceinfo.update({'SerialNumber': getdevinfo(dev, dev.iSerialNumber)})
            deviceinfo.update({'VID': hex(dev.idVendor)})
            deviceinfo.update({'PID': hex(dev.idProduct)})
            PIDebug('PIUSB.enumerate: %s', deviceinfo)
            devicesinfo.append(deviceinfo)
            usb.util.dispose_resources(dev)
        return devicesinfo

    def connect(self, serialnumber, pid, vid=0x1a72):
        """Connect to a USB device with 'serialnumber', 'pid' and 'vid' and flush input buffer.
        @param serialnumber : Serial number of the device as string.
        @param pid : USB Product ID of the device.
        @param vid : USB Vendor ID of the device.
        """
        PIDebug('PIUSB.connect(serialnumber=%s, pid=%#x, vid=%#x)', serialnumber, pid, vid)
        self._dev = self._find_device(serialnumber, pid, vid)
        self._dev.set_configuration()
        cfg = self._dev.get_active_configuration()
        self._ifnum = cfg[(0, 0)].bInterfaceNumber
        interface = usb.control.get_interface(self._dev, self._ifnum)
        descriptor = usb.util.find_descriptor(cfg, bInterfaceNumber=self._ifnum, bAlternateSetting=interface)
        self._ep_out = usb.util.find_descriptor(descriptor, custom_match=lambda e: usb.util.endpoint_direction(
            e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self._ep_in = usb.util.find_descriptor(descriptor, custom_match=lambda e: usb.util.endpoint_direction(
            e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        if self._dev.is_kernel_driver_active(self._ifnum):
            self._reattach = True
            self._dev.detach_kernel_driver(self._ifnum)
        usb.util.claim_interface(self._dev, self._ifnum)
        self.flush()
        self.call_connection_status_changed_callback(self)


    def flush(self):
        """Flush input buffer."""
        PIDebug('PIUSB.flush()')
        while True:
            try:
                self._ep_in.read(self._ep_in.wMaxPacketSize, timeout=100)
            except usb.USBError:
                break

    def send(self, msg):
        """Send a GCS command to the device, do not query error from device.
        @param msg : GCS command as string with trailing line feed character.
        """
        if len(msg) % 2:  # some controllers need a string of size of modulus 2
            msg += '\0'
        PIDebug('PIUSB.send: %r', msg)
        if self._ep_out.write(msg.encode(PI_CONTROLLER_CODEPAGE)) != len(msg):
            raise GCSError(gcserror.E_2_SEND_ERROR)

    def unload(self):
        self.close()

    def close(self):
        """Close connection if connected."""
        if not self.connected:
            return
        PIDebug('PIUSB.close: close connection ID %d', self.connectionid)
        usb.util.release_interface(self._dev, self._ifnum)
        if self._reattach:
            self._dev.attach_kernel_driver(self._ifnum)
        usb.util.dispose_resources(self._dev)
        self._ifnum = None
        self._reattach = False
        self._ep_out = None
        self._ep_in = None
        self._dev = None
        self.call_connection_status_changed_callback(self)

    @staticmethod
    def _find_device(serialnumber, pid, vid):
        """Find USB device according to serialnumber, PID and VID or raise GCS Error.
        @param serialnumber : Serial number of the device as string.
        @param pid : Device product ID as integer.
        @param vid : Device vendor ID as integer.
        @return : USB device instance.
        """
        PIDebug('PIUSB._find_device(serialnumber=%s, pid=%#x, vid=%#x)', serialnumber, pid, vid)
        devices = usb.core.find(find_all=True, idVendor=vid, idProduct=pid)
        if not devices:
            raise GCSError(gcserror.E_6_CONNECTION_FAILED)
        for dev in devices:
            PIDebug('PIUSB._find_device:\n%s', dev)
            if getdevinfo(dev, dev.iSerialNumber) == serialnumber:
                return dev
            usb.util.dispose_resources(dev)
        raise GCSError(gcserror.E_6_CONNECTION_FAILED)

    # Method name doesn't conform to snake_case naming style pylint: disable=C0103
    def ConnectUSB(self, serialnum, pid, vid=0x1a72):
        """Open an USB connection to a device.
        @param serialnum: Serial number of device or one of the
        identification strings listed by EnumerateUSB().
        @param pid : USB Product ID of the device (only for native usb).
        @param vid : USB Vendor ID of the device  (only for native usb).
        """
        self.connect(serialnum, pid, vid)


def getdevinfo(dev, stringid):
    """Return device info as string.
    @param dev : USB device instance.
    @param stringid : String descriptor index.
    @return : Device info string as string.
    """
    try:
        return re.sub('[^a-zA-Z0-9-_*. ]', '', usb.util.get_string(dev, stringid))
    except ValueError:
        PIError('probably you do not have permission to access USB descriptors')
        raise
