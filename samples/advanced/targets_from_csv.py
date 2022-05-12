# !/usr/bin/python
# -*- coding: utf-8 -*-
"""Move all axes to targets read from CSV file 'DATAFILE'."""

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


from time import sleep

from pipython import GCSDevice, pitools

__signature__ = 0x544ecdac060374e1ac098e78c6995cc1

CONTROLLERNAME = 'C-884'
STAGES = ['M-110K078', ]  # connect stages to axes
REFMODES = ['FRF', ]  # reference the connected stages

DATAFILE = 'targets_from_csv.csv' # Enter the absolute path to this file (targets_from_csv.csv)
RELAXTIME = 200  # time in ms to wait after each motion command or 0 to wait for on target state
SEPARATOR = ','


def main():
    """Connect controller, setup stages and move all axes to targets read from CSV file 'DATAFILE'."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.ConnectTCPIP(ipaddress='172.16.244.33')
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
    with open(DATAFILE, 'r') as fobj:
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
    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)
    main()
