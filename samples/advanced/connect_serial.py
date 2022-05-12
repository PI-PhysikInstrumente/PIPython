#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to connect PIPython via serial port."""

# (c)2016 Physik Instrumente (PI) GmbH & Co. KG
# Software products that are provided by PI are subject to the
# General Software License Agreement of Physik Instrumente (PI) GmbH & Co. KG
# and may incorporate and/or make use of third-party software components.
# For more information, please read the General Software License Agreement
# and the Third Party Software Note linked below.
# General Software License Agreement:
# http://www.physikinstrumente.com/download/EULA_PhysikInstrumenteGmbH_Co_KG.pdf
# Third Party Software Note:
# http://www.physikinstrumente.com/download/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf


import sys

from pipython.pidevice.gcscommands import GCSCommands
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.interfaces.piserial import PISerial

__signature__ = 0xe5184c9a60a0c98663347f677824582a


def main():
    """Connect controller via first serial port with 115200 baud."""
    if sys.platform in ('linux', 'linux2', 'darwin'):
        port = '/dev/ttyS0'  # use '/dev/ttyUSB0' for FTDI-USB connections
    else:
        port = 'COM1'
    with PISerial(port=port, baudrate=115200) as gateway:
        print('interface: {}'.format(gateway))
        messages = GCSMessages(gateway)
        pidevice = GCSCommands(messages)
        print('connected: {}'.format(pidevice.qIDN().strip()))


if __name__ == '__main__':
    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)
    main()
