#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide GCS functions to control a PI device."""

from . import GCS2Commands
from . import GCS30Commands
from .common.gcsbasecommands import GCSBaseCommands
from .common.gcscommands_helpers import isdeviceavailable
from . import GCS30Error
from . import isgcs30

__signature__ = 0x445e365b92d08fcba7b68a70ce51ee97

class GCSCommands():
    """Provide a device connected via the PI GCS DLL or antoher gateway, can be used as context manager."""

    def __init__(self, gcsmessage=None, _is_umf=False, gcscommands=None):
        """Provide a device, connected via the PI GCS DLL or another 'gateway'.
        @param devname : Name of device, chooses according DLL which defaults to PI_GCS2_DLL.
        @param gcsdll : Name or path to GCS DLL to use, overwrites 'devname'.
        @type gateway : pipython.pidevice.interfaces.pigateway.PIGateway
        """
        if not gcsmessage:
            raise TypeError("gcsmessage must not be 'None' and must be connected to the controller")

        self._gcsmessage = gcsmessage
        if gcscommands is None:
            self._gcscommands = GCSBaseCommands(self._gcsmessage)
        else:
            self._gcscommands = gcscommands(self._gcsmessage)

        self._gcsmessage.interface.register_connection_status_changed_callback(self.connection_status_changed)

        if self._gcsmessage and self._gcsmessage.connected:
            self._downcast_gcscommands_if_necessary()

    def __getattr__(self, name):
        return getattr(self._gcscommands, name)

    def __setattr__(self, name, value):
        private_name = name
        if not name.startswith('_'):
            private_name = '_' + private_name

        if '_gcscommands' in self.__dict__ and  private_name not in self.__dict__:
            self._gcscommands.__setattr__(name, value)
        else:
            self.__dict__[name] = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        self._gcsmessage.interface.unregister_connection_status_changed_callback(self.connection_status_changed)

    @property
    def gcscommands(self):
        """
        returns the gcscommands object
        """
        return self._gcscommands

    def connection_status_changed(self, gateway):
        """
        Callback called by the gateway if the connection state has changed
        :param gateway: the gateway
        """
        if gateway.connected:
            self. _downcast_gcscommands_if_necessary()

    def _downcast_gcscommands_if_necessary(self):
        if isdeviceavailable([GCSBaseCommands, ], self._gcscommands):
            if isgcs30(self._gcsmessage):
                self._gcscommands = self._cast_gcscommands_to_type(self._gcscommands, GCS30Commands)
                self._gcsmessage.gcs_error_class = GCS30Error
            else:
                self._gcscommands = self._cast_gcscommands_to_type(self._gcscommands, GCS2Commands)

    def _cast_gcscommands_to_type(self, source_gcs_commands_object, target_gcs_commands_object_type):
        gcscommands = target_gcs_commands_object_type(self._gcsmessage)
        gcscommands.__dict__.update(source_gcs_commands_object.__dict__)
        return gcscommands
