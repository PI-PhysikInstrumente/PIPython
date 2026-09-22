#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""

from time import sleep, time

from ...PILogger import PIDebug
from ...pidevice import GCS30Commands
from ...pidevice.common.gcscommands_helpers import isdeviceavailable, getitemsvaluestuple
from ...pidevice.gcs30.gcs30commands_helpers import PIAxisStatusKeys, PIControlModes
from ...pidevice.gcs30.gcs30error import GCS30Error
from ...pitools.common.gcsbasepitools import GCSBaseDeviceStartup, GCSBaseTools

__signature__ = 0x34fe672e68cbe16ceeba7594282e1b49


# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class GCS30DeviceStartup(GCSBaseDeviceStartup):  # Too many instance attributes pylint: disable=R0902
    """Provide a "ready to use" PI device."""

    DEFAULT_SEQUENCE = (
        'stopall', 'enableaxes', 'referencewait', 'setcontrolmode',)
    SPECIAL_SEQUENCE = {}

    def __init__(self, gcs30pitools, **kwargs):
        """Provide a "ready to use" PI device.
        @type gcs30pitools : GCS30Tools
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        PIDebug('create an instance of GCS30DeviceStartup(kwargs=%s)', gcs30pitools.itemstostr(kwargs))

        if not isdeviceavailable([GCS30Tools, ], gcs30pitools):
            raise TypeError('Type %s of pidevice is not supported!' % type(gcs30pitools).__name__)

        self._controlmodes = None

        super().__init__(gcs30pitools, **kwargs)

        self.prop = {
            'devname': self._pidevice.devname, 'skipeax': False, 'skipref': False, 'forceref': False
        }

    @property
    def controlmodes(self):
        """control modes dict {axis: controlmode} or None."""
        if isinstance(self._controlmodes, int):
            return dict(list(zip(self._pidevice.axes, [self._controlmodes] * self._pidevice.numaxes)))
        return self._controlmodes

    @controlmodes.setter
    def controlmodes(self, controlmodes):
        """Desired control modes as int (for all stages) or dict {axis: controlmode} or None to skip."""
        self._controlmodes = controlmodes
        PIDebug('GCSBaseDeviceStartup.controlmodes = %s', self._pitools.itemstostr(self._controlmodes))

    @property
    def servostates(self):
        """Servo states as dict {axis: state} or None."""
        if self._controlmodes is None:
            return None

        if isinstance(self._controlmodes, int):
            servostates = \
                [True] * self._pidevice.numaxes \
                    if self._controlmodes ==  PIControlModes.CLOSED_LOOP_POSITION.value \
                    else [False] * self._pidevice.numaxes
        else:
            servostates = \
                [n == PIControlModes.CLOSED_LOOP_POSITION.value for n in self._controlmodes]

        return  dict(list(zip(self._pidevice.axes, servostates)))

    @servostates.setter
    def servostates(self, servo):
        """Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip."""
        if servo is None:
            self._controlmodes = None
        elif isinstance(servo, bool):
            self._controlmodes = PIControlModes.CLOSED_LOOP_POSITION.value \
                if servo is True \
                else PIControlModes.OPEN_LOOP_POSITION.value
        else:
            self._controlmodes = {a:PIControlModes.OPEN_LOOP_POSITION.value
                if servo[a] is False
                else PIControlModes.CLOSED_LOOP_POSITION.value
                                  for a in servo.keys()}

        PIDebug('GCS30DeviceStartup.servostates = %s', self._pitools.itemstostr(self._controlmodes))

    def run(self):
        """Run according startup sequence to provide a "ready to use" PI device."""
        PIDebug('GCS30DeviceStartup.run()')
        sequence = self.SPECIAL_SEQUENCE.get(self.prop['devname'], self.DEFAULT_SEQUENCE)
        for func in sequence:
            getattr(self, '%s' % func)()

    def referencewait(self):
        """Reference unreferenced axes if according option has been provided and wait on completion."""
        PIDebug('GCS30DeviceStartup.referencewait()')
        if self.prop['skipref']:
            return

        axes_to_reference = []
        control_modes_before_ref = {}
        axes_status = self.pidevice.qSTV()
        refmodes = self._refmodes if self._refmodes else [None] * len(self._pidevice.allaxes)
        for i, refmode in enumerate(refmodes[:self._pidevice.numaxes]):
            if not refmode:
                continue

            axis = self._pidevice.axes[i]
            if not axes_status[axis][PIAxisStatusKeys.REFERENCE_STATE.value]:
                axes_to_reference.append(axis)
                control_modes_before_ref.update({axis:axes_status[axis][PIAxisStatusKeys.MOP.value]})
                self.pidevice.SAM(axis, '0x0')
                self._pidevice.FRF(axis)

        self._pitools.waitonreferencing(axes_to_reference, **self._kwargs)

        for axis in control_modes_before_ref:
            self.pidevice.SAM(axis, control_modes_before_ref[axis])

    def setcontrolmode(self):
        """Reset servo if it has been changed during referencing."""
        PIDebug('GCS30DeviceStartup.resetservo()')
        if self.controlmodes is not None:
            self._pitools.setcontrolmode(self.controlmodes)

    def enableaxes(self):
        """Enable all connected axes if appropriate."""
        PIDebug('GCS30DeviceStartup.enableaxes()')
        if not self._pidevice.HasEAX() or self.prop['skipeax']:
            return

        for axis in self._pidevice.axes:
            self._pidevice.EAX(axis, True)

    def _isreferenced(self, axis):
        """Check if 'axis' has already been referenced with 'refmode'.
        @param axis : Name of axis to check as string.
        @return : False if 'axis' is not referenced or must be referenced.
        """
        if self.prop['forceref']:
            return False

        return self._pidevice.qFRF(axis)[axis]

    def stopall(self):
        """Stop all axes."""
        PIDebug('GCS30DeviceStartup.stopall()')
        self._pitools.stopall(**self._kwargs)

        self._pidevice.checkerror()


class GCS30Tools(GCSBaseTools):  # Too  public methods pylint: disable=R0903
    """
    Provides a PI tool collection
    """

    PAMID_NEGATIVE_AXIS_LIMIT = '0x121'
    PAMID_POSITIVE_AXIS_LIMIT = '0x122'

    def __init__(self, pidevice):
        """Provide a "ready to use" PI device.
        @type pidevice : pipython.gcscommands.GCS30Commands
        """
        if not isdeviceavailable([GCS30Commands, ], pidevice.gcscommands):
            raise TypeError('Type %s of pidevice is not supported!' % type(pidevice).__name__)

        super().__init__(pidevice, )

    def startup(self, _stages=None, refmodes=None, servostates=True, controlmodes=None, **kwargs):
        assert not isinstance(refmodes, tuple), 'argument "refmodes" must not to be of type "tuple"'
        devstartup = GCS30DeviceStartup(self, **kwargs)

        devstartup.refmodes = refmodes
        if controlmodes is None and servostates is not None:
            devstartup.servostates = servostates
        else:
            devstartup.controlmodes = controlmodes

        devstartup.run()
        return devstartup


    def setcontrolmode(self, axes, controlmodes=None, toignore=None, **kwargs):
        """Set control mode of 'axes' to 'controlmodes', and waits for servo
        operation to finish if appropriate. EAX is enabled for axes with control mode > 0x0.
        @param axes: Axis or list/tuple of axes or dictionary {axis : value}.
        @param controlmodes : int or list of ints or None.
        @param toignore : GCS error as integer to ignore or list of them.
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        @return : False if setting the servo failed.
        """
        if not self._pidevice.HasSAM():
            return False
        if not axes:
            return True
        axes, controlmodes = getitemsvaluestuple(axes, controlmodes)
        eaxaxes = [axes[i] for i in range(len(axes)) if controlmodes[i] != 0x0]
        self.enableaxes(axes=eaxaxes, **kwargs)
        success = True
        toignore = [] if toignore is None else toignore
        toignore = [toignore] if not isinstance(toignore, list) else toignore
        for i, axis in enumerate(axes):
            try:
                self._pidevice.SAM(axis, controlmodes[i])
            except GCS30Error as exc:  # no GCS30Raise() because we want to log a warning
                if exc in toignore:
                    PIDebug('could not set control mode for axis %r to %s: %s', axis, controlmodes[i], exc)
                    success = False
                else:
                    raise
        self.waitonready(**kwargs)
        return success

    def stopall(self, **kwargs):
        """Stops all axes an waits until the affected axes have finished their stop procedure.
        :param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        self._pidevice.StopAll(noraise=True)
        self._wait_on_stopall(**kwargs)

    def getmaxtravelrange(self, axis):
        """Returns the maximum travel range of one axis
        @param axis : Axis to get the value for.
        @return : Dictionary of the maximum travel range and the Axis.
        """
        return {axis: self._pidevice.qSPV("RAM", axis, "-", self.PAMID_POSITIVE_AXIS_LIMIT)
        ["RAM"][axis]["-"][self.PAMID_POSITIVE_AXIS_LIMIT]}

    def getmintravelrange(self, axis):
        """Returns the minimum travel range of one axis
        @param axis : Axis to get the value for.
        @return : Dictionary of the minimum travel range and the Axis.
        """
        return {axis: self._pidevice.qSPV("RAM", axis, "-", self.PAMID_NEGATIVE_AXIS_LIMIT)
        ["RAM"][axis]["-"][self.PAMID_NEGATIVE_AXIS_LIMIT]}

    def _wait_on_stopall(self, timeout=300, polldelay=0.1):
        """Wait until controller is on "ready" state and finally query controller error.
        @param timeout : Timeout in seconds as float.
        @param polldelay : Delay time between polls in seconds as float.
        """
        maxtime = time() + timeout
        while any(self._read_axis_status_flag(axes=[],
                                              flag=PIAxisStatusKeys.DSM_FAULT_REACTION_ACTIVE.value,
                                              defaultvalue=False,
                                              throwonaxiserror=False).values()):
            if time() > maxtime:
                raise SystemError('waitonready() timed out after %.1f seconds' % timeout)
            sleep(polldelay)

    def _move_to_middle(self, axes):
        targets = {}
        for axis in axes:
            rangemin = self._pidevice.qSPV('RAM', axis, '-', self.PAMID_NEGATIVE_AXIS_LIMIT)['RAM'][axis]['-'][
                self.PAMID_NEGATIVE_AXIS_LIMIT]
            rangemax = self._pidevice.qSPV('RAM', axis, '-', self.PAMID_POSITIVE_AXIS_LIMIT)['RAM'][axis]['-'][
                self.PAMID_POSITIVE_AXIS_LIMIT]
            targets[axis] = rangemin + (rangemax - rangemin) / 2.0
        self._pidevice.MOV(targets)

    def _get_control_mode(self, axes):
        axes = self.getaxeslist(axes)
        answer = dict(list(zip(axes, [False] * len(axes))))
        if self._pidevice.HasqSAM():

            if len(axes) == 1:
                control_mode = self._pidevice.qSAM(axes)
            else:
                control_mode = self._pidevice.qSAM()

            for axis in control_mode:
                if not axis in axes:
                    continue

                answer[axis] = control_mode[axis]

        return answer

    def _get_servo_state(self, axes):
        control_modes = self._get_control_mode(axes)
        return  {a: bool(control_modes[a] in  PIControlModes.CLOSED_LOOP.value) for a in control_modes.keys()}

    def _read_axis_status_flag(self, axes, flag, defaultvalue=False, throwonaxiserror=False):
        axes_status_flag = self._pidevice.get_axes_status_flag(axes, flag, throwonaxiserror)

        if not axes_status_flag:
            axes_status_flag = dict(list(zip(axes, [defaultvalue] * len(axes))))

        return axes_status_flag

    def _isreferenced(self, axes, throwonaxiserror=False):
        """Check if 'axes'  already have been referenced with.
        @param axes : List of axes.
        @return : dict {<Axis>: <bool>, } or {} if axis is .
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return {}

        return self._read_axis_status_flag(axes=axes, flag=PIAxisStatusKeys.REFERENCE_STATE.value, defaultvalue=False,
                                           throwonaxiserror=throwonaxiserror)

    def _get_closed_loop_on_target(self, axes, throwonaxiserror=False):
        axes = self.getaxeslist(axes)
        if not axes:
            return {}

        return self._read_axis_status_flag(axes=axes, flag=PIAxisStatusKeys.ON_TARGET.value, defaultvalue=False,
                                           throwonaxiserror=throwonaxiserror)

    def _get_open_loop_on_target(self, axes):
        isontarget = {}
        if self._pidevice.HasqSMR():
            stepsleft = self._get_open_loop_remaining_steps(axes).values()
            isontarget.update(dict(list(zip(axes, [x == 0 for x in stepsleft]))))
        else:
            isontarget.update(dict(list(zip(axes, [True] * len(axes)))))
        return isontarget

    # Too many arguments pylint: disable=R0913
    def _wait_to_the_end_of_reference(self, axes, timeout, polldelay):
        maxtime = time() + timeout
        while not all(list(self._isreferenced(axes, throwonaxiserror=True).values())):
            if time() > maxtime:
                self.stopall()
                raise SystemError('waitonreferencing() timed out after %.1f seconds' % timeout)
            sleep(polldelay)

    def _enable_axes(self, axes):
        for axis in axes:
            self._pidevice.EAX(axis, True)

    def _get_open_loop_remaining_steps(self, axes):
        axes = self.getaxeslist(axes)
        answer = dict(list(zip(axes, [0] * len(axes))))
        if self._pidevice.HasqSMR():
            if len(axes) == 1:
                remaining_steps = self._pidevice.qSMR(axes)
            else:
                remaining_steps = self._pidevice.qSMR()

            for axis in remaining_steps:
                if not axis in axes:
                    continue

                answer[axis] = remaining_steps[axis]

        return answer
