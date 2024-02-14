#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide GCS functions to control a PI device."""
# Trailing newlines pylint: disable=C0305

from ...PILogger import PIDebug, PIWarning
# Wildcard import pipython.gcscommands_helpers pylint: disable=W0401
# Unused import platform from wildcard import pylint: disable=W0614
from ..common.gcscommands_helpers import *
from ..common.gcsbasecommands import GCSBaseCommands
from .. import gcserror
from ..gcserror import GCSError
from ...version import __version__

__signature__ = 0x2fd860983d794bd9f34bd6da9da77cf8

GCSFUNCTIONS = {
    'E-816': [
        'qERR', 'qI2C', 'qIDN', 'StopAll', 'BDR', 'qBDR', 'AVG', 'qAVG', 'SCH', 'qSCH', 'qSAI', 'MAC_BEG', 'MAC_START',
        'MAC_NSTART', 'MAC_DEL', 'MAC_DEF', 'MAC_END', 'MAC_qDEF', 'MAC_qFREE', 'qMAC', 'IsRunningMacro', 'DEL', 'WPA',
        'RST', 'qHLP', 'DCO', 'qDCO', 'MOV', 'MVR', 'qMOV', 'SVA', 'SVR', 'qSVA', 'MVT', 'qMVT', 'qDIP', 'qPOS', 'qVOL',
        'qOVF', 'qONT', 'SVO', 'qSVO', 'SWT', 'qSWT', 'WTO', 'SPA', 'qSPA',
    ],
    'HEXAPOD': [
        'qIDN', 'AAP', 'qCST', 'qECO', 'qERR', 'FAA', 'FAM', 'FAS', 'DMOV', 'DRV', 'FIO', 'FSA', 'FSC', 'FSM', 'FSN',
        'GetPosStatus', 'GetScanResult', 'HasPosChanged', 'INI', 'IsMoving', 'IsRecordingMacro', 'IsScanning',
        'MAC_BEG', 'MAC_DEL', 'MAC_END', 'MAC_qERR', 'MAC_START', 'MOV', 'MWG', 'NAV', 'NLM', 'PLM', 'qCST', 'qDRR',
        'qFSN', 'qHLP', 'qMAC', 'qNAV', 'qNLM', 'qPLM', 'qPOS', 'qSAI', 'qSAI_ALL', 'qSCT', 'qSGA', 'qSPA', 'qSPI',
        'qSSL', 'qSST', 'qSVO', 'qTAV', 'qVEL', 'qVER', 'SCT', 'SGA', 'SPI', 'SSL', 'SST', 'STP', 'SVO', 'TAV', 'VEL',
        'VMO',
    ],
    'TRIPOD': [
        'qIDN', 'AAP', 'qCST', 'qECO', 'qERR', 'FAA', 'FAM', 'FAS', 'DMOV', 'DRV', 'FIO', 'FSA', 'FSC', 'FSM', 'FSN',
        'GetPosStatus', 'GetScanResult', 'HasPosChanged', 'INI', 'IsMoving', 'IsRecordingMacro', 'IsScanning',
        'MAC_BEG', 'MAC_DEL', 'MAC_END', 'MAC_qERR', 'MAC_START', 'MOV', 'MWG', 'NAV', 'NLM', 'PLM', 'qCST', 'qDRR',
        'qFSN', 'qHLP', 'qMAC', 'qNAV', 'qNLM', 'qPLM', 'qPOS', 'qSAI', 'qSAI_ALL', 'qSCT', 'qSGA', 'qSPA', 'qSPI',
        'qSSL', 'qSST', 'qSVO', 'qTAV', 'qVEL', 'qVER', 'SCT', 'SGA', 'SPI', 'SSL', 'SST', 'STP', 'SVO', 'TAV', 'VEL',
        'VMO',
    ],
    'C-702.00': [
        'IsMoving', 'HasPosChanged', 'IsControllerReady', 'IsRunningMacro', 'StopAll', 'SystemAbort', 'q*IDN', 'ACC',
        'qACC', 'CCL', 'qCCL', 'CLR', 'CLS', 'CST', 'qCST', 'qCSV', 'CTO', 'qCTO', 'DEL', 'DFF', 'qDFF', 'DFH', 'qDFH',
        'DIO', 'qDIO', 'DRC', 'qDRC', 'qDRR', 'DRT', 'qDRT', 'DSP', 'qDSP', 'qECO', 'qERR', 'GOH', 'qHDR', 'HID',
        'qHID', 'qHLP', 'HLT', 'IFC', 'qIFC', 'IFS', 'qIFS', 'INI', 'ITD', 'qLIM', 'MAC', 'qMAC', 'MNL', 'MOV', 'qMOV',
        'MPL', 'MSG', 'MVR', 'MVS', 'qMVS', 'NLM', 'qNLM', 'qONT', 'PLM', 'qPLM', 'POS', 'qPOS', 'RBT', 'REF', 'qREF',
        'RON', 'qRON', 'RST', 'RTR', 'qRTR', 'SAI', 'qSAI', 'SAV', 'SCA', 'qSCA', 'SMO', 'qSMO', 'SPA', 'qSPA', 'SSL',
        'qSSL', 'qSSN', 'SSP', 'SST', 'qSST', 'qSTA', 'STP', 'SVO', 'qSVO', 'qTAC', 'qTCV', 'qTIM', 'qTIO', 'qTMN',
        'qTMX', 'qTNR', 'TRO', 'qTRO', 'qTSP', 'qTVI', 'VEL', 'qVEL', 'qVER', 'VMO', 'qVST', 'WAA', 'WAI', 'WAV',
        'qWAV', 'WGO', 'qWGO', 'WPA', 'WSL', 'qWSL',
    ]
}


class GCS2Commands(GCSBaseCommands):
    """Provide functions for GCS commands and communicate with PI controller."""

    def __init__(self, msgs):
        """Wrapper for PI GCS DLL.
        @type msgs : pipython.pidevice.gcsmessages.GCSMessages
        """
        PIDebug('create an instance of GCS2Commands(msgs=%s)', str(msgs))
        super().__init__(msgs)

    def __str__(self):
        return 'GCS2Commands(msgs=%s)' % str(self._msgs)

    @property
    def devname(self):
        """Return device name from its IDN string."""
        if self._name is None:
            idn = self.qIDN().upper()
            if 'PI-E816' in idn:
                self._name = 'E-816'
            elif 'DIGITAL PIEZO CONTROLLER' in idn:
                self._name = 'E-710'
            else:
                self._name = idn.split(',')[1].strip()
            PIDebug('GCS2Commands.devname: set to %r', self._name)
        return self._name

    @devname.setter
    def devname(self, devname):
        """Set device name as string, only for testing."""
        super(GCS2Commands, self.__class__).devname.fset(self, devname)
        PIWarning('controller name is coerced to %r', self._name)

    @devname.deleter
    def devname(self):
        """Reset device name."""
        self._name = None
        super(GCS2Commands, self.__class__).devname.fdel(self)
#        super().devname.fdel(self)
        PIDebug('GCS2Commands.devname: reset')

    @property
    def funcs(self):
        """Return list of supported GCS functions."""
        if self._funcs is None:
            if self.devname in GCSFUNCTIONS:
                self._funcs = GCSFUNCTIONS[self.devname]
            else:
                self._funcs = getsupportedfunctions(self.qHLP())
        return self._funcs

    @funcs.deleter
    def funcs(self):
        """Reset list of supported GCS functions."""
        PIDebug('GCS2Commands.funcs: reset')
        super(GCS2Commands, self.__class__).funcs.fdel(self)
#        super().funcs.fdel(self)

    def _initparamconvfromblockcmd(self, block_cmd):
        """Initialize the parameter configuration structure based on
        the parameter information block answer"""

    def paramconv(self, paramdict):
        """Convert values in 'paramdict' to according type in qHPA answer.
        @paramdict: Dictionary of {item: {param: value}}.
        @return: Dictionary of {item: {param: value}}.
        """
        self.initparamconv()

        for item in paramdict:
            for param in paramdict[item]:
                if param in self._settings['paramconv']:
                    paramdict[item][param] = self._settings['paramconv'][param](paramdict[item][param])

        return paramdict

    def update_paramconv_if_necessary(self):
        """
        updates the the parameter convert dict if the current user level his higher the the user level at the last
        update of the parameter convert dict.
        """

    def initparamconv(self):
        """Initialize paramconv .
        """
        if not self._settings['paramconv']:
            for line in self.qHPA().splitlines():
                if '=' not in line:
                    continue
                paramid = int(line.split('=')[0].strip(), base=16)
                convtype = line.split()[3].strip()
                if convtype.upper() == 'INT':
                    self._settings['paramconv'][paramid] = self._int
                elif convtype.upper() == 'FLOAT':
                    self._settings['paramconv'][paramid] = self._float
                elif convtype.upper() in ('CHAR', 'STRING'):
                    continue
                else:
                    raise KeyError('unknown parameter type %r' % convtype)

    def StopAll(self, noraise=False):
        """Stop all axes abruptly by sending "#24".
        Stop all motion caused by move commands (e.g. MOV, MVR, GOH, STE, SVA, SVR), referencing
        commands (e.g. FNL, FPL FRF), macros (e.g. MAC), wave generator output (e.g. WGO) and by
        the autozero procedure (e.g. ATZ) and by the user profile mode (e.g. UP*). Analog input is
        unconnected from the axes. Joystick is disabled.
        May raise GCSError(E10_PI_CNTR_STOP).
        @param noraise : If True a GCS error 10 (controller was stopped by command) will not be raised.
        """
        PIDebug('GCS2Commands.StopAll(noraise=%s)', noraise)
        try:
            self._msgs.send(chr(24))
        except GCSError as exc:
            if noraise and exc == gcserror.E10_PI_CNTR_STOP:
                PIDebug('GCSError 10 is catched and will not raise')
            else:
                raise

    def IsMoving(self, axes=None):
        """Check if 'axes' are moving.
        If an axis is moving the corresponding element will be True, otherwise False.
        @param axes : String convertible or list of them or None.
        @return : Ordered dictionary of {axis: value}, values are bool.
        """
        PIDebug('GCS2Commands.IsMoving(axes=%r)', axes)
        checksize((), axes)
        answer = self._msgs.read(chr(5))
        value = int(answer.strip(), base=16)
        answerdict = getbitcodeditems(value, self.allaxes, axes)
        PIDebug('GCS2Commands.IsMoving = %r', answerdict)
        return answerdict

    def IsControllerReady(self):
        """Test if controller is ready, corresponds to GCS command "#7". No error check.
        @return : True if controller is ready.
        """
        PIDebug('GCS2Commands.IsControllerReady()')
        errcheck = self._msgs.errcheck
        self._msgs.errcheck = False
        answer = self._msgs.read(chr(7))
        self._msgs.errcheck = errcheck
        try:
            if ord(answer.strip()) == 177:
                answer = True
            elif ord(answer.strip()) == 176:
                answer = False
            else:
                raise TypeError
        except TypeError:
            raise ValueError('unexpected response %r for IsControllerReady()' % answer) from TypeError
        PIDebug('GCS2Commands.IsControllerReady = %r', answer)
        return answer

    def qVER(self):
        """Get version information about firmware and modules.
        @return : Version information as string with trailing linefeeds.
        """
        PIDebug('GCSBaseCommands.qVER()')
        answer = self._msgs.read('VER?')
        answer = answer[:-1] + ' \nPIPython: %s\n' % __version__

        PIDebug('GCSBaseCommands.qVER = %r', answer)
        return answer

    # GCS FUNCTIONS ### DO NOT MODIFY THIS LINE !!! ###############################################

    # CODEGEN BEGIN ### DO NOT MODIFY THIS LINE !!! ###############################################


