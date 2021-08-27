__signature__ = 0x12fc3196359278cda0827e2589c00345
# !/usr/bin/python
# -*- coding: utf-8 -*-
"""Move all axes to targets read from CSV file 'DATAFILE'."""

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
from time import sleep

from pipython import GCSDevice, pitools

CONTROLLERNAME = 'C-863.11'
STAGES = ['M-111.1DG', ]  # connect stages to axes
REFMODES = ['FNL', ]  # reference the connected stages

DATAFILE = 'targets_from_csv.csv'
RELAXTIME = 200  # time in ms to wait after each motion command or 0 to wait for on target state
SEPARATOR = ','


def main():
    """Connect controller, setup stages and move all axes to targets read from CSV file 'DATAFILE'."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.ConnectTCPIP(ipaddress='192.168.178.42')
        # pidevice.ConnectUSB(serialnum='123456789')
        # pidevice.ConnectRS232(comport=1, baudrate=115200)
        print('connected: {}'.format(pidevice.qIDN().strip()))
        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)
        movetotargets(pidevice)


def movetotargets(pidevice):
    """Move all axes to targets read from CSV file 'DATAFILE'.
    Add further columns if there are more than 6 axes connected.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    with open(DATAFILE, 'rb') as fobj:
        for line in fobj:
            targets = line.split(SEPARATOR)[:pidevice.numaxes]
            print('targets: {}'.format(', '.join(targets)))
            targets = [float(x) for x in targets]
            pidevice.MOV(pidevice.axes, targets)
            sleep(RELAXTIME / 1000.)
            if not RELAXTIME:
                pitools.waitontarget(pidevice)
    print('done')


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
