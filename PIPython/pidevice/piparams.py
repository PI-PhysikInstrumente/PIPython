#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for handling PI device parameters."""

from . import GCSError, gcserror

__signature__ = 0x5c35caff6a9b938cbab66fdbc56f9105


def applyconfig(pidevice, axis, config, andsave=False):
    """Try to apply 'config' for 'axis' by applyconfig() or CST() function.
    @type pidevice : pipython.gcscommands.GCSDevice
    @param axis: Single axis as string convertible.
    @param config: Name of a configuration existing in PIStages database as string.
    @param andsave: saves the configuration to non volatile memory on the controller.
    @return : Warning as string or empty string on success.
    """
    try:
        pidevice.dll.applyconfig(items='axis %s' % axis, config=config, andsave=andsave)
    except AttributeError:  # function not found in DLL
        if not pidevice.HasCST():
            return 'CST command is not supported'
        pidevice.CST(axis, config)
    except GCSError as exc:
        if exc == gcserror.E_10013_PI_PARAMETER_DB_AND_HPA_MISMATCH_LOOSE:
            pidevice.resetaxes()
            return '%s\n%s' % (exc, pidevice.dll.warning.rstrip())
        raise
    pidevice.resetaxes()
    return ''


def readconfig(pidevice):
    """Try to read available stages by readconfig() or qVST() function.
    @type pidevice : pipython.gcscommands.GCSDevice
    @return : Answer as list of string.
    """
    try:
        answer = pidevice.dll.getconfigs()
    except AttributeError:  # function not found in DLL
        if not pidevice.HasqVST():
            return 'qVST command is not supported'
        answer = pidevice.qVST()
    return answer.split()
