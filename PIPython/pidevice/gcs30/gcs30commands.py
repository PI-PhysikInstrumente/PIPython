#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide GCS functions to control a PI device."""
# Trailing newlines pylint: disable=C0305

from time import sleep

from ...PILogger import PIDebug, PIWarning
from ..common.gcsbasecommands import GCSBaseCommands
from .gcs30commands_helpers import PIAxisStatusKeys, PIValueDataTypes, PIBlockKeys, PIBlockNames, PIContainerUnitKeys, \
    get_subdict_form_umfblockcommnaddict
from ..common.gcscommands_helpers import logsysinfo, getsupportedfunctions
from ..gcserror import GCSError, PI_ERROR_AXIS_RUNTIME_ERROR__1117

__signature__ = 0x4bf97eb2deffb9f9dcad2da0da87bf75


# Invalid method name pylint: disable=C0103
# Too many lines in module pylint: disable=C0302
# Too many public methods pylint: disable=R0904
# Too many arguments pylint: disable=R0913
class GCS30Commands(GCSBaseCommands):
    """Provide functions for GCS commands and communicate with PI controller."""

    def __init__(self, msgs):
        """Wrapper for PI GCS DLL.
        @type msgs : pipython.pidevice.gcsmessages.GCSMessages
        """
        PIDebug('create an instance of GCS30Commands(msgs=%s)', str(msgs))
        logsysinfo()
        self._umf_gcs_device_parent = None
        super().__init__(msgs)
        self._init_settings()

    def __str__(self):
        return 'GCS30Commands(msgs=%s)' % str(self._msgs)

    def _init_settings(self):
        self._settings = {'paramconv': {}, 'validucls': [], 'paramconv_ucl': '', 'interpreter': []}

    @property
    def connectionid(self):
        """Get ID of current connection as integer."""
        return super().connectionid

    @property
    def interpreter(self):
        """Get the used system and interpreter."""
        if self._msgs.connected and not self._settings['interpreter']:
            self._settings['interpreter'] = self.qIPR()

        return self._settings['interpreter']

    @property
    def funcs(self):
        """Return list of supported GCS functions."""
        if self._funcs is None:
            self._funcs = getsupportedfunctions(self.ReadGCSCommand('USG? CMD'))
        return self._funcs

    @funcs.deleter
    def funcs(self):
        """Reset list of supported GCS functions."""
        PIDebug('GCS30Commands.funcs: reset')
        super(GCS30Commands, self.__class__).funcs.fdel(self)

    @property
    def logfile(self):
        """Full path to file where to save communication to/from device."""
        return super().logfile

    @logfile.setter
    def logfile(self, filepath):
        """Full path to file where to save communication to/from device."""
        super(GCS30Commands, self.__class__).logfile.fset(self, filepath)

    @property
    def timeout(self):
        """Get current timeout setting in milliseconds."""
        return super().timeout

    @timeout.setter
    def timeout(self, value):
        """Set timeout.
        @param value : Timeout in milliseconds as integer.
        """
        super(GCS30Commands, self.__class__).timeout.fset(self, value)

    @property
    def bufstate(self):
        """False if no buffered data is available. True if buffered data is ready to use.
        Float value 0..1 indicates read progress. To wait, use "while self.bufstate is not True".
        """
        return super().bufstate

    @property
    def bufdata(self):
        """Get buffered data as 2-dimensional list of float values.
        Use "while self.bufstate is not True" and then call self.bufdata to get the data. (see docs)
        """
        return super().bufdata

    @property
    def umf_gcs_device_parent(self):
        """Gets the UMF GCSDevice parent"""
        return self._umf_gcs_device_parent

    @umf_gcs_device_parent.setter
    def umf_gcs_device_parent(self, umf_gcs_device_parent):
        """Set the UMF GCSDevice parent."""
        self._umf_gcs_device_parent = umf_gcs_device_parent

    @property
    def devname(self):
        """Return device name from its IDN string."""
        if self._name is None:
            self._name = self.qIDN().upper().split(',')[1].strip()
            PIDebug('GCS30Commands.devname: set to %r', self._name)

        return self._name

    @devname.setter
    def devname(self, devname):
        """Set device name as string, only for testing."""
        super(GCS30Commands, self.__class__).devname.fset(self, devname)
        PIWarning('controller name is coerced to %r', self._name)

    @devname.deleter
    def devname(self):
        """Reset device name."""
        self._name = None
        super(GCS30Commands, self.__class__).devname.fdel(self)
        PIDebug('GCS30Commands.devname: reset')

    def clearparamconv(self):
        """Clear the stored parameter conversion settings."""
        PIDebug('GCS30Commands.clearparamconv()')
        super().clearparamconv()
        self._settings['paramconv_ucl'] = ''

    def paramconv(self, paramdict):
        """Convert values in 'paramdict' to according type in qUSG('PAM') answer.
        :param paramdict: Dictionary of {'<memtype>':{'<contr_unit> <func_unit>':[{<parameter_id>:<value>}]}}.
        :type paramdict: dict
        :return: Dictionary of {{'<memtype>':{'<contr_unit> <func_unit>':[{<parameter_id>:<value>}]}}.
        :rtype: dict
        """
        self.initparamconv()

        for memtype in paramdict:
            for cont_unit in paramdict[memtype]:
                if not cont_unit in self._settings['paramconv']:
                    continue

                for func_unit in paramdict[memtype][cont_unit]:
                    if not func_unit in self._settings['paramconv'][cont_unit]:
                        continue

                    for param in paramdict[memtype][cont_unit][func_unit]:
                        # Remove comma seperated index
                        param_settings = param.split(',')[0]
                        if not param_settings in self._settings['paramconv'][cont_unit][func_unit]:
                            continue

                        if paramdict[memtype][cont_unit][func_unit][param] != '-':
                            paramdict[memtype][cont_unit][func_unit][param] = \
                                self._settings['paramconv'][cont_unit][func_unit][param_settings](
                                    paramdict[memtype][cont_unit][func_unit][param])

        return paramdict

    def update_paramconv_if_necessary(self):
        """
        updates the the parameter convert dict if the current user level his higher the the user level at the last
        update of the parameter convert dict.
        """
        self.initparamconv()
        self._init_valid_ucls()
        current_ucl = self._msgs.read('UCL?').strip()

        if self._settings['validucls'].index(self._settings['paramconv_ucl']) < \
           self._settings['validucls'].index(current_ucl):
            self.clearparamconv()
            self.initparamconv()

    def _init_valid_ucls(self):
        if 'validucls' not in self._settings.keys() or not self._settings['validucls']:
            self._settings['validucls'] = [ucl[PIBlockKeys.COMMAND_LEVEL_NAME.value] for ucl in
                                           get_subdict_form_umfblockcommnaddict(PIBlockNames.USER_COMMAND_LEVEL.value,
                                                                    self.qUSG('PROP ' + ' '.join(self.interpreter)))]

    def initparamconv(self):
        """
        Initialize paramconv with the 'qUSG('PAM')' answer.
        """
        if not self._settings['paramconv']:
            self.qUSG('PAM')

    def _initparamconvfromblockcmd(self, block_cmd):
        """
        Initialize paramconv witht the parameter informations in a block command.
        :param block_cmd: dicktionary {PI_KEY_PARAMETER_OVERVIEW: [{PI_KEY_UNIT_ADDRESS: '<contr_unit> <func_unit>'},
        {PI_KEY_PARAMETER_ID: <param_id>}, {PI_KEY_DATA_TYPE:'<data_type>'}, ]}
        :type block_cmd: dict
        """
        for block_cmd_line in block_cmd:
            if PIBlockNames.PARAM_OVERVIEW.value in block_cmd_line:
                for line in block_cmd_line[PIBlockNames.PARAM_OVERVIEW.value]:
                    cont_unit = line[PIBlockKeys.CONTAINER_UNIT.value]
                    func_unit = line[PIBlockKeys.FUNCTION_UNIT.value]
                    paramer_id = line[PIBlockKeys.PARAM_ID.value]
                    data_type = line[PIBlockKeys.DATA_TYPE.value]

                    if not cont_unit in self._settings['paramconv']:
                        self._settings['paramconv'][cont_unit] = {}

                    if not func_unit in self._settings['paramconv'][cont_unit]:
                        self._settings['paramconv'][cont_unit][func_unit] = {}

                    if data_type.upper() in (
                            PIValueDataTypes.INT8.value, PIValueDataTypes.UINT8.value,
                            PIValueDataTypes.INT16.value, PIValueDataTypes.UINT16.value,
                            PIValueDataTypes.INT32.value, PIValueDataTypes.UINT32.value,
                            PIValueDataTypes.INT64.value, PIValueDataTypes.UINT64.value):
                        self._settings['paramconv'][cont_unit][func_unit][paramer_id] = self._int
                    elif data_type.upper() in (PIValueDataTypes.FLOAT32.value, PIValueDataTypes.FLOAT64.value):
                        self._settings['paramconv'][cont_unit][func_unit][paramer_id] = self._float
                    elif data_type.upper() in (PIValueDataTypes.STRING32.value,
                                               PIValueDataTypes.VOID.value,
                                               PIValueDataTypes.ENUM.value):
                        continue
                    else:
                        raise KeyError('unknown parameter type %r' % data_type)

    @staticmethod
    def _get_axes_list(axes):
        if not axes:
            axes = []

        if isinstance(axes, (str)):
            axes = axes.split()

        if not isinstance(axes, (list, set, tuple)):
            axes = [axes]

        return axes

    def _get_axes_status(self, axes):
        axes_state = {}
        if not self.HasqSTV():
            return axes_state

        if len(axes) == 1:
            axes_state = self.qSTV(axes)
        elif len(axes) > 1:
            axes_state = self.qSTV()
            axes_state = {axis: axes_state[axis] for axis in axes_state if axis in axes}
        else:
            axes_state = self.qSTV()
            axes_state = {axis: axes_state[axis] for axis in axes_state if PIContainerUnitKeys.AXIS.value in axis}

        return axes_state

    def get_axes_status_flag(self, axes, flag, throwonaxiserror=False):
        """
        Gets the axes status flag 'flag' for all axes in 'axes'
        :param axes: list of axes or empty list for all axes
        :param flag: the axes flag (PIAxisStatusKeys) to return
        :param throwonaxiserror: if true throws error PI_ERROR_AXIS_RUNTIME_ERROR__1117 if
        the flag PIAxisStatusKeys.ERROR ist true
        :return: dict {<axis>:<flag>, }
        """
        axes_state = self._get_axes_status(axes)
        answer = {axis:axes_state[axis][flag] for axis in axes_state}

        if throwonaxiserror and any(axes_state[axis][PIAxisStatusKeys.ERROR.value]for axis in axes_state):
            raise GCSError(PI_ERROR_AXIS_RUNTIME_ERROR__1117)

        return answer

    def bufdata_generator(self, read_block_size=None):
        """
        Generator for the recorded data
        :param read_block_size: The block size to read at each iteration. If None all at recorded data are returned
        :return: List
        """
        # Access to a protected member _databuffer of a client class pylint: disable=W0212
        if read_block_size is None:
            blocksize = self._msgs._databuffer['index']
        else:
            blocksize = read_block_size

        while self._msgs._databuffer['index'] > 0:

            # Lock the access to the databuffer
            while self._msgs._databuffer['lock']:
                sleep(0.05)
            self._msgs._databuffer['lock'] = True

            # The blocksize cannot be larger than the number of values in the array
            if blocksize > self._msgs._databuffer['index']:
                blocksize = self._msgs._databuffer['index']

            yield [x[0:blocksize] for x in self._msgs.bufdata]
            self._msgs._databuffer['data'] = [x[blocksize:] for x in self._msgs.bufdata]
            self._msgs._databuffer['index'] -= blocksize
            self._msgs._databuffer['lastindex'] -= blocksize

            if self._msgs._databuffer['index'] < 0:
                self._msgs._databuffer['index'] = 0

            if self._msgs._databuffer['lastindex'] < 0:
                self._msgs._databuffer['lastindex'] = 0

            self._msgs._databuffer['lock'] = False

    # Unused argument 'noraise' pylint: disable=W0613
    def StopAll(self, noraise=False):
        """Stop all axes abruptly by sending STP".
        Stop all motion caused by move gcs-commands
        @param noraise : unused (only for compatibility reasons).
        """
        PIDebug('GCS30Commands.StopAll')
        self._msgs.send('STP')

    def HasStopAll(self):
        """Return True if STP() is available."""
        return self._has('STP')

    def IsMoving(self, axes=None):
        """Check if 'axes' are moving.
        If an axis is moving the corresponding element will be True, otherwise False.
        @param axes : String convertible or list of them or None.
        @return : Ordered dictionary of {axis: value}, values are bool.
        """
        PIDebug('GCS30Commands.IsMoving(axes=%r)', axes)
        tmp_checkerror = self._msgs.errcheck
        self._msgs.errcheck = False

        axes = self._get_axes_list(axes)
        axis_moving_status = self.get_axes_status_flag(axes, PIAxisStatusKeys.IN_MOTION.value, self._msgs.errcheck)

        self._msgs.errcheck = tmp_checkerror
        return axis_moving_status

    def IsControllerReady(self):
        """Test if controller is ready, corresponds to GCS command "#7". No error check.
        @return : True if controller is ready.
        """
        PIDebug('GCS30Commands.IsControllerReady()')
        tmp_checkerror = self._msgs.errcheck
        self._msgs.errcheck = False

        axis_ipr_status = self.get_axes_status_flag([], PIAxisStatusKeys.INTERNAL_PROCESS_RUNNING.value,
                                                    self._msgs.errcheck)

        self._msgs.errcheck = tmp_checkerror
        return not any(axis_ipr_status.values())

    def qVER(self):
        """Get version information about firmware and modules.
        @return : Version information as string with trailing linefeeds.
        """
        PIDebug('GCS30Commands.qVER()')
        answer = self._msgs.read('VER?')
        PIDebug('GCS30Commands.qVER = %r', answer)
        return answer

    # GCS FUNCTIONS ### DO NOT MODIFY THIS LINE !!! ###############################################

    # CODEGEN BEGIN ### DO NOT MODIFY THIS LINE !!! ###############################################
