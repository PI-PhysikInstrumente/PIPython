__signature__ = 0x9c8d857a9bceb6de1c59bb3366f41728
#!/usr/bin python
# -*- coding: utf-8 -*-
"""This example shows how to realize a cyclic circular motion with trajectories."""

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


from math import cos, sin, pi

from pipython import GCSDevice, pitools
from pipython.datarectools import getservotime

CONTROLLERNAME = 'C-867.2U2'
STAGES = []  # connect stages to axes
REFMODE = []  # reference the connected stages

PERIOD = 5.0  # duration of one sine period in seconds as float
CENTERPOS = (0.0, 0.0)  # center position of the circular motion as float for both axes
AMPLITUDE = (10.0, 10.0)  # amplitude (i.e. diameter) of the circular motion as float for both axes
BUFFERMIN = 200  # minimum number of points in buffer until motion is started


def main():
    """Connect controller, setup stages and start trajectories."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        #pidevice.ConnectRS232(comport=1, baudrate=115200)
        pidevice.ConnectUSB(serialnum='0116023162')
        # pidevice.ConnectTCPIP(ipaddress='192.168.178.42')
        print('connected: {}'.format(pidevice.qIDN().strip()))
        print('maximum buffer size: {}'.format(pidevice.qSPA(1, 0x22000020)[1][0x22000020]))
        print('initialize connected stages...')
       # pitools.startup(pidevice, stages=STAGES, refmode=REFMODE)
        runprofile(pidevice)


def runprofile(pidevice):
    """Move to start position, set up and run trajectories and wait until they are finished.
    @type pidevice : pipython.gcscommands.GCSCommands
    """
    assert 2 == len(pidevice.axes[:2]), 'this sample requires two connected axes'
    trajectories = (1, 2)
    numpoints = pidevice.qSPA(1, 0x22000020)[1][0x22000020]  # maximum buffer size
    xvals = [2 * pi * float(i) / float(numpoints) for i in range(numpoints)]
    xtrajectory = [CENTERPOS[0] + AMPLITUDE[0] / 2.0 * sin(xval) for xval in xvals]
    ytrajectory = [CENTERPOS[1] + AMPLITUDE[1] / 2.0 * cos(xval) for xval in xvals]
    print('move axes {} to their start positions {}'.format(pidevice.axes[:2], (xtrajectory[0], ytrajectory[0])))
    pidevice.MOV(pidevice.axes[:2], (xtrajectory[0], ytrajectory[0]))
    pitools.waitontarget(pidevice, pidevice.axes[:2])
    servotime = getservotime(pidevice)
    tgtvalue = int(float(PERIOD) / float(numpoints) / servotime)
    print('set %d servo cycles per point -> period of %.2f seconds' % (tgtvalue, tgtvalue * servotime * numpoints))
    pidevice.TGT(tgtvalue)
    print('trajectory timing: {}'.format(pidevice.qTGT()))
    print('clear existing trajectories')
    pidevice.TGC(trajectories)
    pointnum = 0
    print('\r%s' % (' ' * 40)),
    while pointnum < numpoints:
        if pidevice.qTGL(1)[1] < BUFFERMIN:
            pidevice.TGA(trajectories, (xtrajectory[pointnum], ytrajectory[pointnum]))
            pointnum += 1
            print('\rappend point {}/{}'.format(pointnum, numpoints)),
        if BUFFERMIN == pointnum:
            print('\nstarting trajectories')
            pidevice.TGS(trajectories)
        if numpoints == pointnum:
            print('\nfinishing trajectories')
            pidevice.TGF(trajectories)
    pitools.waitontrajectory(pidevice, trajectories)
    print('done')


if __name__ == '__main__':
    # from pipython import PIlogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PIlogger.setLevel(DEBUG)
    main()
