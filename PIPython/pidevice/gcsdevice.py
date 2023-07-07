#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide a device, connected via the PI GCS DLL."""

# Cyclic import (pipython -> pipython.gcsdevice) pylint: disable=R0401
from . import GCS30Error
from . import isgcs30

from .common.gcsbasedevice import GCSBaseDevice
from .common.gcscommands_helpers import isdeviceavailable
from .gcs30.gcs30device import GCS30Device
from .gcs2.gcs2device import GCS2Device

__signature__ = 0x7c25c5be2b1b288788d972911e2337eb


# Method 'GetError' is abstract in class 'GCSBaseDevice' but is not overridden pylint: disable=W0223
# Method 'close' is abstract in class 'GCSBaseDevice' but is not overridden pylint: disable=W0223
# Method 'devname' is abstract in class 'GCSBaseCommands' but is not overridden pylint: disable=W0223
# Method 'funcs' is abstract in class 'GCSBaseCommands' but is not overridden pylint: disable=W0223
# Method 'isavailable' is abstract in class 'GCSBaseDevice' but is not overridden pylint: disable=W0223
# Method 'paramconv' is abstract in class 'GCSBaseCommands' but is not overridden pylint: disable=W0223
# Method 'unload' is abstract in class 'GCSBaseDevice' but is not overridden pylint: disable=W0223
# Invalid method name pylint: disable=C0103
# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class GCSDevice():
    """Provide a device connected via the PI GCS DLL or antoher gateway, can be used as context manager."""

    def __init__(self, devname='', gcsdll='', gateway=None):
        """Provide a device, connected via the PI GCS DLL or another 'gateway'.
        @param devname : Name of device, chooses according DLL which defaults to PI_GCS2_DLL.
        @param gcsdll : Name or path to GCS DLL to use, overwrites 'devname'.
        @type gateway : pipython.pidevice.interfaces.pigateway.PIGateway
        """
        self._devname = devname
        self._gcsdll = gcsdll
        self._gateway = gateway
        self._gcsdevice = GCSBaseDevice(devname=devname, gcsdll=gcsdll, gateway=gateway)

        self._gcsdevice.messages.interface.register_connection_status_changed_callback(self.connection_status_changed)

        if self._gateway and self._gateway.connected:
            self._downcast_gcsdevice_if_necessary()

    def __getattr__(self, name):
        return getattr(self._gcsdevice, name)

    def __setattr__(self, name, value):
        private_name = name
        if not name.startswith('_'):
            private_name = '_' + private_name

        if '_gcsdevice' in self.__dict__ and private_name not in self.__dict__:
            self._gcsdevice.__setattr__(name, value)
        else:
            self.__dict__[name] = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        self._gcsdevice.messages.interface.unregister_connection_status_changed_callback(self.connection_status_changed)
        self._gcsdevice.close()

    def connection_status_changed(self, gateway):
        """
        Callback called by the gateway if the connection state has changed
        :param gateway: the gateway
        """
        if gateway.connected:
            self. _downcast_gcsdevice_if_necessary()

    @property
    def gcsdevice(self):
        """
        returns the gcs device object
        :return: instance of GCSBaseDevice or GCS2Device or GCS30Device
        """
        return self._gcsdevice

    @property
    def gcscommands(self):
        """
        returns the gcs device object
        :return: instance of GCSBaseCommands or GCS2Commands or GCS30DCommands
        """
        return self._gcsdevice.gcscommands

    def _downcast_gcsdevice_if_necessary(self):
        if isdeviceavailable([GCSBaseDevice, ], self._gcsdevice):
            if isgcs30(self._msgs):
                self._gcsdevice = self._cast_gcsdevice_to_type(self._gcsdevice, GCS30Device)
                self._init_settings()
                self._msgs.gcs_error_class = GCS30Error
            else:
                self._gcsdevice = self._cast_gcsdevice_to_type(self._gcsdevice, GCS2Device)

    def _cast_gcsdevice_to_type(self, source_gcs_device_object, target_gcs_devece_object_type):
        gcsdevice = target_gcs_devece_object_type(devname=self._devname, gcsdll=self._gcsdll, gateway=self._gateway)
        gcsdevice.__dict__.update(source_gcs_device_object.__dict__)
        return gcsdevice
