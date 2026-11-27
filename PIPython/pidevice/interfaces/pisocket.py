#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide a socket."""

import socket

from ...PILogger import PIDebug
from .. import GCSError, gcserror
from ..interfaces.pigateway import PIGateway, PI_CONTROLLER_CODEPAGE

__signature__ = 0x59c603b46cab28bc52a1b9e4d21ed900


class PISocket(PIGateway):
    """Provide a socket, can be used as context manager."""

    def __init__(self, host='localhost', port=50000, autoconnect=True):
        """Provide a connected socket.
        @param host : IP address as string, defaults to "localhost".
        @param port : IP port to use as integer, defaults to 50000.
        @param autoconnect : automaticly connect to controller if True (default)
        """
        PIDebug('create an instance of PISocket(host=%s, port=%s)', host, port)
        self._timeout = 7000  # milliseconds
        self._host = host
        self._port = port
        self._connected = False
        self._socket = None
        if autoconnect:
            self.ConnectTCPIP(self._host, self._port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'PISocket(host=%s, port=%s)' % (self._host, self._port)

    @property
    def timeout(self):
        """Return timeout in milliseconds."""
        return self._timeout

    def settimeout(self, value):
        """Set timeout to 'value' in milliseconds."""
        self._timeout = value

    @property
    def connected(self):
        """Return True if a device is connected."""
        return self._connected

    @property
    def connectionid(self):
        """Return 0 as ID of current connection."""
        return 0

    def send(self, msg):
        """Send 'msg' to the socket.
        @param msg : String to send.
        """
        PIDebug('PISocket.send: %r', msg)
        if self._socket.send(msg.encode(PI_CONTROLLER_CODEPAGE)) != len(msg):
            raise GCSError(gcserror.E_2_SEND_ERROR)

    def read(self):
        """Return the answer to a GCS query command.
        @return : Answer as string.
        """
        try:
            received = self._socket.recv(2048)
            PIDebug('PISocket.read: %r', received)
        except IOError:
            return u''
        return received.decode(encoding=PI_CONTROLLER_CODEPAGE, errors='ignore')

    def flush(self):
        """Flush input buffer."""
        PIDebug('PISocket.flush()')
        while True:
            try:
                self._socket.recv(2048)
            except IOError:
                break

    def unload(self):
        self.close()

    def close(self):
        """Close socket."""
        PIDebug('PISocket.close: close connection to %s:%s', self._host, self._port)
        self._connected = False
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
        self.call_connection_status_changed_callback(self)

    # Method name "ConnectRS232" doesn't conform to snake_case naming style pylint: disable=C0103
    def ConnectTCPIP(self, ipaddress, ipport=50000):
        """Open a socket to the device.
           @param ipaddress: IP address to connect to as string.
           @param ipport: Port to use as integer, defaults to 50000.
       """
        self._host = ipaddress
        self._port = ipport
        PIDebug('PISocket.connect: open connection to %s:%s', self._host, self._port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host, self._port))
        self._socket.setblocking(0)
        self._socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)  # disable Nagle algorithm
        self._connected = True
        self.flush()
        self.call_connection_status_changed_callback(self)
