#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Interface class to communicate with a PI device."""

from abc import ABCMeta, abstractmethod, abstractproperty

__signature__ = 0x6f73be99e2558d53191aa50579bab527

PI_CONTROLLER_CODEPAGE = 'cp1252'

# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class PIGateway(object):
    """Interface (in terms of "base class") to communicate with a PI device.
    Members should log an according debug mesage.
    """

    __metaclass__ = ABCMeta
    _connection_status_changed_callbacks = []

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    def __str__(self):
        """Return class name with according parameter(s)."""
        raise NotImplementedError()

    @classmethod
    def call_connection_status_changed_callback(cls, gateway):
        """
        Called form the gateway if the connection state has changed
        :param gateway: the gateway
        """
        for callback in cls._connection_status_changed_callbacks:
            try:
                callback(gateway)
            except StopIteration:
                cls.unregister_connection_status_changed_callback(callback)
                continue
            except AttributeError:
                cls.unregister_connection_status_changed_callback(callback)
                continue

    @classmethod
    def register_connection_status_changed_callback(cls, callback):
        """
        Adds a callback function which is called at the end of the execute function
        :param callback: callback(<umf_service>, <umf_device>, ...)
        """
        if not callback in cls._connection_status_changed_callbacks and callback is not None:
            cls._connection_status_changed_callbacks.append(callback)

    @classmethod
    def unregister_connection_status_changed_callback(cls, callback):
        """
        Removes the callback function which is called at the end of the execute function
        :param callback: Callback function to remove
        """
        if callback in cls._connection_status_changed_callbacks:
            cls._connection_status_changed_callbacks.remove(callback)

    @abstractproperty
    def timeout(self):
        """Return timeout in milliseconds."""
        raise NotImplementedError()

    @abstractmethod
    def settimeout(self, value):
        """Set timeout to 'value' in milliseconds."""
        raise NotImplementedError()

    @abstractproperty
    def connected(self):
        """Return True if a device is connected."""
        raise NotImplementedError()

    @abstractproperty
    def connectionid(self):
        """Return ID of current connection as integer."""
        raise NotImplementedError()

    @abstractmethod
    def send(self, msg):
        """Send a GCS command to the device, do not query error from device.
        @param msg : GCS command as string with trailing line feed character.
        """
        raise NotImplementedError()

    @abstractmethod
    def read(self):
        """Return the answer to a GCS query command.
        @return : Answer as string.
        """
        raise NotImplementedError()

    @abstractmethod
    def flush(self):
        """Flush input buffer. Should be called once after connect."""
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        """Close connection if connected."""
        raise NotImplementedError()

    @abstractmethod
    def unload(self):
        """Close connection if connected."""
        raise NotImplementedError()
