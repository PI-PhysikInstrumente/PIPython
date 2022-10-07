#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This example shows how to use the data recorder and how to plot and save the data."""

# (c) 2021 Physik Instrumente (PI) GmbH & Co. KG
# Software products that are provided by PI are subject to the
# General Software License Agreement of Physik Instrumente (PI) GmbH & Co. KG
# and may incorporate and/or make use of third-party software components.
# For more information, please read the General Software License Agreement
# and the Third Party Software Note linked below.
# General Software License Agreement:
# http://www.physikinstrumente.com/download/EULA_PhysikInstrumenteGmbH_Co_KG.pdf
# Third Party Software Note:
# http://www.physikinstrumente.com/download/TPSWNote_PhysikInstrumenteGmbH_Co_KG.pdf

"""This sample requires the python package matplotlib to work"""

from pipython import GCSDevice, datarectools, pitools

try:
    from matplotlib import pyplot
except ImportError:
    pyplot = None



__signature__ = 0xa325f76851b9413c83ef115ebab6c83

CONTROLLERNAME = 'E-880'  # 'C-884' will also work
STAGES = None
REFMODES = ['FRF', 'FRF']


NUMVALUES = 1024  # number of data sets to record as integer
RECORD_RATE = 1  # number of servo cycles between two recorded values

DATA_RECORDER_ID_1 = 'REC_1'
TRACE_ID_1 = 1
TRACE_ID_2 = 2

PARAMETER_1 = [ 'AXIS_1', '-', '0x102' ]
PARAMETER_2 = [ 'AXIS_1', '-', '0x103' ]

TRIGGER_NAME = 'MOV'
TRIGGER_OPTIONS_1 = 'AXIS_1'
TRIGGER_OPTIONS_2 = '0'

def main():
    """Connect device, set up stage and read and display datarecorder data."""

    # We recommend to use GCSDevice as context manager with "with".
    # The CONTROLLERNAME decides which PI GCS DLL is loaded. If your controller works
    # with the PI_GCS2_DLL (as most controllers actually do) you can leave this empty.

    with GCSDevice(CONTROLLERNAME) as pidevice:
        # Choose the interface according to your cabling.
        pidevice.ConnectTCPIP(ipaddress='localhost')
        # pidevice.ConnectUSB(serialnum='123456789')
        # pidevice.ConnectRS232(comport=1, baudrate=115200)

        # Each PI controller supports the qIDN() command which returns an
        # identification string with a trailing line feed character which
        # we "strip" away.
        print('connected: {}'.format(pidevice.qIDN().strip()))

        # Show the version info which is helpful for PI support when there
        # are any issues.
        if pidevice.HasqVER():
            print('version info:\n{}'.format(pidevice.qVER().strip()))

        # In the module pipython.pitools there are some helper
        # functions to make using a PI device more convenient. The "startup"
        # function will initialize your system. There are controllers that
        # cannot discover the connected stages hence we set them with the
        # "stages" argument. The desired referencing method (see controller
        # user manual) is passed as "refmode" argument. All connected axes
        # will be stopped if they are moving and their servo will be enabled.
        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)

        drec = datarectools.Datarecorder(pidevice, DATA_RECORDER_ID_1)

        print('Servo time [s]: {}'.format(drec.servotime))
        recorddata(drec)

        print('move stage on axis {}...'.format(pidevice.axes[0]))
        pitools.movetomiddle(pidevice, pidevice.axes[0])

        processdata(drec)


def recorddata(drec):
    """Set up data recorder to record 2 tables for first axis after next motion command.
    @type drec : pipython.datarectools.Datarecorder
    """
    drec.number_of_values = NUMVALUES
    drec.record_rate = RECORD_RATE
    print('data recorder rate: {:.2f} Hz'.format(drec.record_rate))

    drec.traces = { TRACE_ID_1: PARAMETER_1, TRACE_ID_2: PARAMETER_2 }
    drec.trigger = [ TRIGGER_NAME, TRIGGER_OPTIONS_1, TRIGGER_OPTIONS_2 ]
    drec.arm()


def processdata(drec):
    """Read out, plot and save data recorder data.
    @type drec : pipython.datarectools.Datarecorder
    """
    if pyplot is None:
        print('matplotlib is not installed')
        return
    pyplot.plot(drec.timescale, drec.data[0], color='red')
    pyplot.plot(drec.timescale, drec.data[1], color='blue')
    pyplot.xlabel('time (s)')
    pyplot.ylabel(', '.join((drec.header['NAME0'], drec.header['NAME1'])))
    pyplot.title('Datarecorder data over time')
    pyplot.grid(True)
    pyplot.show()
    print('save GCSArray to file "gcsarray.dat"')
    pitools.savegcsarray('gcsarray.dat', drec.header, drec.data)


if __name__ == '__main__':
    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)
    main()
