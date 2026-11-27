#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide a device, connected via the PI GCS DLL."""

from ...PILogger import PIDebug
from ..gcsmessages import GCSMessages
from ..common.gcsbasedevice import GCSBaseDevice
from .gcs30commands import GCS30Commands

__signature__ = 0x1fd02950ee3e06b04ebda618c1f3c786


# Invalid method name pylint: disable=C0103
# Too many public methods pylint: disable=R0904
class GCS30Device(GCSBaseDevice, GCS30Commands):
    """Provide a device connected via the PI GCS DLL or antoher gateway, can be used as context manager."""

    def __init__(self, devname='', gcsdll='', gateway=None):
        """Provide a device, connected via the PI GCS DLL or another 'gateway'.
        @param devname : Name of device, chooses according DLL which defaults to PI_GCS2_DLL.
        @param gcsdll : Name or path to GCS DLL to use, overwrites 'devname'.
        @type gateway : pipython.pidevice.interfaces.pigateway.PIGateway
        """
        GCSBaseDevice.__init__(self, devname, gcsdll, gateway)
        messages = GCSMessages(self.dll)
        GCS30Commands.__init__(self, messages)

    def close(self):
        """Close connection to device and daisy chain."""
        PIDebug('GCS30Device.close()')
        self.unload()

    def CloseConnection(self):
        """Reset axes property and close connection to the device."""
        del self.axes
        GCSBaseDevice.CloseConnection(self)

    def GetError(self):
        """Get current controller error.
        @return : Current error code as integer.
        """
        return self.qERR()
