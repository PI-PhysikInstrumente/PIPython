#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example connects to a PIPython device."""

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


from pipython import GCSDevice

__signature__ = 0x8b193828fd914ccc87e2198cb8a30417

def main():
    """Connect to a PIPython device."""

    # We recommend to use GCSDevice as context manager with "with".

    with GCSDevice() as pidevice:
        # Choose the interface which is appropriate to your cabling.

        pidevice.ConnectTCPIP(ipaddress='192.168.178.42')
        # pidevice.ConnectUSB(serialnum='104237344')
        # pidevice.ConnectRS232(comport=1, baudrate=115200)

        # Each PI controller supports the qIDN() command which returns an
        # identification string with a trailing line feed character which
        # we "strip" away.

        print('connected: {}'.format(pidevice.qIDN().strip()))

        # Show the version info which is helpful for PI support when there
        # are any issues.

        if pidevice.HasqVER():
            print('version info: {}'.format(pidevice.qVER().strip()))

        print('done - you may now continue with the simplemove.py example...')


if __name__ == '__main__':
    # To see what is going on in the background you can remove the following
    # two hashtags. Then debug messages are shown. This can be helpful if
    # there are any issues.

    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)

    main()
