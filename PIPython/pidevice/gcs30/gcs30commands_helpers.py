# !/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide GCS functions to control a PI device."""

# Trailing newlines pylint: disable=C0305

from enum import Enum
import re
import copy
from functools import reduce

from .. import gcserror
from ..gcserror import GCSError
from ..common.gcscommands_helpers import GCS2DEVICES, GCS1DEVICES

__signature__ = 0x62492f1c17c16bb21447780561d90467

PI_KEY_CURRENT_VALUE_TIME_STAMP = 'CUR_VAL_READ_TIME'
PI_KEY_CURRENT_VALUE = 'CUR_VAL'
PI_KEY_NEW_VALUE = 'NEW_VAL'
PI_KEY_USER_COMMAND_LEVEL = 'User Command Level'


class PIBlockNames(Enum):
    """
    Enumeration with PI block commands key words for block names
    """
    PARAM_OVERVIEW = 'Parameter Overview'
    CONTENTS_OVERVIEW = 'Contents Overview'
    COMMAND_OVERVIEW = 'Command Overview'
    RELATED_UNITS = "Related Units"
    RELATED_CONFIGURATION_TYPES = 'Related Configuration Types'
    RELATED_MEMORY_TYPES = 'Related Memory Types'
    USER_COMMAND_LEVEL = 'User Command Level'
    UNIT_PROPERTIES = 'Unit Properties'


class PIBlockKeys(Enum):
    """
    Enumeration with PI block commands key words for properties
    """
    CONTAINER_UNITS = 'Container Unit Contents'
    CONTAINER_UNIT = 'Container Unit'
    FUNCTION_UNITS = 'Function Unit Contents'
    FUNCTION_UNIT = 'Function Unit'
    DESCRIPTION = 'Description'
    UNIT_DESCRIPTION = 'Unit Description'
    UNIT_ADDRESS = 'Unit Address'
    SUB_MODULE = 'SUB'
    PARAM_DESCRIPTION = 'Parameter Description'
    PARAM_ID = 'Parameter ID'
    DATA_TYPE = 'Data Type'
    READ_ACCESS_LEVEL = 'READ-UCL'
    WRITE_ACCESS_LEVEL = 'WRITE-UCL'
    MIN_VALUE = 'MINVALUE'
    MAX_VALUE = 'MAXVALUE'
    DIMENSION = 'Dimension'
    PARAMETER_TYPE = 'Parameter Type'
    COMMNAND_LEVEL_NAME = 'Command Level Name'
    RECORDER_FORMAT = 'Recorder Format'
    RECORDER_TRIGGER = 'Recorder Trigger'
    RECORDER_TRACE_INFO = 'Recorder Trace Information'
    RECORDABLE_TYPE_OVERVIEW = 'Recordable DataType Overview'
    RECORDER_HEADER_FORMAT = 'Recorder Header Format'
    RECORDER_TRIGGER_RECURRING = 'Recorder Trigger Recurring'
    RECORDER_STATE = 'Recorder State'
    ALIAS = 'Alias'
    OPTIONS = 'Options'
    OPTION1 = 'Option1'
    OPTION2 = 'Option2'
    MAX_TRACES = 'Max Traces'
    MAX_NUMBER_OF_POINTS_PER_TRACE = 'NumPoints pro Trace'
    VALUE = 'Value'
    SECTION = 'Section'
    TYPE = 'Type'
    COMMAND = 'Command'
    ARGUMENTS = 'Arguments'
    COMMAND_LEVEL_NAME = 'Name'
    TRIGGER_OPTION_TYPES = 'Trigger Option Types'


class PIContainerUnitKeys(Enum):
    """
    Enumeration with PI ContainerUnit key words
    """
    AXIS = 'AXIS'
    IN = 'IN'
    OUT = 'OUT'
    SYS = 'SYS'


class PIFunctionUnitKeys(Enum):
    """
    Enumeration with PI FunctionUnit key words
    """
    ONLY = '-'
    PID = 'PID'
    TRAJECTORY = 'TRAJ'
    ERR = 'ERR'
    SYNC = 'SYNC'
    GCS_INTERPRETER = 'GCS'
    SIMULATION = 'SIM'
    DATA_RECORDER = 'REC'


class PIUserGuideSectionKeys(Enum):
    """
    Enumeration with PI UserGuide section key words
    """
    CMD = 'CMD'
    SYS = 'SYS'
    PAM = 'PAM'
    HW = 'HW'


class PIMemoryTypeKeys(Enum):
    """
    Enumeration with PI memory types key words
    """
    TMP = 'TMP'
    RAM = 'RAM'
    FLASH = 'FLASH'


class PIValueDataTypes(Enum):
    """
    Enumeration of PI data type key words
    """
    INT8 = 'INT8'
    UINT8 = 'UINT8'
    INT16 = 'INT16'
    UINT16 = 'UINT16'
    INT32 = 'INT32'
    UINT32 = 'UINT32'
    INT64 = 'INT64'
    UINT64 = 'UINT64'
    FLOAT32 = 'FLOAT32'
    FLOAT64 = 'FLOAT64'
    STRING32 = 'STRING32'
    VOID = 'VOID'
    ENUM = 'ENUM'

class PIParameterKeys(Enum):
    """
    Enumeration with PI FunctionUnit key words
    """
    CONFIG = 'Configuration'
    OUTPUT = 'Unit Output'
    INPUT = 'Unit Input'
    INPUT_OUTPUT = 'Unit Input-Output'


class PIDataRecorderKeys(Enum):
    """
    Enumeration with DataRecorder key words
    """
    RECURRING = '<Recurring>'
    AXISID = '<AxisID>'
    STATE_CFG = 'CFG'
    STATE_WAITING = 'WAIT'
    STATE_RUNNING = 'RUN'


class PIAxisStatusKeys(Enum):
    """
    Enumeration with AXIS status bit key
    """
    ERROR = 'Error'
    AXIS_ENABLE = 'EAX?'
    DSM_READY_TO_SWITCH_ON = 'DSM: Ready to switch on'
    DSM_FAULT = 'DSM: Fault'
    DSM_OPERATION_ENABLED = 'DSM: Operation enabled'
    DSM_FAULT_REACTION_ACTIVE = 'DSM: Fault reaction active'
    DSM_QUICK_STOP_ACTIVE = 'DSM: Quick stop active'
    DSM = 'DSM'
    MOP_OPEN = 'MOP Open'
    MOP_OPEN_LOOP_POSITION = 'MOP: Open loop position'
    MOP_CLOSED_LOOP_POSITION = 'MOP: Closed loop position'
    MOP_OPEN_LOOP_VELOCITY = 'MOP: Open loop velocity'
    MOP_CLOSED_LOOP_VELOCITY = 'MOP: Closed loop velocity'
    MOP_OPEN_LOOP_FORCE = 'MOP: Open loop force'
    MOP_CLOSED_LOOP_FORCE = 'MOP: Closed loop force'
    MOP_STEP_OPERATION = 'MOP: Step operation'
    MOP = 'MOP'
    REFERENCE_STATE = 'FRF?'
    ON_TARGET = 'ONT?'
    OPEN_CLOSED_LOOP = 'OL/CL'
    INTERNAL_PROCESS_RUNNING = 'IPR'
    POSITIVE_LIMIT_ACTIVE = 'Plim'
    NEGATIVE_LIMIT_ACTIVE = 'Nlim'
    IN_MOTION = 'In Motion'
    STATUS_WORD = 'Status word'

class PIAxisStatusMopValues(Enum):
    """
    Enumeration with AXIS status ModeOfOperations (MOP) values
    """
    MOP_OPEN = 0x00000000
    MOP_OPEN_LOOP_POSITION = 0x00000001
    MOP_CLOSED_LOOP_POSITION = 0x00000002
    MOP_OPEN_LOOP_VELOCITY = 0x00000003
    MOP_CLOSED_LOOP_VELOCITY = 0x00000004
    MOP_OPEN_LOOP_FORCE = 0x00000005
    MOP_CLOSED_LOOP_FORCE = 0x00000006
    MOP_STEP_OPERATION = 0x00000007
    MOP_OFFSET = 8

class PIAxisStatusDsmValues(Enum):
    """
    Enumeration with DSM (DriveStasteMachien) values
    """
    DSM_READY_TO_SWITCH_ON = 0x00000000
    DSM_FAULT = 0x00000001
    DSM_OPERATION_ENABLED = 0x00000002
    DSM_FAULT_REACTION_ACTIVE = 0x00000003
    DSM_QUICK_STOP_ACTIVE = 0x00000006
    DSM_OFFSET = 0


class PISystemStatusKeys(Enum):
    """
    Enumeration with System status bit key
    """
    COMMAND_ERROR = 'Command error'
    CRITICAL_ERROR = 'Critical error'
    INFORMATION = 'Information'
    WARNING = 'Warning'
    STATUS_WORD = 'Status word'


PI_POSSIBLE_MEM_TYPES = [PIMemoryTypeKeys.TMP.value, PIMemoryTypeKeys.RAM.value, PIMemoryTypeKeys.FLASH.value]


class PIParameterFileKeys(Enum):
    """
    Enumeration of PI parameter file key words
    """
    PI_PARAFILE_KEY_CONTAINERUNITS = 'ContainerUnits'
    PI_PARAFILE_KEY_FUNCTIONUNITS = 'FunctionUnits'
    PI_PARAFILE_KEY_PARAMETERS = 'Parameters'
    PI_PARAFILE_KEY_ID = 'Id'
    PI_PARAFILE_KEY_DESCRIPTION = 'Description'
    PI_PARAFILE_KEY_VALUE = 'Value'
    PI_PARAFILE_KEY_VALUES = 'Values'


class PIControlModes(Enum):
    """
    Enumeration of PI Control Modes
    """
    OPEN = 0x0
    OPEN_LOOP_POSITION = 0x1
    CLOSED_LOOP_POSITION = 0x2
    OPEN_LOOP_VELOCITY = 0x3
    CLOSED_LOOP_VELOCITY = 0x4
    OPEN_LOOP_FORCE = 0x5
    CLOSED_LOOP_FORCE = 0x6
    STEP_OPERATION = 0x7

    OPEN_LOOP = [
        OPEN_LOOP_POSITION,
        OPEN_LOOP_VELOCITY,
        OPEN_LOOP_FORCE,
        STEP_OPERATION]

    CLOSED_LOOP = [
        CLOSED_LOOP_POSITION,
        CLOSED_LOOP_VELOCITY,
        CLOSED_LOOP_FORCE]


# PI_BlocCommandsLineStatus_XXX
PI_BCLS_NO_STATUS = 'NO_STATUS'
PI_BCLS_NEW_MAIN_BLOCK = 'NEW_MAIN_BLOCK'
PI_BCLS_IN_MAIN_BLOCK = 'IN_MAIN_BLOCK'
PI_BCLS_END_MAIN_BLOCK = 'END_MAIN_BLOCK'
PI_BCLS_END_SUB_BLOCK = 'END_SUB_BLOCK'
PI_BCLS_IN_SUB_BLOCK = 'IN_SUB_BLOCK'


def isgcs30(gcsmessages):
    """
    Checks if the connected controller is a GCS30 controller
    @param gcsmessages : pipython.pidevice.gcsmessages.GCSMessages
    @return: 'True' if the connected controller is a GCS30 controller, else 'False'
    """
    is_gcs30 = None

    try:
        is_gcs30 = isgcs30_by_qcsv(gcsmessages)
    except GCSError:
        pass

    if is_gcs30 is None:
        try:
            is_gcs30 = isgcs30_by_qidn(gcsmessages)
        except GCSError:
            pass

    return is_gcs30 is True


def isgcs30_by_qcsv(gcsmessages):
    """
    Checks if the connected controller is a GCS30 controller using the 'CSV?' command
    @param gcsmessages : pipython.pidevice.gcsmessages.GCSMessages
    @return: 'True' if the connected controller is a GCS30 controller, else 'False'
    """
    csv = gcsmessages.read('CSV?')
    if float(csv) <= 2.0:
        return False
    return True


def isgcs30_by_qidn(gcsmessages):
    """
    Checks if the connected controller is a GCS30 controller using the controller name and firmware version number
    from the received from the '*IDN?' command
    @param gcsmessages : pipython.pidevice.gcsmessages.GCSMessages
    @return: 'True' if the connected controller is a GCS30 controller, else 'False'
    """

    idn_split = gcsmessages.read('*IDN?').split(',')

    #
    # Check if the controller is a GCS1 controller. If so it is definitely no GCS30 controller.
    #
    # Check if the answer of '*IDN?' has at least two comma separated sections. This is required because the
    # device name is in the second section.
    if len(idn_split) < 2:
        raise GCSError(gcserror.E_1004_PI_UNEXPECTED_RESPONSE)

    if idn_split[1].strip() in GCS1DEVICES:
        return False

    if idn_split[1].split('.')[0].strip() in GCS2DEVICES:
        return False

    #
    # Starting with GCS30 the firmware of the controllers have a four digits version numbers
    # (GCS2 controllers have two or three digits version numbers). The version number is placed at the fourth
    # comma separated section of the '*IDN?' answer.
    #
    # Check if the answer of '*IDN?' has at least four comma separated sections. This is required because the
    # version nummber is in the fourth section.
    if len(idn_split) < 4:
        raise GCSError(gcserror.E_1004_PI_UNEXPECTED_RESPONSE)

    # Check if the version numger has four digits.
    if len(idn_split[3].split('.')) < 4:
        return False

    return True

def get_status_dict_for_containerunits(contaiuer_units_status):
    """
    Converts the staus word '<status_word>' of a container unit into a dict {<status_bit>: <value_as_boolean>, }.
    If the container unit is unknown, the status word '<status_word>' is returned without parsing.
    :param contaiuer_units: {<containter_unit>: <status_word>, }
    :type contaiuer_units_status: dict
    :return: {<containter_unit>: {<status_bit>: <value_as_boolean>, }, }
    :rtype: dict
    """
    for contunit in contaiuer_units_status:
        if PIContainerUnitKeys.AXIS.value in contunit:
            contaiuer_units_status[contunit] = get_axis_status_dict(contaiuer_units_status[contunit])
        if PIContainerUnitKeys.SYS.value in contunit:
            contaiuer_units_status[contunit] = get_system_status_dict(contaiuer_units_status[contunit])
    return contaiuer_units_status

def get_axis_drive_state_machine_flags(status_word):
    """
    Returns a dict with PIAxisStatusKeys values
    :param status_word: the status word returned by qSTV()
    :return: dict with the DSM PIAxisStatusKeys values
    """
    return {
        PIAxisStatusKeys.DSM_READY_TO_SWITCH_ON.value:
            bool(((status_word >> PIAxisStatusDsmValues.DSM_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusDsmValues.DSM_READY_TO_SWITCH_ON.value),
        PIAxisStatusKeys.DSM_FAULT.value:
            bool(((status_word >> PIAxisStatusDsmValues.DSM_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusDsmValues.DSM_FAULT.value),
        PIAxisStatusKeys.DSM_OPERATION_ENABLED.value:
            bool(((status_word >> PIAxisStatusDsmValues.DSM_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusDsmValues.DSM_OPERATION_ENABLED.value),
        PIAxisStatusKeys.DSM_FAULT_REACTION_ACTIVE.value:
            bool(((status_word >> PIAxisStatusDsmValues.DSM_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusDsmValues.DSM_FAULT_REACTION_ACTIVE.value),
        PIAxisStatusKeys.DSM_QUICK_STOP_ACTIVE.value:
            bool(((status_word >> PIAxisStatusDsmValues.DSM_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusDsmValues.DSM_QUICK_STOP_ACTIVE.value),
        PIAxisStatusKeys.DSM.value: status_word & 0x000000FF
    }

def get_axis_mode_of_operations_flags(status_word):
    """
    Returns a dict with PIAxisStatusKeys values
    :param status_word: the status word returnde by qSTV()
    :return: dict with the MOP PIAxisStatusKeys values
    """
    return {
        PIAxisStatusKeys.MOP_OPEN.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_OPEN.value),
        PIAxisStatusKeys.MOP_OPEN_LOOP_POSITION.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_OPEN_LOOP_POSITION.value),
        PIAxisStatusKeys.MOP_CLOSED_LOOP_POSITION.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_CLOSED_LOOP_POSITION.value),
        PIAxisStatusKeys.MOP_OPEN_LOOP_VELOCITY.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_OPEN_LOOP_VELOCITY.value),
        PIAxisStatusKeys.MOP_CLOSED_LOOP_VELOCITY.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_CLOSED_LOOP_VELOCITY.value),
        PIAxisStatusKeys.MOP_OPEN_LOOP_FORCE.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_OPEN_LOOP_FORCE.value),
        PIAxisStatusKeys.MOP_CLOSED_LOOP_FORCE.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_CLOSED_LOOP_FORCE.value),
        PIAxisStatusKeys.MOP_STEP_OPERATION.value:
            bool(((status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF) ==
                 PIAxisStatusMopValues.MOP_STEP_OPERATION.value),
        PIAxisStatusKeys.MOP.value:
            (status_word >> PIAxisStatusMopValues.MOP_OFFSET.value) & 0x000000FF
    }

def get_axis_status_dict(status_word):
    """
    Returns a dict with PIAxisStatusKeys values
    :param status_word: the status word returnde by qSTV()
    :return: dict with PIAxisStatusKeys values
    """
    axis_status_dict = {}

    axis_status_dict[PIAxisStatusKeys.ERROR.value] = \
        bool(status_word & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.AXIS_ENABLE.value] = \
        bool((status_word >> 1) & 0x00000001)

    axis_status_dict.update(get_axis_drive_state_machine_flags(status_word))
    axis_status_dict.update(get_axis_mode_of_operations_flags(status_word))

    axis_status_dict[PIAxisStatusKeys.OPEN_CLOSED_LOOP.value] = \
        bool((status_word >> 16) & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.ON_TARGET.value] = \
        bool((status_word >> 17) & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.IN_MOTION.value] = \
        bool((status_word >> 18) & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.REFERENCE_STATE.value] = \
        bool((status_word >> 19) & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.INTERNAL_PROCESS_RUNNING.value] = \
        bool((status_word >> 20) & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.POSITIVE_LIMIT_ACTIVE.value] = \
        bool((status_word >> 21) & 0x00000001)
    axis_status_dict[PIAxisStatusKeys.NEGATIVE_LIMIT_ACTIVE.value] = \
        bool((status_word >> 22) & 0x00000001)

    axis_status_dict[PIAxisStatusKeys.STATUS_WORD.value] = status_word

    return axis_status_dict

def get_system_status_dict(status_word):
    """
    Returns a dict with PISystemStatusKeys values
    :param status_word: the status word returnde by qSTV()
    :return: dict with PISystemStatusKeys values
    """
    system_status_dict = {}

    system_status_dict[PISystemStatusKeys.COMMAND_ERROR.value] = bool(status_word & 0x00000001)
    system_status_dict[PISystemStatusKeys.CRITICAL_ERROR.value] = bool((status_word >> 1) & 0x00000001)
    system_status_dict[PISystemStatusKeys.INFORMATION.value] = bool((status_word >> 2) & 0x00000001)
    system_status_dict[PISystemStatusKeys.WARNING.value] = bool((status_word >> 3) & 0x00000001)
    system_status_dict[PISystemStatusKeys.STATUS_WORD.value] = status_word

    return system_status_dict

def getlinesstatusofblockanswer(lines):
    """
    Parse the lines and estimates the status of each lien which is required to parse the command
    @param lines : List of lines of a block command answer
    @return: List of [[<Lien>, <line status>], ...]
    """
    block_counter = 0
    lines_and_status = []
    status = PI_BCLS_NO_STATUS
    for line in lines:
        if re.compile('^#END').search(line) or re.compile('^#end').search(line):
            if block_counter > 0:
                block_counter = block_counter - 1

            if block_counter == 0:
                status = PI_BCLS_END_MAIN_BLOCK
            elif block_counter == 1:
                status = PI_BCLS_END_SUB_BLOCK
            else:
                status = PI_BCLS_IN_SUB_BLOCK

        elif re.compile('^#').search(line):

            if block_counter == 0:
                status = PI_BCLS_NEW_MAIN_BLOCK
            elif block_counter == 1:
                status = PI_BCLS_IN_SUB_BLOCK

            block_counter = block_counter + 1
        else:
            if block_counter == 1:
                status = PI_BCLS_IN_MAIN_BLOCK

        lines_and_status.append([line, status])

    return lines_and_status


# 'parseblockanswertodict' is too complex. The McCabe rating is 12 pylint: disable=R1260
def parseblockanswertodict(blockanswer):
    """
    Parse the lines of a GCS blockanswer into lists and dictionaries
    @param blockanswer : String with the answer or a list with lines of a block command answer
    @return: Dict with the parsed lines of a bolck command answer
    """
    if isinstance(blockanswer, str):
        lines = blockanswer.split('\n')[0:-1]
    elif isinstance(blockanswer, list):
        lines = blockanswer
    else:
        lines = []

    lines = [x.lstrip('\t') for x in lines]
    lines = [x.strip() for x in lines]
    lines_and_status = getlinesstatusofblockanswer(lines)

    answer_list = []
    answer_sub_lines = []
    answer_lines = []
    line_dict = {}
#    line_dict = OrderedDict()
    block_headers = []
    block_description = ''
    sub_block_counter = 0

    for line_and_status in lines_and_status:
        if line_and_status[1] == PI_BCLS_NEW_MAIN_BLOCK:
            block_description = line_and_status[0].split(':')[0].replace('#', '')
            block_headers = \
                [h.strip().replace('>', '').replace('<', '') for h in line_and_status[0].split(':')[1].split('\t')]

            block_headers = [x for x in block_headers if x]

        elif line_and_status[1] == PI_BCLS_IN_MAIN_BLOCK:
            sub_block_counter = 0
            line_dict.clear()
            line_cols = line_and_status[0].split('\t')
            if len(block_headers) != len(line_cols):
                raise GCSError(gcserror.E_1004_PI_UNEXPECTED_RESPONSE, 'parseblockanswertodict: The number of cols does'
                                                                       ' not match between the block headers '
                               + str(block_headers) + ', and line ' + str(line_cols))

            for block_header, line_col in zip(block_headers, line_cols):
                line_dict[block_header] = line_col

            if line_dict:
                answer_lines.append(copy.copy(line_dict))

        elif line_and_status[1] == PI_BCLS_IN_SUB_BLOCK:
            answer_sub_lines.append(line_and_status[0])

        elif line_and_status[1] == PI_BCLS_END_SUB_BLOCK:
            sub_block_counter = sub_block_counter + 1
            answer_sub_lines.append(line_and_status[0])
            answer_lines[-1]['SUB_' + str(sub_block_counter)] = parseblockanswertodict(answer_sub_lines)
            del answer_sub_lines[:]

        elif line_and_status[1] == PI_BCLS_END_MAIN_BLOCK:
            block_dict = {}
#            block_dict = OrderedDict()
            block_dict[block_description] = copy.copy(answer_lines)
            answer_list.append(block_dict)
            del answer_lines[:]

    return answer_list


def getqspvparameterstringofdictionarry(param_dict):
    """
    Parse a dictionary to a sting in the format which is required by the 'SPV?' command
    the dictionay can have the followieng formats:,
    {'<memtype>':{'<contr_unit> <func_unit>':{'<parameter_id>': {PI_KEY_NEW_VALUE: <value>, }, }, }, }
    {'<memtype>':{'<contr_unit> <func_unit>':['<parameter_id>', ], }, }
    {'<memtype>':{'<contr_unit> <func_unit>':None}}
    {'<memtype>':None}
    {}
    @param param_dict : dictionay with the parameters
    @return: string with parameters
    """
    param_str = ''

    if not param_dict:
        return param_str

    for memtype in param_dict:
        if not param_dict[memtype]:
            param_str = param_str + ' ' + memtype
            return param_str

        for unit in param_dict[memtype]:
            if not param_dict[memtype][unit]:
                param_str = param_str + ' ' + memtype + ' ' + unit
                return param_str

            param_list = (
                param_dict[memtype][unit] if isinstance(param_dict[memtype][unit], list) else list(
                    param_dict[memtype][unit].keys()) if isinstance(param_dict[memtype][unit], dict) else [
                    param_dict[memtype][unit]])
            param_str = param_str + ' ' + ' '.join(
                [memtype + ' ' + unit + ' ' + (x if isinstance(x, str) else hex(x)) for x in param_list])

    return param_str


def getparamerterdictfromstring(param_str):
    """
     Parse a string as returned by the 'SPV?' command to a sdictionary
     the string should have following format:
     "<memtype> <contr_unit> <func_unit> <parameter_id> = <vakue> \n
     ...
     <memtype> <contr_unit> <func_unit> <parameter_id> = <vakue>\n"
     @param param_str : string with the parameters
     @return: dictionary with parameters
     """

    answer_dict = {}
    if param_str == '\n' and len(param_str) == 1:
        return answer_dict

    for line in param_str.lstrip().rstrip().split('\n'):
        param_value = line.split('=')
        parmeters = param_value[0].lstrip().rstrip().split(' ')
        if not parmeters[0] in answer_dict:
            answer_dict[parmeters[0]] = {}
        if not parmeters[1] in answer_dict[parmeters[0]]:
            answer_dict[parmeters[0]][parmeters[1]] = {}
        if not parmeters[2] in answer_dict[parmeters[0]][parmeters[1]]:
            answer_dict[parmeters[0]][parmeters[1]][parmeters[2]] = {}
        answer_dict[parmeters[0]][parmeters[1]][parmeters[2]][parmeters[3]] = param_value[1].lstrip().rstrip()

    return answer_dict


def get_parameter_inices(dimension):
    """
    Returns a list of listes with the indices of each parameter e.g.:
    dimesion = [4,2]
    Return = [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1], [3, 0], [3, 1]]
    :param dimension: a list with the dimensions of the parameter e.g. [2,2] for 2X2 matirx
    :type dimension: list
    :return: List of list with the inices of each parameter of the matrix
    :rtype: list
    """
    num_parameters = reduce((lambda x, y: x * y), dimension)
    number_dimesions = len(dimension)
    indices_value_counter = [0] * number_dimesions
    indices_values = [0] * number_dimesions
    indices_array = [[]] * num_parameters

    value_offsets = [0] * num_parameters

    for dim_index in range(number_dimesions):
        if dimension[dim_index + 1:]:
            test = dimension[dim_index + 1:]
            value_offsets[dim_index] = reduce((lambda x, y: x * y), test)
        else:
            value_offsets[dim_index] = 1

    for param in range(num_parameters):
        indices = [0] * number_dimesions
        indices_array[param] = indices
        for dim_index in range(number_dimesions):
            indices_array[param][dim_index] = indices_values[dim_index]
            indices_value_counter[dim_index] = indices_value_counter[dim_index] + 1

            if indices_value_counter[dim_index] + 1 > value_offsets[dim_index]:
                indices_value_counter[dim_index] = 0
                indices_values[dim_index] = indices_values[dim_index] + 1

            if indices_values[dim_index] >= dimension[dim_index]:
                indices_values[dim_index] = 0

    return indices_array


def find_subblock_with_key(umf_dict, key):
    """
    Returns the sub block (SUB_X) with the 'key'of a UMF dictionary
    :param umf_dict: a UMF dictionary
    :param key: the key value
    :type umf_dict: dict
    :type key: str
    :return:
    """
    subblock_couner = 1
    while PIBlockKeys.SUB_MODULE.value + '_' + str(subblock_couner) in umf_dict:
        subblock_couner = subblock_couner + 1

        for sub_block in umf_dict[PIBlockKeys.SUB_MODULE.value + '_' + str(subblock_couner - 1)]:
            if key in sub_block:
                return sub_block

    return None


def get_subdict_form_umfblockcommnaddict(key_value, block_cmd_dict):
    """
    Gets a sub dictionary of 'key_value' form a UMF block command dictionary
    :param key_value: the key value
    :param block_cmd_dict: UMF block command dictionary
    :type key_value: str
    :type block_cmd_dict: dict or list
    :return: the sub dictionary
    :rtype: dict
    """

    if isinstance(block_cmd_dict, list):
        for item in block_cmd_dict:
            answer = get_subdict_form_umfblockcommnaddict(key_value, item)
            if answer:
                return answer

    if isinstance(block_cmd_dict, dict):
        for key in block_cmd_dict:
            if key == key_value:
                return block_cmd_dict[key]

        for key in block_cmd_dict:
            answer = get_subdict_form_umfblockcommnaddict(key_value, block_cmd_dict[key])
            if answer:
                return answer

    return {}
