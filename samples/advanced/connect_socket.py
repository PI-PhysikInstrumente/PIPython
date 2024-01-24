#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to connect PIPython via socket."""

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


from pipython.pidevice.gcscommands import GCSCommands
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.interfaces.pisocket import PISocket

__signature__ = 0x51d08070e3f282f9d3a42dcfedf682ff

IPADDR = '192.168.90.166'


def main():
    """Connect controller via socket on port 50000."""
    with PISocket(host=IPADDR, port=50000) as gateway:
        print('interface: {}'.format(gateway))
        messages = GCSMessages(gateway)
        with GCSCommands(messages) as pidevice:
            print('connected: {}'.format(pidevice.qIDN().strip()))


if __name__ == '__main__':
    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)
    main()
