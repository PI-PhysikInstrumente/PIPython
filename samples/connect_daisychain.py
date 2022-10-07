#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to connect three controllers on a daisy chain."""

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

__signature__ = 0x5e6acd5e3836778bdf6df55864bb5aa

# C-863 controller with device ID 3, this is the master device
# E-861 controller with device ID 7
# C-867 controller with device ID 1

def main():
    """Connect three controllers on a daisy chain."""
    with GCSDevice('C-863.11') as c863:
        c863.OpenRS232DaisyChain(comport=1, baudrate=115200)
        # c863.OpenUSBDaisyChain(description='1234567890')
        # c863.OpenTCPIPDaisyChain(ipaddress='192.168.178.42')
        daisychainid = c863.dcid
        c863.ConnectDaisyChainDevice(3, daisychainid)
        with GCSDevice('E-861') as e861:
            e861.ConnectDaisyChainDevice(7, daisychainid)
            with GCSDevice('C-867') as c867:
                c867.ConnectDaisyChainDevice(1, daisychainid)
                print('\n{}:\n{}'.format(c863.GetInterfaceDescription(), c863.qIDN()))
                print('\n{}:\n{}'.format(e861.GetInterfaceDescription(), e861.qIDN()))
                print('\n{}:\n{}'.format(c867.GetInterfaceDescription(), c867.qIDN()))


if __name__ == '__main__':
    # from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # PILogger.setLevel(DEBUG)
    main()
