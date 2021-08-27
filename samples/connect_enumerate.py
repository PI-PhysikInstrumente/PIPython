__signature__ = 0x8a454394b6c512a1a437c92962192176
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to search for controllers."""

# (c)2016-2020 Physik Instrumente (PI) GmbH & Co. KG
# Software products that are provided by PI are subject to the
# General Software License Agreement of Physik Instrumente (PI) GmbH & Co. KG
# and may incorporate and/or make use of third-party software components.
# For more information, please read the General Software License Agreement
# and the Third Party Software Note linked below.
# General Software License Agreement:
# http://www.physikinstrumente.com/download/EULA_PhysikInstrumenteGmbH_Co_KG.pdf
# Third Party Software Note:
# http://www.physikinstrumente.com/download/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf


from __future__ import print_function

from pipython import GCSDevice


def main():
    """Search controllers on interface, show dialog and connect a controller."""
    with GCSDevice() as pidevice:
        print('search for controllers...')
        devices = pidevice.EnumerateTCPIPDevices()
        # devices = EnumerateUSBDevices()
        for i, device in enumerate(devices):
            print('{} - {}'.format(i, device))
        item = int(input('select device to connect: '))
        pidevice.ConnectTCPIPByDescription(devices[item])
        # ConnectUSB(devices[item])
        print('connected: {}'.format(pidevice.qIDN().strip()))


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
