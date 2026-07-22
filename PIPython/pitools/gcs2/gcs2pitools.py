#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""

from time import sleep, time

from ...PILogger import PIDebug, PIInfo, PIWarning
from ...pidevice.gcs2.gcs2commands import GCS2Commands
from ...pidevice import gcserror
from ...pidevice.gcserror import GCSError
from ...pidevice.common.gcscommands_helpers import isdeviceavailable
from ...pidevice.piparams import applyconfig
from ...pitools.common.gcsbasepitools import GCSBaseDeviceStartup, GCSBaseTools

__signature__ = 0x4d6f064bbc8acdbe6aae5c27c6c52986


# Class inherits from object, can be safely removed from bases in python3 pylint: disable=R0205
class GCS2DeviceStartup(GCSBaseDeviceStartup):  # Too many instance attributes pylint: disable=R0902
    """Provide a "ready to use" PI device."""

    DEFAULT_SEQUENCE = (
        'setaxesnames', 'setstages', 'callini', 'enableonl', 'stopall', 'waitonready', 'enableaxes', 'referencewait',
        'findphase', 'resetservo', 'waitonready',)
    SPECIAL_SEQUENCE = {
        'HYDRA': [x for x in DEFAULT_SEQUENCE if x not in ('callini',)],
        'C-887': [x for x in DEFAULT_SEQUENCE if x not in ('stopall',)],
        'E-861 VERSION 7': [x for x in DEFAULT_SEQUENCE if x not in ('stopall',)],
    }

    def __init__(self, gcs2pitools, **kwargs):
        """Provide a "ready to use" PI device.
        @type gcs2pitools : GCS2Tools
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        PIDebug('create an instance of GCS2DeviceStartup(kwargs=%s)', gcs2pitools.itemstostr(kwargs))

        if not isdeviceavailable([GCS2Tools,], gcs2pitools):
            raise TypeError('Type %s of pidevice is not supported!' % type(gcs2pitools).__name__)

        super().__init__(gcs2pitools, **kwargs)

        self._stages = None
        self._axesnames = None
        self._servo = None
        self._databuf = {'servobuf': {}, 'cstdone': []}
        self.prop = {
            'devname': self._pidevice.devname, 'skipcst': False, 'forcecst': False, 'skipsai': False,
            'forcesai': False, 'showlog': False, 'skipini': False, 'skiponl': False, 'skipeax': False,
            'skipref': False, 'forceref': False, 'skipfph': False,
        }

    @property
    def servostates(self):
        """Servo states as dict {axis: state} or None."""
        if isinstance(self._servo, bool):
            return dict(list(zip(self._pidevice.axes, [self._servo] * self._pidevice.numaxes)))
        return self._servo

    @servostates.setter
    def servostates(self, servo):
        """Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip."""
        self._servo = servo
        PIDebug('GCS2DeviceStartup.servostates = %s', self._pitools.itemstostr(self._servo))

    @property
    def stages(self):
        return self._stages

    @stages.setter
    def stages(self, stages):
        if stages is None:
            self._stages = None
        else:
            self._stages = stages if isinstance(stages, list) else [stages] * len(self._pidevice.allaxes)
        PIDebug('GCS2DeviceStartup.stages = %s', self._pitools.itemstostr(self._stages))

    @property
    def axesnames(self):
        """Name of axes as list of strings or None."""
        return self._axesnames

    @axesnames.setter
    def axesnames(self, axesnames):
        """Name of axes to set as list of strings (not tuple!) or None to skip."""
        if axesnames is None:
            self._axesnames = None
        else:
            assert isinstance(axesnames, list), 'axesnames must be list'
            self._axesnames = axesnames
        PIDebug('GCS2DeviceStartup.axesnames = %s', self._pitools.itemstostr(self._axesnames))

    def run(self):
        """Run according startup sequence to provide a "ready to use" PI device."""
        PIDebug('GCS2DeviceStartup.run()')
        sequence = self.SPECIAL_SEQUENCE.get(self.prop['devname'], self.DEFAULT_SEQUENCE)
        for func in sequence:
            getattr(self, '%s' % func)()

    def setstages(self):
        """Set stages if according option has been provided."""
        if not self._stages or self.prop['skipcst']:
            return
        PIDebug('GCS2DeviceStartup.setstages()')
        allaxes = self._pidevice.qSAI_ALL()
        oldstages = self._pidevice.qCST()
        for i, newstage in enumerate(self._stages):
            if not newstage:
                continue
            axis = allaxes[i]
            oldstage = oldstages.get(axis, 'NOSTAGE')
            if oldstage != newstage or self.prop['forcecst']:
                warnmsg = applyconfig(self._pidevice, axis, newstage)
                self._databuf['cstdone'].append(axis)
                if self.prop['showlog'] and warnmsg:
                    PIWarning(warnmsg)
            elif self.prop['showlog']:
                PIInfo('stage %r on axis %r is already configured', oldstage, axis)

    def findphase(self):
        """Start find phase if cst was done before
        """
        PIDebug('GCS2DeviceStartup.findphase()')
        if not self._pidevice.HasFPH() or self.prop['skipfph']:
            return
        if not self._databuf['cstdone']:
            PIDebug('no need to do find phase for axes %r', self._pidevice.axes)
            return
        for axis in self._databuf['cstdone']:
            if self._pidevice.qFRF(axis)[axis]:
                self._pidevice.FPH(axis)
                self._pitools.waitonphase(**self._kwargs)
                self._pidevice.WPA()
            else:
                PIInfo('skip find phase for axis while axis %s is not referenced', axis)

    def setaxesnames(self):
        """Set stages if according option has been provided."""
        if not self._axesnames or self.prop['skipsai']:
            return
        PIDebug('GCS2DeviceStartup.setaxesnames()')
        oldaxes = self._pidevice.qSAI_ALL()
        for i, newaxis in enumerate(self.axesnames):
            if newaxis != oldaxes[i] or self.prop['forcesai']:
                setstage = False
                if self._pidevice.HasqCST():
                    if self._pidevice.qCST()[oldaxes[i]] == 'NOSTAGE':
                        try:
                            PIDebug('try rename NOSTAGE to TEMP (0x3C)')
                            self._pidevice.SPA(oldaxes[i], 0x3c, 'TEMP')
                            setstage = True
                        except GCSError:
                            pass
                self._pidevice.SAI(oldaxes[i], newaxis)
                if setstage:
                    self._pidevice.SPA(newaxis, 0x3c, 'NOSTAGE')
                    PIDebug('restore NOSTAGE (0x3C)')

    def callini(self):
        """Call INI command if available."""
        PIDebug('GCS2DeviceStartup.callini()')
        if not self._pidevice.HasINI() or self.prop['skipini']:
            return
        self._pidevice.INI()

    def enableonl(self):
        """Enable online state of connected axes if available."""
        PIDebug('GCS2DeviceStartup.enableonl()')
        if not self._pidevice.HasONL() or self.prop['skiponl']:
            return
        self._pidevice.ONL(list(range(1, self._pidevice.numaxes + 1)), [True] * self._pidevice.numaxes)

    def waitonready(self):
        """Wait until device is ready."""
        PIDebug('GCS2DeviceStartup.waitonready()')
        self._pitools.waitonready(**self._kwargs)

    def resetservo(self):
        """Reset servo if it has been changed during referencing."""
        PIDebug('GCS2DeviceStartup.resetservo()')
        if self.servostates is not None:
            self._pitools.setservo(self.servostates)
        elif self._databuf['servobuf']:
            self._pitools.setservo(self._databuf['servobuf'])

    def referencewait(self):
        """Reference unreferenced axes if according option has been provided and wait on completion."""
        PIDebug('GCS2DeviceStartup.referencewait()')
        if not self.refmodes or self.prop['skipref']:
            return
        self._databuf['servobuf'] = self._pitools.getservo(self._pidevice.axes)
        toreference = {}  # {cmd: [axes]}
        for i, refmode in enumerate(self._refmodes[:self._pidevice.numaxes]):
            if not refmode:
                continue
            axis = self._pidevice.axes[i]
            refmode = refmode.upper()
            if refmode not in toreference:
                toreference[refmode] = []
            if self._isreferenced(refmode, axis):
                PIDebug('axis %r is already referenced by %r', axis, refmode)
            else:
                toreference[refmode].append(self._pidevice.axes[i])
        waitonaxes = []
        for refmode, axes in toreference.items():
            if not axes:
                continue
            if refmode == 'POS':
                self._ref_with_pos(axes)
            elif refmode == 'ATZ':
                self._autozero(axes)
            else:
                self._ref_with_refcmd(axes, refmode)
                waitonaxes += axes
        self._pitools.waitonreferencing(axes=waitonaxes, **self._kwargs)

    def _isreferenced(self, refmode, axis):
        """Check if 'axis' has already been referenced with 'refmode'.
        @param refmode : Mode of referencing as string, e.g. POS, ATZ, FRF.
        @param axis : Name of axis to check as string.
        @return : False if 'axis' is not referenced or must be referenced.
        """
        if self.prop['forceref']:
            return False
        if refmode in ('POS',):
            return False
        if refmode == 'ATZ':
            return self._pidevice.qATZ(axis)[axis]
        if refmode == 'REF':
            return self._pidevice.qREF(axis)[axis]
        return self._pidevice.qFRF(axis)[axis]

    def _ref_with_refcmd(self, axes, refmode):
        """Enable RON, change servo state if appropriate and reference 'axes' with the 'refmode' command.
        @param axes : Axes to reference as list or tuple of strings, must not be empty.
        @param refmode : Name of command to use for referencing as string.
        """
        PIDebug('GCS2DeviceStartup._ref_with_refcmd(axes=%s, refmode=%s)', axes, refmode)
        for axis in axes:
            if self._pidevice.HasRON():
                try:
                    self._pidevice.RON(axis, True)
                except GCSError as exc:
                    if exc == gcserror.E34_PI_CNTR_CMD_NOT_ALLOWED_FOR_STAGE:
                        pass  # hexapod axis
                    else:
                        raise
            try:
                getattr(self._pidevice, refmode)(axis)
            except GCSError as exc:
                if exc == gcserror.E5_PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO:
                    self._databuf['servobuf'][axis] = self._pitools.getservo(axis)[axis]
                    self._pidevice.SVO(axis, not self._databuf['servobuf'][axis])
                    getattr(self._pidevice, refmode)(axis)
                else:
                    raise
            if self._pidevice.devname in ('C-843',):
                self._pitools.waitonreferencing(axes=axis, **self._kwargs)
            self._pitools.waitonready()

    def _autozero(self, axes):
        """Autozero 'axes' and move them to position "0.0".
        @param axes : Axes to autozero as list or tuple of strings, must not be empty.
        """
        PIDebug('GCS2DeviceStartup._autozero(axes=%s)', axes)
        self._pidevice.ATZ(axes, ['NaN'] * len(axes))
        self._pitools.waitonautozero(axes, **self._kwargs)
        self._pitools.setservo(axes, [True] * len(axes), **self._kwargs)
        self._pitools.moveandwait(axes, [0.0] * len(axes), **self._kwargs)

    def _ref_with_pos(self, axes):
        """Set RON accordingly and reference 'axes' with the POS command to position "0.0".
        @param axes : Axes to reference as list or tuple of strings, must not be empty.
        """
        PIDebug('GCS2DeviceStartup._ref_with_pos(axes=%s)', axes)
        assert self._pidevice.HasPOS(), 'controller does not support the POS command'
        self._pidevice.RON(axes, [False] * len(axes))
        self._pidevice.POS(axes, [0.0] * len(axes))
        self._pitools.waitonready(**self._kwargs)
        self._pidevice.SVO(axes, [True] * len(axes))  # A following qONT will fail if servo is disabled.

    def enableaxes(self):
        """Enable all connected axes if appropriate."""
        PIDebug('GCS2DeviceStartup.enableaxes()')
        if not self._pidevice.HasEAX() or self.prop['skipeax']:
            return
        for axis in self._pidevice.axes:
            try:
                self._pidevice.EAX(axis, True)
            except GCSError as exc:
                if exc != gcserror.E2_PI_CNTR_UNKNOWN_COMMAND:
                    raise
        self._pitools.waitonready(**self._kwargs)


class GCS2Tools(GCSBaseTools):  # Too  public methods pylint: disable=R0903
    """
    Provides a PI tool collection
    """
    def __init__(self, pidevice):
        """Provide a "ready to use" PI device.
        @type pidevice : pipython.gcscommands.GCS2Commands
        """
        if not isdeviceavailable([GCS2Commands, ], pidevice.gcscommands):
            raise TypeError('Type %s of pidevice is not supported!' % type(pidevice).__name__)

        super().__init__(pidevice,)

    def startup(self, stages=None, refmodes=None, servostates=True, _controlmodes=None, **kwargs):
        assert not isinstance(stages, tuple), 'argument "stages" must not to be of type "tuple"'
        assert not isinstance(refmodes, tuple), 'argument "refmodes" must not to be of type "tuple"'
        devstartup = GCS2DeviceStartup(self, **kwargs)

        devstartup.stages = stages
        devstartup.refmodes = refmodes
        devstartup.servostates = servostates
        devstartup.run()
        return devstartup


    def writewavepoints(self, wavetable, wavepoints, bunchsize=None):
        """Write 'wavepoints' for 'wavetable' in bunches of 'bunchsize'.
        The 'bunchsize' is device specific. Please refer to the controller manual.
        @param wavetable : Wave table ID as integer.
        @param wavepoints : Single wavepoint as float convertible or list/tuple of them.
        @param bunchsize : Number of wavepoints in a single bunch or None to send all 'wavepoints' in a single bunch.
        """
        wavepoints = wavepoints if isinstance(wavepoints, (list, set, tuple)) else [wavepoints]
        if bunchsize is None:
            bunchsize = len(wavepoints)
        for startindex in range(0, len(wavepoints), bunchsize):
            bunch = wavepoints[startindex:startindex + bunchsize]
            self._pidevice.WAV_PNT(table=wavetable, firstpoint=startindex + 1, numpoints=len(bunch),
                                   append='&' if startindex else 'X', wavepoint=bunch)


    # Too many arguments (6/5) pylint: disable=R0913
    def waitonfastalign(self, name=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until all 'axes' are on target.
        @param name : Name of the process as string or list/tuple.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param postdelay : Additional delay time in seconds as float after reaching desired state.
        @param polldelay : Delay time between polls in seconds as float.
        """
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        maxtime = time() + timeout
        while any(list(self._pidevice.qFRP(name).values())):
            if time() > maxtime:
                raise SystemError('waitonfastalign() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        sleep(postdelay)


    # Too many arguments (6/5) pylint: disable=R0913
    def waitonwavegen(self, wavegens=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until all 'axes' are on target.
        @param wavegens : Integer convertible or list/tuple of them or None.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param postdelay : Additional delay time in seconds as float after reaching desired state.
        @param polldelay : Delay time between polls in seconds as float.
        """
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        maxtime = time() + timeout
        while any(list(self._pidevice.IsGeneratorRunning(wavegens).values())):
            if time() > maxtime:
                raise SystemError('waitonwavegen() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        sleep(postdelay)


    # Too many arguments (6/5) pylint: disable=R0913
    def waitonautozero(self, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until all 'axes' are on target.
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
        maxtime = time() + timeout
        while not all(list(self._pidevice.qATZ(axes).values())):
            if time() > maxtime:
                raise SystemError('waitonautozero() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        sleep(postdelay)


    # Too many arguments pylint: disable=R0913
    def waitonphase(self, axes=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until all 'axes' are on phase.
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
        maxtime = time() + timeout
        while not all(x > -1.0 for x in self._pidevice.qFPH(axes).values()):
            if time() > maxtime:
                raise SystemError('waitonphase() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        sleep(postdelay)


    # Too many arguments pylint: disable=R0913
    def waitonwalk(self, channels, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until qOSN for channels is zero.
        @param channels : Channel or list or tuple of channels to wait for motion to finish.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param postdelay : Additional delay time in seconds as float after reaching desired state.
        @param polldelay : Delay time between polls in seconds as float.
        """
        channels = channels if isinstance(channels, (list, set, tuple)) else [channels]
        if not channels:
            return
        maxtime = time() + timeout
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        while not all(list(x == 0 for x in list(self._pidevice.qOSN(channels).values()))):
            if time() > maxtime:
                self.stopall()
                raise SystemError('waitonwalk() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        sleep(postdelay)


    # Too many arguments pylint: disable=R0913
    def waitonoma(self, axes=None, timeout=300, predelay=0, polldelay=0.1):
        """Wait on the end of an open loop motion of 'axes'.
        @param axes : Axis as string or list/tuple of them to get values for or None to query all axes.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param polldelay : Delay time between polls in seconds as float.
        """
        axes = self.getaxeslist(axes)
        if not axes:
            return
        numsamples = 5
        positions = []
        maxtime = time() + timeout
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        while True:
            positions.append(list(self._pidevice.qPOS(axes).values()))
            positions = positions[-numsamples:]
            if len(positions) < numsamples:
                continue
            isontarget = True
            for vals in zip(*positions):
                isontarget &= sum([abs(vals[i] - vals[i + 1]) for i in range(len(vals) - 1)]) < 0.01
            if isontarget:
                return
            if time() > maxtime:
                self.stopall()
                raise SystemError('waitonoma() timed out after %.1f seconds' % timeout)
            sleep(polldelay)


    # Too many arguments pylint: disable=R0913
    def waitontrajectory(self, trajectories=None, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
        """Wait until all 'trajectories' are done and all axes are on target.
        @param trajectories : Integer convertible or list/tuple of them or None for all trajectories.
        @param timeout : Timeout in seconds as floatfor trajectory and motion.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param postdelay : Additional delay time in seconds as float after reaching desired state.
        @param polldelay : Delay time between polls in seconds as float.
        """
        maxtime = time() + timeout
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        while any(list(self._pidevice.qTGL(trajectories).values())):
            if time() > maxtime:
                self.stopall()
                raise SystemError('waitontrajectory() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        self.waitontarget(timeout=timeout, predelay=0, postdelay=postdelay, polldelay=polldelay)


    def waitonmacro(self, timeout=300, predelay=0, polldelay=0.1):
        """Wait until all macros are finished, then query and raise macro error.
        @param timeout : Timeout in seconds as float.
        @param predelay : Time in seconds as float until querying any state from controller.
        @param polldelay : Delay time between polls in seconds as float.
        """
        maxtime = time() + timeout
        self.waitonready(timeout=timeout, predelay=predelay, polldelay=polldelay)
        assert self._pidevice.HasqRMC() or self._pidevice.HasIsRunningMacro(), 'device does not support wait on macro'
        while True:
            if self._pidevice.HasqRMC() and not self._pidevice.qRMC().strip():
                break
            if self._pidevice.HasIsRunningMacro() and not self._pidevice.IsRunningMacro():
                break
            if time() > maxtime:
                self.stopall()
                raise SystemError('waitonmacro() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        if self._pidevice.HasMAC_qERR():
            errmsg = self._pidevice.MAC_qERR().strip()
            if errmsg and int(errmsg.split('=')[1].split()[0]) != 0:
                raise GCSError(gcserror.E1012_PI_CNTR_ERROR_IN_MACRO, message=errmsg)

    def getmaxtravelrange(self, axis):
        """Returns the maximum travel range of one axis
        @param axis : Axis to get the value for.
        @return : Dictionary of the maximum travel range and the Axis.
        """
        return self._pidevice.qTMX(axis)

    def getmintravelrange(self, axis):
        """Returns the minimum travel range of one axis
        @param axis : Axis to get the value for.
        @return : Dictionary of the minimum travel range and the Axis.
        """
        return self._pidevice.qTMN(axis)

    def _move_to_middle(self, axes):
        rangemin = self._pidevice.qTMN(axes)
        rangemax = self._pidevice.qTMX(axes)
        targets = {}
        for axis in axes:
            targets[axis] = rangemin[axis] + (rangemax[axis] - rangemin[axis]) / 2.0
        self._pidevice.MOV(targets)


    def _get_servo_state(self, axes):
        if self._pidevice.HasqSVO():
            return self._pidevice.qSVO(axes)

        return dict(list(zip(axes, [False] * len(axes))))

    def _get_closed_loop_on_target(self, axes, throwonaxiserror=False):
        isontarget = {}
        if self._pidevice.HasqONT():
            isontarget.update(self._pidevice.qONT(axes))
        elif self._pidevice.HasIsMoving():
            ismoving = self._pidevice.IsMoving(axes).values()
            isontarget.update(dict(list(zip(axes, [not x for x in ismoving]))))
        return isontarget


    def _get_open_loop_on_target(self, axes):
        isontarget = {}
        if self._pidevice.HasqOSN():
            stepsleft = self._pidevice.qOSN(axes).values()
            isontarget.update(dict(list(zip(axes, [x == 0 for x in stepsleft]))))
        else:
            isontarget.update(dict(list(zip(axes, [True] * len(axes)))))
        return isontarget

    # Too many arguments pylint: disable=R0913
    def _wait_to_the_end_of_reference(self, axes, timeout, polldelay):
        maxtime = time() + timeout
        if self._pidevice.devname in ('C-843',):
            self._pidevice.errcheck = False
        while not all(list(self._pidevice.qFRF(axes).values())):
            if time() > maxtime:
                self.stopall()
                raise SystemError('waitonreferencing() timed out after %.1f seconds' % timeout)
            sleep(polldelay)
        if self._pidevice.devname in ('C-843',):
            self._pidevice.errcheck = True


    def _enable_axes(self, axes):
        for axis in axes:
            try:
                self._pidevice.EAX(axis, True)
            except GCSError as exc:
                if exc == gcserror.E2_PI_CNTR_UNKNOWN_COMMAND:
                    pass  # C-885
                else:
                    raise
