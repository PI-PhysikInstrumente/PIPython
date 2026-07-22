#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tools for setting up and using the data recorder of a PI device."""

__signature__ = 0x3e5112fc34b726384b36efebbc6f6b79

from ..pidevice.common.gcsbasedatarectools import GCSBaseDatarecorder
from ..pidevice.gcs2.gcs2datarectools import GCS2Datarecorder
from ..pidevice.gcs30.gcs30datarectools import GCS30Datarecorder
from ..pidevice.gcs30.gcs30commands_helpers import isgcs30
from ..pidevice.gcs30.gcs30error import GCS30Error
from ..pidevice.common.gcscommands_helpers import isdeviceavailable


class Datarecorder():
    """
    Retuns an instance to the data recorder tools Datarecorder
    """
    def __init__(self, gcs, recorder_id=''):
        self._gcs = gcs
        self._recorder_id = recorder_id
        self._datarecorder = GCSBaseDatarecorder(gcs=gcs)

        self._gcs.messages.interface.register_connection_status_changed_callback(self.connection_status_changed)

        if self._gcs.messages and self._gcs.messages.connected:
            self._downcaste_datarecorder_if_necessary()

    def __getattr__(self, name):
        return getattr(self._datarecorder, name)

    def __setattr__(self, name, value):
        private_name = name
        if not name.startswith('_'):
            private_name = '_' + private_name

        if '_datarecorder' in self.__dict__ and private_name not in self.__dict__:
            self._datarecorder.__setattr__(name, value)
        else:
            self.__dict__[name] = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        self._gcs.messages.interface.unregister_connection_status_changed_callback(self.connection_status_changed)

    @property
    def datarecorder(self):
        """
        returns the datarecorder object
        :return: instance of GCSBaseDatarecorder or GCS2Datarecorder or GCS30Datarecorder
        """
        return self._datarecorder

    def connection_status_changed(self, gateway):
        """
        Callback called by the gateway if the connection state has changed
        :param gateway: the gateway
        """
        if gateway.connected:
            self. _downcaste_datarecorder_if_necessary()

    def _downcaste_datarecorder_if_necessary(self):
        if isdeviceavailable([GCSBaseDatarecorder, ], self._datarecorder):
            if isgcs30(self._gcs.messages):
                datarecorder = GCS30Datarecorder(self._gcs, self._recorder_id)
                self._gcs.messages.gcs_error_class = GCS30Error
            else:
                datarecorder = GCS2Datarecorder(self._gcs)

            datarecorder.__dict__.update(self._datarecorder.__dict__)
            self._datarecorder = datarecorder
