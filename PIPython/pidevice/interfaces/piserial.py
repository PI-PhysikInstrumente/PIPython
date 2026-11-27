#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide access to the serial port. Requires the "pyserial" package (pip install pyserial)."""

import serial

from ...PILogger import PIDebug
from ..interfaces.pigateway import PIGateway, PI_CONTROLLER_CODEPAGE


__signature__ = 0xdca3b828dfe0cfd9fad2ec504c040e6a


class PISerial(PIGateway):
    """Provide access to the serial port, can be used as context manager."""

    def __init__(self, port, baudrate, autoconnect=True):
        """Provide access to the serial port.
        @param port : Name of the serial port to use as string, e.g. "COM1" or "/dev/ttyS0".
        @param baudrate : Baud rate as integer.
        @param autoconnect : automaticly connect to controller if True (default)
        """
        PIDebug('create an instance of PISerial(port=%s, baudrate=%s)', port, baudrate)
        self._timeout = 7000  # milliseconds
        self._connected = False
        self._baudrate = baudrate
        self._port = port
        self._ser = None
        if autoconnect:
            self.ConnectRS232(self._port, self._baudrate)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'PISerial(port=%s, baudrate=%s)' % (self._port, self._baudrate)

    @property
    def timeout(self):
        """Return timeout in milliseconds."""
        return self._timeout

    def settimeout(self, value):
        """Set timeout to 'value' in milliseconds."""
        self._timeout = value
        self._ser.timeout = value / 1000.

    @property
    def connected(self):
        """Return True if a device is connected."""
        return self._connected

    @property
    def connectionid(self):
        """Return 0 as ID of current connection."""
        return 0

    def send(self, msg):
        """Send 'msg' to the serial port.
        @param msg : String to send.
        """
        PIDebug('PISerial.send: %r', msg)
        self._ser.write(msg.encode(PI_CONTROLLER_CODEPAGE))

    def read(self):
        """Return the answer to a GCS query command.
        @return : Answer as string.
        """
        received = self._ser.read_all()
        if len(received) != 0:
            PIDebug('PISerial.read: %r', received)
        return received.decode(encoding=PI_CONTROLLER_CODEPAGE, errors='ignore')

    def flush(self):
        """Flush input buffer."""
        PIDebug('PISerial.flush()')
        self._ser.read_all()

    def unload(self):
        self.close()

    def close(self):
        """Close serial port if connected."""
        if not self.connected:
            return
        PIDebug('PISerial.close: close connection to port %r', self._ser.port)
        self._connected = False
        self._ser.close()
        self.call_connection_status_changed_callback(self)

    # Method name "ConnectRS232" doesn't conform to snake_case naming style pylint: disable=C0103
    def ConnectRS232(self, port, baudrate):
        """Open access to the serial port.
        @param port : Name of the serial port to use as string, e.g. "COM1" or "/dev/ttyS0".
        @param baudrate : Baud rate as integer.
        """
        self._ser = serial.Serial(port=port, baudrate=baudrate, timeout=self._timeout / 1000.)
        self._connected = True
        self.flush()
        self.call_connection_status_changed_callback(self)
