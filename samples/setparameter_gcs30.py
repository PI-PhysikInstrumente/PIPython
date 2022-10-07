#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example demonstrates how to read and write parameters with a GCS 3.0 device."""

# (c)2021 Physik Instrumente (PI) GmbH & Co. KG
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

__signature__ = 0x25ce29daf01c16560076e151708db74b

def readparametervalue(device, memtype, cont_unit, func_unit, parameter_id):
    return device.qSPV(memtype, cont_unit, func_unit, parameter_id)[memtype][cont_unit][func_unit][parameter_id]

def main():
    """Connect to a PIPython device."""

    # We recommend to use GCSDevice as context manager with "with".

    with GCSDevice() as pidevice:
        # Choose the interface which is appropriate to your cabling.

        pidevice.ConnectTCPIP(ipaddress='localhost')
        #pidevice.ConnectUSB(serialnum='104237344')
        # pidevice.ConnectRS232(comport=1, baudrate=115200)

        # Each PI controller supports the qIDN() command which returns an
        # identification string with a trailing line feed character which
        # we "strip" away.

        print('connected: {}'.format(pidevice.qIDN().strip()))

        # Show the version info which is helpful for PI support when there
        # are any issues.

        if pidevice.HasqVER():
            print('version info: {}'.format(pidevice.qVER().strip()))

        # read out maximum velocity for AXIS_1 and set velocity to 50% of maximum

        maxvelocity = readparametervalue(pidevice, "RAM", "AXIS_1", "TRAJ_1", "0x105")
        velocity = maxvelocity * 0.5
        pidevice.SPV("RAM", "AXIS_1", "TRAJ_1", "0x104", velocity)
        print('maximum velocity is {0}, set velocity to {1}'.format(maxvelocity, velocity))


if __name__ == '__main__':
    # To see what is going on in the background you can remove the following
    # two hashtags. Then debug messages are shown. This can be helpful if
    # there are any issues.

    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)

    main()
