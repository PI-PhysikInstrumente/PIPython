#!/usr/bin python
# -*- coding: utf-8 -*-
"""Provide GCSError defines and GCSError exception class."""
# too many lines in module pylint: disable=C0302
# line too long pylint: disable=C0301

import json
import os

from ...PILogger import PIDebug
from ..pierror_base import PIErrorBase

__signature__ = 0xf34cc9973cb9024ed4ab12892d3b8d3e

# /*!
#  * \brief Structure of an UMF error.
#  * \- RSD:   		Reserved bit
#  * \- FGroup ID: 	Functional Group ID
#  * \- Error Class:  Config or Processing error
#  * \- Error Code:   The error code
#  *  _______________________________________________________________________________________________________________________________
#  * |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
#  * |               Reserve                 |          ErrorClass           |                     ErrorID                           |
#  * |___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|
#  *
#  */

# error definition begin  ## DO NOT MODIFY THIS LINE!!!
E0_PI_ERROR_NO_ERROR = 0
E49154_NUMBER_OF_ARGUMENTS = 49154
E49155_UNKNOWN_COMMAND = 49155
E49156_COMMAND_LEVEL_TOO_LOW_FOR_COMMAND_ACCESS = 49156
E49157_INVALID_PWD = 49157
E49158_UNKNOWN_SECTION_COMMAND = 49158
E49159_INVALID_CHAR = 49159
E81928_STP = 81928
E245769_WRONG_DATA_TYPE = 245769
E49161_WRONG_DATA_TYPE = 49161
E49162_UNKNOWN_PARAMETER_ID = 49162
E49163_COMMAND_LEVEL_TOO_LOW_FOR_PARAMETER_ACCESS = 49163
E49164_INVALID_VALUE = 49164
E49165_WRONG_PARAMETER_TYPE = 49165
E49166_VALUE_OUT_OF_RANGE = 49166
E49167_UNKNOWN_AXIS_ID = 49167
E49168_ON_LIMIT_SWITCH = 49168
E49169_INVALID_MODE_OF_OPERATION = 49169
E49170_AXIS_NOT_REF = 49170
E81938_AXIS_NOT_REF = 81938
E49171_INVALID_AXIS_STATE = 49171
E49172_TARGET_OUT_OF_RANGE = 49172
E49173_AXIS_DISABLED = 49173
E49174_FAULT_REACTION_ACTIVE = 49174
E81943_LIMIT_SWITCH_ACTIVATED = 81943
E81944_OVER_CURRENT_PROTECTION = 81944
E32793_OUTPUT_LIMIT = 32793
E81946_POSITION_ERROR_TOO_LARGE = 81946
E81947_STOP = 81947
E245788_MAX_DATA_RECORDER_NUMBER_REACHED = 245788
E245789_ALREADY_REGISTERED = 245789
E49182_WRONG_FORMAT = 49182
E49183_UNKNOWN_RECORDER_ID = 49183
E49184_NOT_IN_CONFIG_MODE = 49184
E49185_WRONG_RECORDER_TRIGGER = 49185
E49186_WRONG_STARTPOINT = 49186
E49187_WRONG_NUMPOINT = 49187
E49188_ALREADY_RUNNING = 49188
E49189_TRACE_DOES_NOT_EXIST = 49189
E49190_NOT_ENOUGH_RECORDED_DATA = 49190
E49191_TRACES_NOT_CONFIGURED = 49191
E32808_COMMUNICATION_ERROR = 32808
E49193_FW_INDEX_UNKNOWN = 49193
E65578_TIMEOUT = 65578
E65579_INVALID_SOCKET = 65579
E245804_WRONG_UNIT_ID_FORMAT = 245804
E245805_UNIT_NOT_INITIALIZED = 245805
E245806_MAX_CONNECTION_NUMBER_REACHED = 245806
E245807_CONNECTION_OUTPUT_WRONG_ARGUMENTS = 245807
E245808_CONNECTION_INPUT_WRONG_ARGUMENTS = 245808
E245809_WRONG_DEVICE_ID = 245809
E245810_WRONG_FUNCTION_ID = 245810
E245811_WRONG_PROXY_ID = 245811
E245812_CONNECTION_OUTPUT_INDEX_OUT_OF_RANGE = 245812
E245813_INTERFACE_REGISTRATION_FAILED = 245813
E245814_DEVICE_REGISTRATION_FAILED = 245814
E245815_PROXY_REGISTRATION_FAILED = 245815
E16440_INPUT_PORT_ALREADY_CONNECTED = 16440
E49208_INPUT_PORT_ALREADY_CONNECTED = 49208
E16441_UNIT_ALREADY_REGISTERED = 16441
E16442_CONNECTION_HAS_NO_INPUT = 16442
E49210_CONNECTION_HAS_NO_INPUT = 49210
E16443_CONNECTION_HAS_NO_OUTPUT = 16443
E49211_CONNECTION_HAS_NO_OUTPUT = 49211
E16444_CONNECTION_NOT_FOUND = 16444
E49212_CONNECTION_NOT_FOUND = 49212
E16445_INPUT_PORT_NOT_CONNECTED = 16445
E32830_DATA_CORRUPT = 32830
E49215_UNIT_TYPE_NOT_SUPPORTED = 49215
E65599_UNIT_TYPE_NOT_SUPPORTED = 65599
E49216_FW_UPDATE_ERROR = 49216
E49217_UNIT_NOT_FOUND = 49217
E49218_CUNIT_NOT_FOUND = 49218
E49219_FUNIT_NOT_FOUND = 49219
E65604_NOT_ENOUGH_MEMORY = 65604
E65605_FLASH_READ_FAILED = 65605
E65606_NO_DATA_AVAILABLE = 65606
E65607_FATAL_ERROR = 65607
E49224_AXIS_IN_FAULT = 49224
E81993_REF_SIGNAL_NOT_FOUND = 81993
E65610_TIMEOUT = 65610
E49227_ON_IPR = 49227
E16459_ON_IPR = 16459
E245836_HALT_WAS_COMMANDED = 245836
E49229_EXPR_INVALID = 49229
E49230_EXPR_TOO_COMPLEX = 49230
E49231_LNK_ALREADY_SET = 49231
E49232_LNK_WRONG_INDEX = 49232
E49233_CUNIT_INPUT_NOT_FOUND = 49233
E49234_FUNIT_INPUT_NOT_FOUND = 49234
E49235_CUNIT_OUTPUT_NOT_FOUND = 49235
E49236_FUNIT_OUTPUT_NOT_FOUND = 49236
E49237_UNKNOWN_TRIGGER_ID = 49237

# error definition end  ## DO NOT MODIFY THIS LINE!!!


PI_GCS30_ERRORS_ERRORS_DICT_KEY = 'errors'
PI_GCS30_ERRORS_CLASSES_DICT_KEY = 'classes'
PI_GCS30_ERRORS_MODULES_DICT_KEY = 'modules'
PI_GCS30_ERRORS_ID_KEY = 'id'
PI_GCS30_ERRORS_CLASS_KEY = 'class'
PI_GCS30_ERRORS_MODULE_KEY = 'module'
PI_GCS30_ERRORS_DESCRIPTION_KEY = 'description'
PI_GCS30_ERRORS_TYP_KEY = 'typ'
PI_GCS30_ERRORS_VALUE_KEY = 'value'
PI_GCS30_ERRORS_ALIAS_KEY = 'alias'

ERROR_FILE_PATH = os.path.dirname(__file__) + '/CustomError.json'
POSSIBLE_ERRORS = {}

def parse_error_jdson(file_name):
    """
    Parses the jdson file 'file_name' into a dictionary which is usede by the PIPython to handle the errors
    :param file_name: the GCS3 3.0 Error jdson file (path and file)
    :return: dic which ist used by PIPython to handle the errors
    """
    possible_errors = {}
    error_jdson = json.load(file_name)
    for dict_key in error_jdson:
        if dict_key == PI_GCS30_ERRORS_ERRORS_DICT_KEY:
            possible_errors[PI_GCS30_ERRORS_ERRORS_DICT_KEY] = {}
            for err_id in error_jdson[PI_GCS30_ERRORS_ERRORS_DICT_KEY]:
                error_module_key = error_jdson[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err_id][
                    PI_GCS30_ERRORS_MODULE_KEY]

                module_alias = error_jdson[PI_GCS30_ERRORS_MODULES_DICT_KEY][error_module_key][
                    PI_GCS30_ERRORS_ALIAS_KEY]

                for class_key in error_jdson[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err_id][PI_GCS30_ERRORS_CLASS_KEY]:
                    error_class_alias = error_jdson[PI_GCS30_ERRORS_CLASSES_DICT_KEY][class_key][
                        PI_GCS30_ERRORS_ALIAS_KEY]
                    error_key = err_id.replace('$MODULE', module_alias).replace('$CLASS', error_class_alias)
                    if ':' in error_key:
                        error_id = int(error_key.split(':')[0])
                        error_name = error_key.split(':')[1]
                    else:
                        error_name = error_key

                    error_dict = error_jdson[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err_id].copy()
                    if ':' in error_key:
                        error_dict[PI_GCS30_ERRORS_ID_KEY] = error_id

                    error_dict[PI_GCS30_ERRORS_CLASS_KEY] = class_key
                    possible_errors[PI_GCS30_ERRORS_ERRORS_DICT_KEY][error_name] = error_dict

        else:
            possible_errors[dict_key] = error_jdson[dict_key]

    return possible_errors

with open(ERROR_FILE_PATH, 'r') as error_file:
    POSSIBLE_ERRORS = parse_error_jdson(error_file)

class GCS30Error(PIErrorBase):
    """GCSError exception."""

    def __init__(self, value, message=''):
        """GCSError exception.
        :param value : Error value as integer.
        :param message : Optional message to show in exceptions string representation.
        """
        PIErrorBase.__init__(self, value, message)
        if isinstance(value, GCS30Error):
            self.err = value.err
        else:
            self.err = GCS30Error.get_error_dict(value)
            if self.err:
                self.msg = self.translate_error(self.err)

        PIDebug('GCS30Error: %s', self.msg)

    @staticmethod
    def translate_error(value):
        """Return a readable error message of 'value'.
        :param value : Error value as integer or a gcs30 error dictionary.
        :return : Error message as string if 'value' was an integer else 'value' itself.
        """

        if not isinstance(value, (int, dict)):
            return value

        if isinstance(value, int):
            error_dict = GCS30Error.get_error_dict(value)
        else:
            error_dict = value

        try:
            msg = 'ERROR: ' + str(error_dict[PI_GCS30_ERRORS_VALUE_KEY]) + '\n'
            msg = msg + error_dict[PI_GCS30_ERRORS_DESCRIPTION_KEY] + ' (' + str(
                error_dict[PI_GCS30_ERRORS_ID_KEY]) + ')\n'
            msg = msg + error_dict[PI_GCS30_ERRORS_CLASS_KEY][PI_GCS30_ERRORS_DESCRIPTION_KEY] + ' (' + str(
                error_dict[PI_GCS30_ERRORS_CLASS_KEY][PI_GCS30_ERRORS_ID_KEY]) + ')\n'
        except KeyError:
            if isinstance(value, int):
                error_class, error_id = GCS30Error.parse_errorcode(value)
                msg = 'ERROR: ' + str(value) + '\nUnknown error: class: ' + str(
                    error_class) + ', error: ' + str(error_id) + '\n'
            else:
                msg = 'ERROR: Unknown error\n'

        return msg

    @staticmethod
    def parse_errorcode(error_number):
        """
        parses a error code returnd by the controller into the mocule, class, and error number
        :param error_number: the error code
        :return: [moduel, class, error_number]
        """
        error_class = (error_number & 0x003FC000) >> 14
        error_id = error_number & 0x00003fff

        return error_class, error_id

    @staticmethod
    def parse_to_errorcode(error_class, error_id):
        """
        parses module id, error class and error id to error number
        :type module_id: int
        :param error_class: the error class
        :type error_class: int
        :param error_id: the error id
        :type error_id: int
        :return: error_number
        """
        error_number = (((error_class << 14) & 0x003FC000) | \
                       (error_id & 0x00003fff))
        return error_number

    @staticmethod
    def get_error_dict(error_number):
        """
        gets the gcs30 error dictionary form the error number
        :param error_number:
        :return:
        """
        error_dict = {}
        error_class, error_id = GCS30Error.parse_errorcode(error_number)

        classes_dict = {}
        for classe in POSSIBLE_ERRORS[PI_GCS30_ERRORS_CLASSES_DICT_KEY]:
            if POSSIBLE_ERRORS[PI_GCS30_ERRORS_CLASSES_DICT_KEY][classe][PI_GCS30_ERRORS_ID_KEY] == error_class:
                classes_dict = POSSIBLE_ERRORS[PI_GCS30_ERRORS_CLASSES_DICT_KEY][classe]
                classes_dict[PI_GCS30_ERRORS_TYP_KEY] = classe

        for err in POSSIBLE_ERRORS[PI_GCS30_ERRORS_ERRORS_DICT_KEY]:
            if POSSIBLE_ERRORS[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err][PI_GCS30_ERRORS_ID_KEY] == error_id and \
                    classes_dict[PI_GCS30_ERRORS_TYP_KEY] in POSSIBLE_ERRORS[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err][
                        PI_GCS30_ERRORS_CLASS_KEY]:
                error_dict = {PI_GCS30_ERRORS_TYP_KEY: err}
                error_dict[PI_GCS30_ERRORS_CLASS_KEY] = classes_dict
                error_dict[PI_GCS30_ERRORS_ID_KEY] = POSSIBLE_ERRORS[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err][
                    PI_GCS30_ERRORS_ID_KEY]
                error_dict[PI_GCS30_ERRORS_DESCRIPTION_KEY] = POSSIBLE_ERRORS[PI_GCS30_ERRORS_ERRORS_DICT_KEY][err][
                    PI_GCS30_ERRORS_DESCRIPTION_KEY]
                error_dict[PI_GCS30_ERRORS_VALUE_KEY] = error_number

        return error_dict
