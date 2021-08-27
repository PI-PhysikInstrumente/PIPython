__signature__ = 0x3de195de202ecebe89850d7c4e34e893
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to use the data recorder and plot and save the data."""

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

try:
    from matplotlib import pyplot
except ImportError:
    pyplot = None

from pipython import GCSDevice, datarectools, pitools

CONTROLLERNAME = 'C-884'
STAGES = ['M-111.1DG', ]  # connect stages to axes
REFMODES = ['FNL', ]  # reference the connected stages

NUMVALUES = 1024  # number of data sets to record as integer
RECRATE = 2000  # number of recordings per second, i.e. in Hz


def main():
    """Connect device, set up stage and read and display datarecorder data."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.ConnectTCPIP(ipaddress='192.168.90.207')
        # pidevice.ConnectUSB(serialnum='123456789')
        # pidevice.ConnectRS232(comport=1, baudrate=115200)
        print('connected: {}'.format(pidevice.qIDN().strip()))
        print('initialize connected stages...')
        pitools.startup(pidevice, STAGES, REFMODES)
        drec = datarectools.Datarecorder(pidevice)
        recorddata(drec)
        print('move stage on axis {}...'.format(pidevice.axes[0]))
        pidevice.MVR(pidevice.axes[0], 0.1)
        processdata(drec)


def recorddata(drec):
    """Set up data recorder to record 2 tables for first axis after next motion command.
    @type drec : pipython.datarectools.Datarecorder
    """
    drec.numvalues = NUMVALUES
    drec.samplefreq = RECRATE
    print('data recorder rate: {:.2f} Hz'.format(drec.samplefreq))
    drec.options = (datarectools.RecordOptions.ACTUAL_POSITION_2,
                    datarectools.RecordOptions.COMMANDED_POSITION_1)
    drec.sources = drec.gcs.axes[0]
    drec.trigsources = datarectools.TriggerSources.POSITION_CHANGING_COMMAND_1
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
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
