#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to send string commands and handle the answer."""

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
from pipython.pidevice import gcscommands

__signature__ = 0x131230192bfd7ae19ee76c614dfdefa6

def one_item_one_value():
    """Sample for a command that answers with one item (e.g. axis) and one value."""
    with GCSDevice() as pidevice:
        answer = pidevice.ReadGCSCommand('FOO? 1 2 3')
        # This will return:
        # 1 = 1.23
        # 2 = 2.00
        # 3 = 3.45

        # There is a helper function to get a dict of this answer.

        gcscommands.getdict_oneitem(answer, items=None)
        # Answer: {'1': '1.23', '2': '2.00', '3': '3.45'}
        # Remember, all keys and values are strings because the function
        # does not now how to convert.

        gcscommands.getdict_oneitem(answer, items=None, itemconv=int)
        # Answer: {1: '1.23', 2: '2.00', 3: '3.45'}
        # Now the keys are int.

        gcscommands.getdict_oneitem(answer, items=None, itemconv=int, valueconv=(float,))
        # Answer: {1: 1.23, 2: 2.0, 3: 3.45}
        # Now the keys are int and the values are float.
        # Remember the 'valueconv' argument must be a list or a tuple!

        gcscommands.getdict_oneitem(answer, items=None, itemconv=int, valueconv=(True,))
        # Answer: {1: 1.23, 2: 2.0, 3: 3.45}
        # With "True" as conversion function it will be converted as far as possible, i.e.
        # str, float, int is chosen automatically. The "2.0" is converted to float because
        # there is a "." in the string. An answer of "2" would have been converted to int.


def one_item_two_values():
    """Sample for a command that answers with one item (e.g. axis) and two values."""
    with GCSDevice() as pidevice:
        answer = pidevice.ReadGCSCommand('FOO? 1 2 3')
        # This will return:
        # 1 = 1.23 4
        # 2 = 2.00 5
        # 3 = 3.45 6

        gcscommands.getdict_oneitem(answer, items=None)
        # Answer: {'1': ['1.23', '4'], '2': ['2.00', '5'], '3': ['3.45', '6']}
        # Remember, all keys and values are strings because the function
        # does not now how to convert.

        gcscommands.getdict_oneitem(answer, items=None, itemconv=int, valueconv=(float, int))
        # Answer: {'1': [1.23, 4], '2': [2.00, 5], '3': [3.45, 6]}
        # Now the keys are int, the first values are float and the second values are int.


def one_item_multi_values():
    """Sample for a command that answers with one item (e.g. axis) and a different number of values."""
    with GCSDevice() as pidevice:
        answer = pidevice.ReadGCSCommand('FOO? 1 2 3')
        # This will return:
        # 1 = 1.23 4 7 8
        # 2 = 2.00 5 9
        # 3 = 3.45 6

        gcscommands.getdict_oneitem(answer, items=None, itemconv=int, valueconv=(float, int))
        # Answer: {'1': [1.23, 4, 7, 8], '2': [2.00, 5, 9], '3': [3.45, 6]}
        # Now the keys are int, the first values are float and the second and following values are int.


def two_items_one_value():
    """Sample for a command that answers with two items (e.g. axis and option) and one value."""
    with GCSDevice() as pidevice:
        answer = pidevice.ReadGCSCommand('FOO? 1 2 1 4 2 6')
        # This will return:
        # 1 2 = 1.23
        # 1 4 = 2.00
        # 2 6 = 3.45

        # There is a helper function to get a dict of this answer.

        gcscommands.getdict_twoitems(answer, items1=None, items2=None, itemconv=[], valueconv=[])
        # Answer: {'1': {'2': '1.23', '4': '2.00'}, '2': {'6': '3.45'}}
        # Remember, all keys and values are strings because the function
        # does not now how to convert.

        gcscommands.getdict_twoitems(answer, items1=None, items2=None, itemconv=[int, str], valueconv=(float,))
        # Answer: {1: {'2': 1.23, '4': 2.00}, 2: {'6': 3.45}}
        # Now the keys are int and str and the values are float. Remember, itemconv must not be a tuple!


if __name__ == '__main__':
    print('this sample is not executable')
