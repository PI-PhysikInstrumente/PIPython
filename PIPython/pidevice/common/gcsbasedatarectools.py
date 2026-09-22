#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tools for setting up and using the data recorder of a PI device."""

from abc import abstractmethod

__signature__ = 0xc190f99f357acb1c503509d893b658f6

# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
# Too many instance attributes pylint: disable=R0902
class GCSBaseDatarecorder(object):
    """Set up and use the data recorder of a GCSdevice."""

    def __init__(self, gcs):
        self._gcs = gcs
        self._header = None
        self._data = None

    @property
    def gcs(self):
        """Access to GCS commands of controller."""
        return self._gcs

    @property
    @abstractmethod
    def header(self):
        """Return header from last controller readout."""

    @property
    @abstractmethod
    def data(self):
        """Return data from last controller readout."""

    @abstractmethod
    def arm(self):
        """Configures the data recorder based on the properties record_rate,
        traces and trigger. Finally the data recorder is set to state WAIT, so
        that it is ready for recording.
        """
