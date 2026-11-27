#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""
import inspect

from ..pidevice.common.gcscommands_helpers import isdeviceavailable
from ..pidevice.gcs2.gcs2commands import GCS2Commands
from ..pidevice.gcs30.gcs30commands import GCS30Commands
from .gcs2.gcs2pitools import GCS2Tools, GCS2DeviceStartup
from .gcs30.gcs30pitools import GCS30Tools, GCS30DeviceStartup
from .common.gcsbasepitools import GCSBaseTools


__signature__ = 0x6b04ea5e2aad8bd670fa4bf4300ca3b

class PIInvalidDevice(Exception):
    """
    Exception for an invalid PI device
    """

# Function name "DeviceStartup" doesn't conform to snake_case naming style pylint: disable=C0103
def DeviceStartup(pidevice, **kwargs):
    """
    Gets an instance to an DeviceStartup object dependen on
    the Type'pidevice' (GCS2Commands or GCS30Commands)
    :param pidevice: an istance to GCS2Commands or GCS30Commands object
    :type pidevice: GCS2Commands or GCS30Commands
    :param kwargs: Optional arguments with keywords that are passed to sub functions.
    :return: instance to a DeviceStartop object
    :rtype: GCS2DeviceStartup or GCS30DeviceStartup
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2DeviceStartup(GCS2Tools(pidevice), **kwargs)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30DeviceStartup(GCS30Tools(pidevice), **kwargs)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def startup(pidevice, stages=None, refmodes=None, servostates=True, controlmodes=None, **kwargs):
    """Define 'stages', stop all, enable servo on all connected axes and reference them with 'refmodes'.
    Defining stages and homing them is done only if necessary.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param stages : Name of stages to initialize as string or list (not tuple!) or None to skip.
    @param refmodes : Referencing command as string (for all stages) or list (not tuple!) or None to skip.
    @param servostates : Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip.
                         for controllers with GCS 3.0 syntax:
                                if True the axis is switched into control mode 0x2.
                                if False the axis is switched into control mode 0x1.
    @param controlmodes : !!! Only valid for controllers with GCS 3.0 syntax !!!
                          switch the axis into the given control mode
                          int (for all stages) or dict {axis: controlmode} or None to ignore.
                          To skip any control mode switch the servostate has to be None also!
                          If controlmode is not None the parameter servostate is ignored
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).startup(stages, refmodes, servostates, **kwargs)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).startup(stages, refmodes, servostates, controlmodes, **kwargs)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def enableaxes(pidevice, axes, **kwargs):
    """Enable all 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : String or list/tuple of strings of axes to enable.
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).enableaxes(axes, **kwargs)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).enableaxes(axes, **kwargs)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def setservo(pidevice, axes, states=None, toignore=None, **kwargs):
    """Set servo of 'axes' to 'states'. Calls RNP for openloop axes and waits for servo
    operation to finish if appropriate. EAX is enabled for closed loop axes.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes: Axis or list/tuple of axes or dictionary {axis : value}.
    @param states : Bool or list of bools or None.
    @param toignore : GCS error as integer to ignore or list of them.
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    @return : False if setting the servo failed.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).setservo(axes, states, toignore, **kwargs)


    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).setservo(axes, states, toignore, **kwargs)


    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def getservo(pidevice, axes):
    """Return dictionary of servo states or "False" if the qSVO command is not supported.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis or list/tuple of axes to get values for or None for all axes.
    @return : Dictionary of boolean servo states of 'axes'.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getservo(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getservo(axes)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def moveandwait(pidevice, axes, values=None, timeout=300):
    """Call MOV with 'axes' and 'values' and wait for motion to finish.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Dictionary of axis:target or list/tuple of axes or axis.
    @param values : Optional list of values or value.
    @param timeout : Seconds as float until SystemError is raised.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).moveandwait(axes, values, timeout)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).moveandwait(axes, values, timeout)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def movetomiddle(pidevice, axes=None):
    """Move 'axes' to its middle positions but do not wait "on target".
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : List/tuple of strings of axes to get values for or None to query all axes.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).movetomiddle(axes)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).movetomiddle(axes)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def ontarget(pidevice, axes):
    """Return dictionary of on target states for open- or closedloop 'axes'.
    If qOSN is not supported open loop axes will return True.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis or list/tuple of axes to get values for or None for all axes.
    @return : Dictionary of boolean ontarget states of 'axes'.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).ontarget(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).ontarget(axes)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def stopall(pidevice, **kwargs):
    """
    for GCS2 Controllers:  Stop motion of all axes and mask the "error 10" warning.
    for GCS30 Controllers: Stops all axes an waits until the affected axes have finished their stop procedure.
    :type pidevice : pipython.gcscommands.GCSCommands
    :param kwargs : Optional arguments with keywords that are passed to sub functions.
    :return: Only for GCS30 Controllers returns the affected axes
    :rtype: list. Only for GCS30 Controllers.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).stopall(**kwargs)
        return []

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).stopall(**kwargs)


    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def getaxeslist(pidevice, axes):
    """Return list of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list or tuple of them or None for all axes.
    @return : List of axes from 'axes' or all axes or empty list.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getaxeslist(axes)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getaxeslist(axes)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def waitonready(pidevice, timeout=300, predelay=0, polldelay=0.1):
    """Wait until controller is on "ready" state and finally query controller error.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonready(timeout, predelay, polldelay)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).waitonready(timeout, predelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


# Too many arguments pylint: disable=R0913
def waitontarget(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all closedloop 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitontarget(axes, timeout, predelay, postdelay, polldelay)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).waitontarget(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


# Too many arguments pylint: disable=R0913
def waitonreferencing(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until referencing of 'axes' is finished or timeout.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis or list/tuple of axes to wait for or None for all axes.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonreferencing(axes, timeout, predelay, postdelay, polldelay)
        return

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        GCS30Tools(pidevice).waitonreferencing(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def writewavepoints(pidevice, wavetable, wavepoints, bunchsize=None):
    """Write 'wavepoints' for 'wavetable' in bunches of 'bunchsize'.
    The 'bunchsize' is device specific. Please refer to the controller manual.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param wavetable : Wave table ID as integer.
    @param wavepoints : Single wavepoint as float convertible or list/tuple of them.
    @param bunchsize : Number of wavepoints in a single bunch or None to send all 'wavepoints' in a single bunch.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).writewavepoints(wavetable, wavepoints, bunchsize)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def waitonfastalign(pidevice, name=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param name : Name of the process as string or list/tuple.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonfastalign(name, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def waitonwavegen(pidevice, wavegens=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param wavegens : Integer convertible or list/tuple of them or None.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonwavegen(wavegens, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def waitonautozero(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonautozero(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


# Too many arguments pylint: disable=R0913
def waitonphase(pidevice, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on phase.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonphase(axes, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


# Too many arguments pylint: disable=R0913
def waitonwalk(pidevice, channels, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until qOSN for channels is zero.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param channels : Channel or list or tuple of channels to wait for motion to finish.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonwalk(channels, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


# Too many arguments pylint: disable=R0913
def waitonoma(pidevice, axes=None, timeout=300, predelay=0, polldelay=0.1):
    """Wait on the end of an open loop motion of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list/tuple of them to get values for or None to query all axes.
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonoma(axes, timeout, predelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


# Too many arguments pylint: disable=R0913
def waitontrajectory(pidevice, trajectories=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'trajectories' are done and all axes are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param trajectories : Integer convertible or list/tuple of them or None for all trajectories.
    @param timeout : Timeout in seconds as floatfor trajectory and motion.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitontrajectory(trajectories, timeout, predelay, postdelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def waitonmacro(pidevice, timeout=300, predelay=0, polldelay=0.1):
    """Wait until all macros are finished, then query and raise macro error.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param timeout : Timeout in seconds as float.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        GCS2Tools(pidevice).waitonmacro(timeout, predelay, polldelay)
        return

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def savegcsarray(filepath, header, data):
    """Save data recorder output to a GCSArray file.
    @param filepath : Full path to target file as string.
    @param header : Header information from qDRR() as dictionary or None.
    @param data : Datarecorder data as one or two dimensional list of floats or NumPy array.
    """
    GCSBaseTools.savegcsarray(filepath, header, data)


def readgcsarray(filepath):
    """Read a GCSArray file and return header and data.
    Scans the file until the start of the data is found
    to account additional information at the start of the file
    @param filepath : Full path to file as string.
    @return header : Header information from qDRR() as dictionary.
    @return data : Datarecorder data as two columns list of floats.
    """
    return GCSBaseTools.readgcsarray(filepath)


def itemstostr(data):
    """Convert 'data' into a string message.
    @param data : Dictionary or list or tuple or single item to convert.
    """
    return GCSBaseTools.itemstostr(data)


def piwrite(filepath, text):
    """Write 'text' to 'filepath' with preset encoding.
    @param filepath : Full path to file to write as string, existing file will be replaced.
    @param text : Text to write as string or list of strings (with trailing line feeds).
    """
    GCSBaseTools.piwrite(filepath, text)


def enum(*args, **kwargs):
    """Return an Enum object of 'args' (enumerated) and 'kwargs' that can convert the values back to its names."""
    return GCSBaseTools.enum(*args, **kwargs)


def getmaxtravelrange(pidevice, axis):
    """
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axis : Axis to get the value for.
    @return : Dictionary of the maximum travel range and the Axis.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getmaxtravelrange(axis)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getmaxtravelrange(axis)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))


def getmintravelrange(pidevice, axis):
    """
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axis : Axis to get the value for.
    @return : Dictionary of the minimum travel range and the Axis.
    """
    if isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
        return GCS2Tools(pidevice).getmintravelrange(axis)

    if isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
        return GCS30Tools(pidevice).getmintravelrange(axis)

    raise PIInvalidDevice("Type %s of pidevice is not supported for '%s'!" %
                          (type(pidevice).__name__, inspect.stack()[0].function))
