#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""

import sys
import numbers
from abc import abstractmethod, abstractproperty
from collections import OrderedDict
from io import open  # Redefining built-in 'open' pylint: disable=W0622
from time import sleep, time

from ...PILogger import PIDebug
from ...pidevice.common.gcscommands_helpers import isdeviceavailable
from ...pidevice.gcs2.gcs2commands import GCS2Commands
from ...pidevice.gcs30.gcs30commands import GCS30Commands
from ...pidevice import gcserror
from ...gcserror import GCSError
from ...pidevice.gcs30.gcs30error import GCS30Error
from ...pidevice.common.gcscommands_helpers import getgcsheader, getitemsvaluestuple


__signature__ = 0x405aa2b789efb313fecb01205ca7007f

# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class GCSBaseDeviceStartup(object):  # Too many instance attributes pylint: disable=R0902
    """Provide a "ready to use" PI device."""

    def __init__(self, pitools, **kwargs):
        """Provide a "ready to use" PI device.
        @type pitools : GCSBaseTools
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        PIDebug('create an instance of GCSBaseDeviceStartup(kwargs=%s)', pitools.itemstostr(kwargs))

        if not isdeviceavailable([GCSBaseTools, ], pitools):
            raise TypeError('Type %s of pitools is not supported!' % type(pitools).__name__)

        self._pitools = pitools
        self._pidevice = pitools.pidevice
        self._refmodes = []
        self._kwargs = kwargs
        self.prop = {'devname': self._pidevice.devname}

    @property
    def pidevice(self):
        """
        returns the used pideive
        :return: pipython.gcscommands.GCSCommands
        """
        return self._pidevice

    @property
    def stages(self):
        """Name of stages as list of strings or None."""
        return None

    @stages.setter
    def stages(self, stages):
        """Name of stages to initialize as string or list (not tuple!) or None to skip.
        Skip single axes with "" or None as item in the list.
        """

    @property
    def axesnames(self):
        """Name of axes as list of strings or None."""
        return None

    @axesnames.setter
    def axesnames(self, axesnames):
        """Name of axes to set as list of strings (not tuple!) or None to skip."""

    @property
    def refmodes(self):
        """Referencing commands as list of strings or None."""
        return self._refmodes

    @refmodes.setter
    def refmodes(self, refmodes):
        """Referencing command as string (for all stages) or list (not tuple!) or None to skip.
        Skip single axes with "" or None as item in the list.
        """
        if refmodes is None:
            self._refmodes = None
        else:
            self._refmodes = refmodes if isinstance(refmodes, list) else [refmodes] * len(self._pidevice.allaxes)
        PIDebug('GCSBaseDeviceStartup.refmodes = %s', self._pitools.itemstostr(self._refmodes))

    @abstractproperty
    @property
    def servostates(self):
        """Servo states as dict {axis: state} or None."""

    @abstractproperty
    @servostates.setter
    def servostates(self, servo):
        """Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip."""

    def stopall(self):
        """Stop all axes."""
        PIDebug('GCSBaseDeviceStartup.stopall()')
        self._pitools.stopall(**self._kwargs)

    @abstractmethod
    def run(self):
        """Run according startup sequence to provide a "ready to use" PI device."""

# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class GCSRaise(object):  # Too few public methods pylint: disable=R0903
    """Context manager that asserts raising of specific GCSError(s).
    @param gcserrorid : GCSError ID or iterable of IDs that are expected to be raised as integer.
    @param mustraise : If True an exception must be raised, if False an exception can be raised.
    """

    def __init__(self, gcserrorid, mustraise=True):
        PIDebug('create an instance of GCSRaise(gcserrorid=%s, mustraise=%s', gcserrorid, mustraise)
        self.__expected = gcserrorid if isinstance(gcserrorid, (list, set, tuple)) else [gcserrorid]
        self.__mustraise = mustraise and gcserrorid

    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, _exctraceback):
        gcsmsg = '%r' % gcserror.translate_error(excvalue)
        if exctype in (GCSError, GCS30Error):
            if gcsmsg == str(excvalue.val):
                gcsmsg = '%r' % GCS30Error.translate_error(excvalue)
            if excvalue in self.__expected:
                PIDebug('expected GCSError %s was raised', gcsmsg)
                return True  # do not re-raise
        if not self.__mustraise and excvalue is None:
            PIDebug('no error was raised')
            return True  # do not re-raise
        expected = ''
        for err in self.__expected:
            errval = gcserror.translate_error(err)
            if errval == str(err):
                errval = GCS30Error.translate_error(err)
            expected = expected + errval + ', '
        msg = 'expected %s%r but raised was %s' % ('' if self.__mustraise else 'no error or ', expected, gcsmsg)
        if exctype is not None:
            raise ValueError(msg) from exctype(excvalue)

        raise ValueError(msg) from Exception


# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class FrozenClass(object):  # Too few public methods pylint: disable=R0903
    """Freeze child class when self.__isfrozen is set, i.e. values of already existing properties can still
    be changed but no new properties can be added.
    """
    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen and key not in dir(self):  # don't use hasattr(), it returns False on any exception
            raise TypeError('%r is immutable, cannot add %r' % (self, key))
        object.__setattr__(self, key, value)

    def _freeze(self):
        """After this method has been called the child class denies adding new properties."""
        self.__isfrozen = True


class GCSBaseTools(object):
    """
    Provides a PI tool collection
    """
    def __init__(self, pidevice):
        """Provide a "ready to use" PI device.
        @type pidevice : pipython.gcscommands.GCSCommands
        """
        if not isdeviceavailable([GCS2Commands, GCS30Commands, ], pidevice.gcscommands):
            raise TypeError('Type %s of pidevice is not supported!' % type(pidevice).__name__)

        self._pidevice = pidevice

    @property
    def pidevice(self):
        """
        Returns the 'pidevice'
        :return: pidevice
        :rtype: pipython.gcscommands.GCSCommands
        """
        return self._pidevice

    @staticmethod
    def enum(*args, **kwargs):
        """Return an Enum object of 'args' (enumerated) and 'kwargs' that can convert the values back to its names."""
        enums = dict(list(zip(args, range(len(args)))), **kwargs)
        reverse = dict((value, key) for key, value in enums.items())
        enums['name'] = reverse
        return type('Enum', (object,), enums)

    def ontarget(self, axes):
        """Return dictionary of on target states for open- or closedloop 'axes'.
        If qOSN is not supported open loop axes will return True.
        @param axes : Axis or list/tuple of axes to get values for or None for all axes.
        @return : Dictionary of boolean ontarget states of 'axes'.
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return {}
        servo = self.getservo(axes)
        closedloopaxes = [axis for axis in axes if servo[axis]]
        openloopaxes = [axis for axis in axes if not servo[axis]]
        isontarget = {}
        if closedloopaxes:
            isontarget.update(self._get_closed_loop_on_target(closedloopaxes))
        if openloopaxes:
            isontarget.update(self._get_open_loop_on_target(openloopaxes))
        return isontarget

    def getservo(self, axes):
        """Return dictionary of servo states or "False" if the qSVO command is not supported.
        @param axes : Axis or list/tuple of axes to get values for or None for all axes.
        @return : Dictionary of boolean servo states of 'axes'.
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return {}

        return self._get_servo_state(axes)

    def getaxeslist(self, axes):
        """Return list of 'axes'.
        @param axes : Axis as string or list or tuple of them or None for all axes.
        @return : List of axes from 'axes' or all axes or empty list.
        """
        axes = self._pidevice.axes if axes is None else axes
        if not axes:
            return []
        if not isinstance(axes, (list, set, tuple)):
            axes = [axes]
        return list(axes)  # convert tuple to list

    def waitonready(self, timeout=300, predelay=0, polldelay=0.1):
        """Wait until controller is on "ready" state and finally query controller error.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param polldelay : Delay time between polls in seconds as float.
        """
        sleep(predelay)
        if not self._pidevice.HasIsControllerReady():
            return
        maxtime = time() + timeout
        while not self._pidevice.IsControllerReady():
            if time() > maxtime:
                raise SystemError('waitonready() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        self._pidevice.checkerror()

    # Too many arguments (6/5) pylint: disable=R0913
    def waitontarget(self, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until all closedloop 'axes' are on target.
        @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param postdelay : Additional delay time in seconds as float after reaching desired state.
        @param polldelay : Delay time between polls in seconds as float.
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return

        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)

        if not self._pidevice.HasqONT():
            return

        servo = self.getservo(axes)
        axes = [x for x in axes if servo[x]]
        maxtime = time() + timeout
        while not all(list(self._get_closed_loop_on_target(axes, throwonaxiserror=True).values())):
            if time() > maxtime:
                raise SystemError('waitontarget() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        sleep(postdelay)

    # Too many arguments pylint: disable=R0913
    def waitonreferencing(self, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until referencing of 'axes' is finished or timeout.
        @param axes : Axis or list/tuple of axes to wait for or None for all axes.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param postdelay : Additional delay time in seconds as float after reaching desired state.
        @param polldelay : Delay time between polls in seconds as float.
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        self._wait_to_the_end_of_reference(axes, timeout, polldelay)
        sleep(postdelay)


    def setservo(self, axes, states=None, toignore=None, **kwargs):
        """Set servo of 'axes' to 'states'. Calls RNP for openloop axes and waits for servo
        operation to finish if appropriate. EAX is enabled for closedloop axes.
        @param axes: Axis or list/tuple of axes or dictionary {axis : value}.
        @param states : Bool or list of bools or None.
        @param toignore : GCS error as integer to ignore or list of them.
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        @return : False if setting the servo failed.
        """
        if not self._pidevice.HasSVO():
            return False
        if not axes:
            return True
        axes, states = getitemsvaluestuple(axes, states)
        if self._pidevice.HasRNP():
            axestorelax = [axis for axis, state in list(self.getservo(axes).items()) if not state]
            if axestorelax:
                self._pidevice.RNP(axestorelax, [0.0] * len(axestorelax))
                self.waitonready(**kwargs)
        eaxaxes = [axes[i] for i in range(len(axes)) if states[i]]
        self.enableaxes(axes=eaxaxes, **kwargs)
        success = True
        toignore = [] if toignore is None else toignore
        toignore = [toignore] if not isinstance(toignore, list) else toignore
        toignore += [gcserror.E5_PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO, gcserror.E23_PI_CNTR_ILLEGAL_AXIS]
        for i, axis in enumerate(axes):
            try:
                self._pidevice.SVO(axis, states[i])
            except GCSError as exc:  # no GCSRaise() because we want to log a warning
                if exc in toignore:
                    PIDebug('could not set servo for axis %r to %s: %s', axis, states[i], exc)
                    success = False
                else:
                    raise
        self.waitonready(**kwargs)
        return success


    def enableaxes(self, axes, **kwargs):
        """Enable all 'axes'.
        @param axes : String or list/tuple of strings of axes to enable.
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        if not self._pidevice.HasEAX():
            return

        axes = self.getaxeslist(axes)
        if not axes:
            return

        self._enable_axes(axes)
        self.waitonready(**kwargs)


    def stopall(self, **kwargs):
        """Stop motion of all axes and mask the "error 10" warning.
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        self._pidevice.StopAll(noraise=True)
        self.waitonready(**kwargs)  # there are controllers that need some time to halt all axes


    def movetomiddle(self, axes=None):
        """Move 'axes' to its middle positions but do not wait "on target".
        @param axes : List/tuple of strings of axes to get values for or None to query all axes.
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return

        self._move_to_middle(axes)


    def moveandwait(self, axes, values=None, timeout=300):
        """Call MOV with 'axes' and 'values' and wait for motion to finish.
        @param axes : Dictionary of axis:target or list/tuple of axes or axis.
        @param values : Optional list of values or value.
        @param timeout : Seconds as float until SystemError is raised.
        """
        if not axes:
            return
        axes, values = getitemsvaluestuple(axes, values)
        self._pidevice.MOV(axes, values)
        self.waitontarget(axes=axes, timeout=timeout)

    @staticmethod
    def savegcsarray(filepath, header, data):
        """Save data recorder output to a GCSArray file.
        @param filepath : Full path to target file as string.
        @param header : Header information from qDRR() as dictionary or None.
        @param data : Datarecorder data as one or two dimensional list of floats or NumPy array.
        """
        PIDebug('save %r', filepath)
        try:
            data = data.tolist()  # convert numpy array to list
        except AttributeError:
            pass  # data already is a list
        if not isinstance(data[0], list):  # data must be multi dimensional
            data = [data]
        if header is None:
            header = OrderedDict([('VERSION', 1), ('TYPE', 1), ('SEPARATOR', 32), ('DIM', len(data)),
                                  ('NDATA', len(data[0]))])
        sep = chr(header['SEPARATOR'])
        out = ''
        for key, value in header.items():
            out += '# %s = %s \n' % (key, value)
        out += '# \n# END_HEADER \n'
        for values in map(list, zip(*data)):  # transpose data
            out += sep.join(['%f' % value for value in values]) + ' \n'
        out = out[:-2] + '\n'
        GCSBaseTools.piwrite(filepath, out)


    @staticmethod
    def readgcsarray(filepath):
        """Read a GCSArray file and return header and data.
        Scans the file until the start of the data is found
        to account additional information at the start of the file
        @param filepath : Full path to file as string.
        @return header : Header information from qDRR() as dictionary.
        @return data : Datarecorder data as two columns list of floats.
        """
        PIDebug('read %r', filepath)
        headerstr, datastr = [], []
        gcsarray_found = False

        with open(filepath, 'r', encoding='utf-8', newline='\n') as fobj:
            for line in fobj:
                if line.startswith('[GCS_ARRAY'):
                    gcsarray_found = True
                    continue

                if line.startswith('#'):
                    gcsarray_found = True

                if not gcsarray_found:
                    continue

                if line.startswith('#'):
                    headerstr.append(line)
                else:
                    datastr.append(line)

        header = getgcsheader('\n'.join(headerstr))
        sep = chr(header['SEPARATOR'])
        numcolumns = header['DIM']
        data = [[] for _ in range(numcolumns)]
        for line in datastr:
            if not line.strip():
                continue
            values = [float(x) for x in line.strip().split(sep)]
            for i in range(numcolumns):
                data[i].append(values[i])
        return header, data


    @staticmethod
    def itemstostr(data):
        """Convert 'data' into a string message.
        @param data : Dictionary or list or tuple or single item to convert.
        """
        if data is False:
            return 'False'

        if not isinstance(data, numbers.Number):
            if not data:
                return 'None'

        msg = ''
        if isinstance(data, dict):
            for key, value in list(data.items()):
                msg += '%s: %s, ' % (key, value)
        elif isinstance(data, (list, set, tuple)):
            for value in data:
                msg += '%s, ' % value
        else:
            msg = str(data)
        try:
            msg = msg.rstrip(b', ')
        except TypeError:
            msg = msg.rstrip(', ')
        return msg


    @staticmethod
    def piwrite(filepath, text):
        """Write 'text' to 'filepath' with preset encoding.
        @param filepath : Full path to file to write as string, existing file will be replaced.
        @param text : Text to write as string or list of strings (with trailing line feeds).
        """
        if isinstance(text, list):
            text = ''.join(text)
        with open(filepath, 'w', encoding='utf-8', newline='\n') as fobj:
            if sys.platform in ('linux', 'linux2', 'darwin'):
                try:
                    fobj.write(text.decode('utf-8'))
                except (UnicodeEncodeError, AttributeError):
                    fobj.write(text)
            else:
                try:
                    fobj.write(text)
                except TypeError:
                    try:
                        fobj.write(text.decode('cp1252'))
                    except TypeError:
                        fobj.write(text.decode('utf-8'))


    @abstractmethod
    def startup(self, stages=None, refmodes=None, servostates=True, controlmodes=None, **kwargs):
        """Define 'stages', stop all, enable servo on all connected axes and reference them with 'refmodes'.
        Defining stages and homing them is done only if necessary.
        @param refmodes : Referencing command as string (for all stages) or list (not tuple!) or None to skip.
        @param servostates : Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip.
                         for controllers with GCS 3.0 syntax:
                                if True the axis is switched into control mode 0x2.
                                if False the axis is switched into contorl mode 0x1.
        @param controlmodes : !!! Only valid for controllers with GCS 3.0 syntax !!!
                          switches the axis into the given control mode
                          int (for all stages) or dict {axis: controlmode} or None to ignore.
                          To skip any control mode switch the servostate has to be None also!
                          If controlmode is not None the parameter servostate is ignored
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        :return: Instance to a DeviceStarup object
        :rtype: DeviceStarup
        """

    @abstractmethod
    def _get_servo_state(self, axes):
        """
        Gets the servo state of 'axes'
        :param axes: String convertible or list of them or None
        :type axes: String or list or None
        :return: the servor states of 'axes'
        :rtype: Ordered dictionary of {axis: value}, values are bool
        """

    @abstractmethod
    def _get_closed_loop_on_target(self, axes, throwonaxiserror=False):
        """Return dictionary of on target states for closed loop 'axes'.
        @param axes : Axis or list/tuple of axes to get values for or None for all axes.
        @param throwonaxiserror: only for GCS30! Throw an exeception on an axis error
        @return : Dictionary of boolean ontarget states of 'axes'.
        """

    @abstractmethod
    def _get_open_loop_on_target(self, axes):
        """Return dictionary of on target states for open loop 'axes'.
        @param axes : Axis or list/tuple of axes to get values for or None for all axes.
        @return : Dictionary of boolean ontarget states of 'axes'.
        """

    @abstractmethod
    def _wait_to_the_end_of_reference(self, axes, timeout, polldelay):
        """Wait until referencing of 'axes' is finished or timeout.
        @param axes : Axis or list/tuple of axes to wait for or None for all axes.
        @param timeout : Timeout in seconds as float.
        @param polldelay : Delay time between polls in seconds as float.
        """

    @abstractmethod
    def _enable_axes(self, axes):
        """Enable all 'axes'.
        @param axes : String or list/tuple of strings of axes to enable.
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """

    @abstractmethod
    def _move_to_middle(self, axes):
        """Move 'axes' to its middle positions but do not wait "on target".
        @param axes : List/tuple of strings of axes to get values for or None to query all axes.
        """
