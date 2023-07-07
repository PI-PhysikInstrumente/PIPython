#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tools for setting up and using the data recorder of a PI device."""

from time import sleep, time
from collections import OrderedDict
from ...PILogger import PIDebug
from .gcs30commands_helpers import (
    PIBlockNames,
    PIBlockKeys,
    PIMemoryTypeKeys,
    PIDataRecorderKeys,
    PIFunctionUnitKeys,
    find_subblock_with_key)
from ..common.gcsbasedatarectools import GCSBaseDatarecorder

__signature__ = 0x53808980c89911387169d95ece3c39d1

# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
# Too many instance attributes pylint: disable=R0902
class GCS30Datarecorder(GCSBaseDatarecorder):
    """Set up and use the data recorder of a GCS30device."""

    def __init__(self, gcs, recorder_id):
        self._verify_recorder_id(recorder_id)
        self._verify_that_all_required_gcs_commands_are_available(gcs)

        self._recorder_id = recorder_id
        self._servotime_in_seconds = None
        self._configurable_triggers = None
        self._configurable_trigger_options = None
        self._record_rate = None
        self._max_number_of_traces = None
        self._max_number_of_values_per_trace = None
        self._number_of_values = None
        self._offset = None
        self._timeout = None
        self._traces = None
        self._trigger = None
        super().__init__(gcs)

    @property
    def servotime(self):
        """Return current servo cycle time.
        :return: Servo cycle time in seconds.
        :rtype: float
        """
        if not self._servotime_in_seconds:
            self._servotime_in_seconds = self._read_servo_cycle_time_parameter() * 0.000001
        return self._servotime_in_seconds

    @property
    def configurable_triggers(self):
        """List of all triggers which can be configured for the connected device
        :return: List of [ { 'Name': '<trigger_name>, 'TriggerOption1': <trigger_option_1>,
                 'TriggerOption2': <trigger_option_2> } ]
        :rtype: list
        """
        if not self._configurable_triggers:
            self._read_configurable_triggers_and_configurable_trigger_options()
        return self._configurable_triggers

    @property
    def configurable_trigger_options(self):
        """List of all trigger options which are used by the configurable triggers
        :return: List of [ { 'Name': '<option_name>, 'Description': <description> } ]
        :rtype: list
        """
        if not self._configurable_trigger_options:
            self._read_configurable_triggers_and_configurable_trigger_options()
        return self._configurable_trigger_options

    @property
    def max_number_of_traces(self):
        """Returns the current maximum number of traces which might be recorded.
        :return: Maximum number of traces
        :rtype: int
        """
        if not self._max_number_of_traces:
            self._max_number_of_traces = self._read_max_number_of_traces_parameter()
        return self._max_number_of_traces

    @property
    def max_number_of_values_per_trace(self):
        """Returns the maximum number of values which might be recorded per trace.
        :return: Maximum number of values per trace
        :rtype: int
        """
        if not self._max_number_of_values_per_trace:
            self._max_number_of_values_per_trace = self._read_max_number_of_values_per_trace()
        return self._max_number_of_values_per_trace

    @property
    def number_of_values(self):
        """Returns the current number of values which should be read per trace.
        :return: Number of values to read
        :rtype: int
        """
        if not self._number_of_values:
            self._number_of_values = self.max_number_of_values_per_trace
        return self._number_of_values

    @number_of_values.setter
    def number_of_values(self, value):
        """Sets the number of values which should be read per trace.
        :param value: New value for the number of values to read.
        :type value: convertible to int
        """
        try:
            int(value)
        except Exception as exception:
            raise TypeError('number_of_values must be convertible to int') from exception
        if value > self.max_number_of_values_per_trace:
            raise ValueError('number_of_values must be < {0}'.format(
                self.max_number_of_values_per_trace))
        self._number_of_values = int(value)
        PIDebug('GCS30Datarecorder.number_of_values: set to %s', str(self._record_rate))

    @number_of_values.deleter
    def number_of_values(self):
        """Resets the number of values which should be read per trace."""
        self._number_of_values = None
        PIDebug('GCS30Datarecorder.number_of_values: reset')

    @property
    def offset(self):
        """Returns the offset for start reading the recorded values.
        :return: Offset for start reading
        :rtype: int
        """
        if not self._offset:
            self._offset = 1
        return self._offset

    @offset.setter
    def offset(self, value):
        """Sets the offset for start reading the recorded values.
        :param value: New offset value for start reading.
        :type value: convertible to int
        """
        try:
            int(value)
        except Exception as exception:
            raise TypeError('offset must be convertible to int') from exception
        if value < 1:
            raise ValueError('offset must be > 1')
        if value > self.max_number_of_values_per_trace:
            raise ValueError('offset must be < {0}'.format(self.max_number_of_values_per_trace))
        self._offset = int(value)
        PIDebug('GCS30Datarecorder.offset: set to %s', str(self._offset))

    @offset.deleter
    def offset(self):
        """Resets the offset for start reading the recorded values."""
        self._offset = None
        PIDebug('GCS30Datarecorder.offset: reset')

    @property
    def timeout(self):
        """Returns the timeout in seconds for reading the recorded values.
        :return: Timeout in seconds
        :rtype: float
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Sets the timeout in seconds for reading the recorded values.
        :param value: New timeout value in seconds
        :type value: convertible to float
        """
        try:
            float(value)
        except Exception as exception:
            raise TypeError('timeout must be convertible to float') from exception
        if not value > 0.0:
            raise ValueError('timeout must be > 0.0')
        self._timeout = float(value)
        PIDebug('GCS30Datarecorder.timeout: set to %s', str(self._timeout))

    @timeout.deleter
    def timeout(self):
        """Resets the timeout in seconds for reading the recorded values."""
        self._timeout = None
        PIDebug('GCS30Datarecorder.timeout: reset')

    @property
    def header(self):
        """Return header from last controller readout."""
        if self._header is None:
            self._getdata()
        return self._header

    @property
    def data(self):
        """Return data from last controller readout."""
        if self._data is None:
            self._getdata()
        return self._data

    @property
    def timescale(self):
        """Return list of values for time scale of recorded data."""
        return [self.record_rate * self.servotime * x for x in range(self.number_of_values)]

    @property
    def record_rate(self):
        """Return record rate in servo cyles of the data recorder. If no value
        has yet been configured, the configured value from the controller is read.
        :return: Record rate in servo cycles
        :rtype: int
        """
        if self._record_rate is None:
            self._record_rate = int(self._gcs.qREC_RATE(self._recorder_id)[self._recorder_id])
        return self._record_rate

    @record_rate.setter
    def record_rate(self, value):
        """Set record rate of the data recorder, not yet configured on controller.
        :param value: New value for record rate
        :type value: convertible to int
        """
        try:
            int(value)
        except Exception as exception:
            raise TypeError('record_rate must be convertible to int') from exception
        if value < 1:
            raise ValueError('record_rate must be >= 1')
        self._record_rate = int(value)
        PIDebug('GCS30Datarecorder.record_rate: set to %s', str(self._record_rate))

    @record_rate.deleter
    def record_rate(self):
        """Reset record rate of the data recorder."""
        self._record_rate = None
        PIDebug('GCS30Datarecorder.record_rate: reset')

    @property
    def traces(self):
        """Return current trace configuration. If no value
        has yet been configured, the configured value from the controller is read.
        :return: Trace configuration as OrderedDict of ( <trace id>,
                 [ <container_unit>, <function_unit>, <parameter_id> ] )
        :rtype: OrderedDict
        """
        if self._traces is None:
            self._traces = self._gcs.qREC_TRACE(self._recorder_id)[self._recorder_id]
        return self._traces

    @traces.setter
    def traces(self, value):
        """Sets the current trace configuration. Configuration is not yet applied
        to the controller
        :param value: New trace configuration
        :type value: OrderedDIct, dict or list
        """
        self._traces = self._normalize_traces(value)
        PIDebug('GCS30Datarecorder.traces: set to %r', self._traces)#

    @traces.deleter
    def traces(self):
        """Resets the current trace configuration."""
        self._traces = None
        PIDebug('GCS30Datarecorder.traces: reset')

    @property
    def trigger(self):
        """Return current trigger configuration as list of size 3. First entry
        is the trigger name, the other values are the trigger options.
        :return: List of size 3 [ <trigger name>, <trigger option 1>, <trigger option 2>]
        :rtype: list
        """
        if self._trigger is None:
            self._trigger = self._gcs.qREC_TRG(self._recorder_id)[self._recorder_id]
        return self._trigger

    @trigger.setter
    def trigger(self, value):
        """Sets the current trigger configuration.
        :param value: New trace configuration
        :type value: list, string
        """
        self._trigger = self._normalize_trigger(value)
        PIDebug('GCS30Datarecorder.trigger: set to %r', self._trigger)

    @trigger.deleter
    def trigger(self):
        """Resets the current trigger configuration."""
        self._trigger = None
        PIDebug('GCS30Datarecorder.trigger: reset')

    def arm(self):
        """Configures the data recored based on the properties record_rate,
        traces and trigger. Finally the data recorder is set to state WAIT, so
        that it is ready for recording.
        """
        if not self._can_be_configured():
            self._enable_configuration()
        self._clear_data()
        self._configure_record_rate()
        self._configure_traces()
        self._configure_trigger()
        self._enable_recording()

    def _getdata(self):
        """Wait for end of data recording, start reading out the data and return the data.
        :return : Tuple of (header, data), see qREC_DAT command.
        :rtype: tuple
        """
        self._wait()
        self._header, self._data = self._read()
        return self._header, self._data

    def _wait(self):
        """Wait for end of data recording.
        """
        start_time = time()
        while self._gcs.qREC_NUM(self._recorder_id)[self._recorder_id] < self.number_of_values:
            if self.timeout and (time() - start_time) > self.timeout:
                raise SystemError(
                    'timeout after %.1f secs while waiting on data recorder' % self.timeout)
            sleep(0.005)

    def _read(self, verbose=True):
        """Read out the data and return it.
        :param verbose : If True print a line that shows how many values have been read out already.
        :type value: bool
        :return : Tuple of (header, data), see qREC_DAT command.
        :rtype: tuple
        """
        header = self._gcs.qREC_DAT(
            self._recorder_id,
            'ASCII',
            None,
            self.offset,
            self.number_of_values)
        while self._gcs.bufstate is not True:
            if verbose:
                print(('\rread data {:.1f}%...'.format(self._gcs.bufstate * 100)), end='')
            sleep(0.05)
        if verbose:
            print(('\r%s\r' % (' ' * 20)), end='')
        data = self._gcs.bufdata
        return header, data

    def _can_be_configured(self):
        return self._gcs.qREC_STATE(self._recorder_id)[self._recorder_id] == \
            PIDataRecorderKeys.STATE_CFG.value

    def _enable_configuration(self):
        self._gcs.REC_STOP(self._recorder_id)

    def _clear_data(self):
        self._header = None
        self._data = None

    def _configure_record_rate(self):
        self._gcs.REC_RATE(self._recorder_id, self.record_rate)

    def _configure_traces(self):
        for trace_id in self.traces:
            parameter_id = self.traces[trace_id]
            self._gcs.REC_TRACE(
                self._recorder_id,
                trace_id,
                parameter_id[0],
                parameter_id[1],
                parameter_id[2])

    def _configure_trigger(self):
        self._gcs.REC_TRG(self._recorder_id, self.trigger[0], self.trigger[1:])

    def _enable_recording(self):
        self._gcs.REC_START(self._recorder_id)

    def _read_parameter(self, memory_type, container_unit, function_unit, parameter_id):
        response = self._gcs.qSPV(memory_type, container_unit, function_unit, parameter_id)
        return response[memory_type][container_unit][function_unit][parameter_id]

    @classmethod
    def _verify_recorder_id(cls, recorder_id):
        if not isinstance(recorder_id, str):
            raise TypeError('Recorder ID must be an string!')
        if not recorder_id.upper().startswith(PIFunctionUnitKeys.DATA_RECORDER.value + '_'):
            raise ValueError('Recorder ID must start with prefix "REC_"!')

    # '_verify_that_all_required_gcs_commands_are_available' is too complex. The McCabe rating is 12 pylint: disable=R1260
    @classmethod
    def _verify_that_all_required_gcs_commands_are_available(cls, gcs30commands):
        if not gcs30commands.HasqUSG():
            raise SystemError('PI device which supports USG? is required!')
        if not gcs30commands.HasqSPV():
            raise SystemError('PI device which supports SPV? is required!')
        if not gcs30commands.HasqREC_NUM():
            raise SystemError('PI device which supports REC? NUM is required!')
        if not gcs30commands.HasqREC_RATE():
            raise SystemError('PI device which supports REC? RATE is required!')
        if not gcs30commands.HasqREC_STATE():
            raise SystemError('PI device which supports REC? STATE is required!')
        if not gcs30commands.HasqREC_DAT():
            raise SystemError('PI device which supports REC? DAT is required!')
        if not gcs30commands.HasREC_START():
            raise SystemError('PI device which supports REC START is required!')
        if not gcs30commands.HasREC_STOP():
            raise SystemError('PI device which supports REC STOP is required!')
        if not gcs30commands.HasREC_RATE():
            raise SystemError('PI device which supports REC RATE is required!')
        if not gcs30commands.HasREC_TRACE():
            raise SystemError('PI device which supports REC TRACE is required!')
        if not gcs30commands.HasREC_TRG():
            raise SystemError('PI device which supports REC TRG is required!')

    def _read_configurable_triggers_and_configurable_trigger_options(self):
        response = self._gcs.qUSG('PROP ' + self._recorder_id)
        self._parse_qusg_prop_rec_trg_response(response)

    def _parse_qusg_prop_rec_trg_response(self, usg_prop_rec_id_response):
        try:
            unit_properties_dict = \
                usg_prop_rec_id_response[0][PIBlockNames.UNIT_PROPERTIES.value][0]
            recorder_trigger_subblock = find_subblock_with_key(
                unit_properties_dict, PIBlockKeys.RECORDER_TRIGGER.value)
            trigger_option_subblock = find_subblock_with_key(
                unit_properties_dict,
                PIBlockKeys.TRIGGER_OPTION_TYPES.value)
            self._configurable_triggers = \
                recorder_trigger_subblock[PIBlockKeys.RECORDER_TRIGGER.value]
            self._configurable_trigger_options = \
                trigger_option_subblock[PIBlockKeys.TRIGGER_OPTION_TYPES.value]
        except Exception as exception:
            raise ValueError('Unexpected format of response on "USG? PROP <Container Unit>"') from exception

    def _read_max_number_of_traces_parameter(self):
        return int(self._read_parameter(
            PIMemoryTypeKeys.RAM.value,
            self._recorder_id,
            PIFunctionUnitKeys.ONLY.value,
            "0x104"))

    def _read_servo_cycle_time_parameter(self):
        return int(self._read_parameter(
            PIMemoryTypeKeys.RAM.value,
            "SYS_1",
            PIFunctionUnitKeys.ONLY.value,
            "0x107"))

    def _read_max_number_of_values_per_trace(self):
        return int(self._read_parameter(
            PIMemoryTypeKeys.RAM.value,
            self._recorder_id,
            PIFunctionUnitKeys.ONLY.value,
            "0x103"))

    def _normalize_traces(self, value):
        if isinstance(value, (OrderedDict, dict)):
            return self._normalize_dictionary_of_traces(value)
        if isinstance(value, list):
            return self._normalize_list_of_traces(value)
        raise TypeError('Requires OrderedDict, dict or list as argument type')

    def _normalize_dictionary_of_traces(self, dictionary):
        self._check_number_of_traces(dictionary)
        self._check_all_trace_ids(dictionary.keys())
        self._check_all_parameter_addresses(dictionary.values())
        return self._normalize_traces_dictionary(dictionary)

    def _normalize_traces_dictionary(self, original_dictionary):
        normalized_dict = OrderedDict()
        for trace_id in range(1, self.max_number_of_traces + 1):
            if trace_id in original_dictionary:
                normalized_dict[trace_id] = [
                    original_dictionary[trace_id][0],
                    original_dictionary[trace_id][1],
                    original_dictionary[trace_id][2]]
            else:
                normalized_dict[trace_id] = [
                    PIFunctionUnitKeys.ONLY.value,
                    PIFunctionUnitKeys.ONLY.value,
                    PIFunctionUnitKeys.ONLY.value]
        return normalized_dict

    def _normalize_list_of_traces(self, trace_list):
        self._check_number_of_traces(trace_list)
        self._check_all_parameter_addresses(trace_list)
        return self._normalize_traces_list(trace_list)

    def _normalize_traces_list(self, trace_list):
        normalized_dict = OrderedDict()
        for trace_id in range(1, self.max_number_of_traces + 1):
            if trace_id <= len(trace_list):
                normalized_dict[trace_id] = [
                    trace_list[trace_id - 1][0],
                    trace_list[trace_id - 1][1],
                    trace_list[trace_id - 1][2]]
            else:
                normalized_dict[trace_id] = [
                    PIFunctionUnitKeys.ONLY.value,
                    PIFunctionUnitKeys.ONLY.value,
                    PIFunctionUnitKeys.ONLY.value]
        return normalized_dict

    def _check_number_of_traces(self, collection):
        if len(collection) > self.max_number_of_traces:
            raise ValueError(
                'Number of traces ({0}) is to high. Maximum number of traces is {1}!'.format(
                    len(collection), self.max_number_of_traces))

    def _check_all_trace_ids(self, trace_ids):
        for entry in trace_ids:
            if entry < 1:
                raise ValueError('Invalid trace ID: {0}. Must be >= 1!'.format(entry))
            if entry > self.max_number_of_traces:
                raise ValueError(
                    'Invalid trace ID: {0}. Must be <= {1}!'.format(
                        entry, self.max_number_of_traces))

    def _check_all_parameter_addresses(self, parameter_addresses):
        for entry in parameter_addresses:
            self._check_single_parameter_address(entry)

    @classmethod
    def _check_single_parameter_address(cls, parameter_address):
        if not isinstance(parameter_address, (tuple, list)):
            raise TypeError('Parameter address must be a list or a tuple!')
        if len(parameter_address) != 3:
            raise ValueError(
                'Invalid parameter address {0}. Must contain 3 elements!'.format(
                    parameter_address))
        for entry in parameter_address:
            if not isinstance(entry, str):
                raise ValueError(
                    'Invalid parameter address {0}. Each entry must be a string!'.format(
                        parameter_address))

    def _normalize_trigger(self, value):
        if isinstance(value, (list, tuple)):
            return self._normalize_trigger_list_or_tuple(value)
        if isinstance(value, str):
            return self._normalize_trigger_list_or_tuple(value.split())
        raise TypeError('Requires List, tuple or string as argument type')

    @classmethod
    def _normalize_trigger_list_or_tuple(cls, trigger_configuration):
        if len(trigger_configuration) != 3:
            raise ValueError(
                'Invalid number of entries in trigger configuration ({0}). '
                'Must contain 3 elements!!'.format(
                    len(trigger_configuration)))
        for entry in trigger_configuration:
            if not isinstance(entry, str):
                raise ValueError(
                    'Invalid trigger configuration {0}. '
                    'Each entry must be a string!'.format(
                        trigger_configuration))
        return [trigger_configuration[0], trigger_configuration[1], trigger_configuration[2]]
