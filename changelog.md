# Feature Version History



### PIPython 2.4.0
- add GCSCommands.qUSG()
- add GCSCommands.SPV()
- add GCSCommands.qSPV()
- add GCSCommands.CPA()
- add GCSCommands.UCL()
- add GCSCommands.qUCL()
- add GCSCommands.REC_STAT()
- add GCSCommands.qREC_STAT()
- add GCSCommands.REC_TRACE()
- add GCSCommands.qREC_TRACE()
- add GCSCommands.REC_TRG()
- add GCSCommands.qREC_TRG()
- add GCSCommands.REC_RATE()
- add GCSCommands.qREC_RATE()
- add GCSCommands.REC_START()
- add GCSCommands.REC_STOP()
- add GCSCommands.qREC_NUM()
- add GCSCommands.qREC_DAT()
- add GCSCommands.qLOG()


### PIPython 2.3.0
- Internal refactoring


### PIPython 2.2.2
- fix: No module named gcs21.gcs21commands_helpers


### PIPython 2.2.1
- fix missing argument in isgcs21


### PIPython 2.2.0
- Support for PI_SetConnectTimeout() and PI_EnableBaudRateScan()


### PIPython 2.1.1
- fix timing probles while reading the data recorder with pythom3


### PIPython 2.1.0
- pipython.datarectools.Datarecorder: maxnumvalues now also reads the maximum number 
  of data recorder points from the 'HDR?' answer.
- fix pipython.pitools.pitoopls.itemstostr. If 'data' is an integer of 0 or a float of 0.0 
  'itemstostr' now returns the string '0' or '0.0' instead of 'None'


### PIPython 2.0.0
- New package structure
- support for WriteConfigurationFromDatabaseToControllerAndSave()


### PIPython 1.5.2
- Linux: fix string decoding in piusb


### PIPython 1.5.1
- fix parameter value conversion of hex parameter values


### PIPython 1.5.0
- add GCSCommands.POL()
- add GCSCommands.STD()
- add GCSCommands.RTD()
- add GCSCommands.qRTD()
- add GCSCommands.qLST()
- add GCSCommands.DTL()


### PIPython 1.4.0

- fix string decoding in GCSDll()
- add pitools.getservo()
- pitools.waitonreferencing() does not call waitontarget()
- in pitools call waitonready() with the "polldelay" argument
- fix signature of GCSCommands.qTWS()
- GCSCommands.CCL() will reset the list of supported GCS commands
- interfaces.pisocket.PISocket() uses socket.TCP_NODELAY
- add "ATZ" as "referencing command" to pitools.DeviceStartup()
- add GCSMessages.logfile property
- rename license.md to eula.md
- add datarectools.get_hdr_options()
- add Datarecorder.recopts property
- add Datarecorder.trigopts property
- all timeout default values are set to 300 seconds


### PIPython 1.3.9

- add pitools.waitonmacro()
- catch GCS error 2 (unknown command) after EAX during startup
- GCS commands arguments can be sets, too
- DDL(tables, offsets, values) -> DDL(table, offsets, values)
- add GCSDevice.isavailable
- convert parameter values according to types in qHPA answer
- fix signature of GCSCommands.qJLT()


### PIPython 1.3.8

- add interfaces.piusb
- add pitools.readgcsarray()
- add pitools.waitonwavegen()
- add pitools.moveandwait()
- add piparams.applyconfig()
- pitools.startup() defines and references stages only if necessary
- add GCSCommands.allaxes
- add GCSDevice.hasref()
- add GCSDevice.haslim()
- add GCSDevice.canfrf()
- add GCSDevice.canfnl()
- add GCSDevice.canfpl()
- add pitools.waitonphase()
- add pitools.setservo()
- controller specific startup sequence


### PIPython 1.3.7

- add pitools.movetomiddle()
- add pipython.fastaligntools
- PI_GCS2_DLL is used by default
- add pitools.savegcsarray()
- add pitools.itemstostr()


### PIPython 1.3.6

- add controller C-886, E-872
- GCSDevice supports external Gateway


### PIPython 1.3.5

- add DLL functions for PIStages3
- "wait on" functions support polldelay times
- fix GCSCommands.SGA()
- fix GCSCommands.qSPA()
- fix GCSCommands.qSEP()
- add optional argument "noraise" for StopAll(), HLT(), STP()
- add pitools.waitonfastalign()
- add pitools.waitonautozero()
- add GCS Error codes


### PIPython 1.3.4

- add pipython.interfaces.piserial
- "wait on" functions support predelay and postdelay times
- add GCSCommands.TSP()
- setup writes key for PIUpdateFinder always into 32 bit part of registry
- change formatting of numbers in GCS strings
- GCSDll supports "K" devices
- GCSMessages.bufstate will not write to log
- rename ReadGCSData() -> read_gcsdata()
- add controller C-663.12
- add parameters for E-873.3QTU, C-663.10C885
- add GCS Error codes
- bugfixing


### PIPython 1.3.3

- add GCSCommands.SGP()
- add GCSCommands.qSGP()
- add GCSCommands.WAV_SIN()
- add GCSCommands.WAV_POL()
- add GCSCommands.WAV_TAN()
- add GCSCommands.WAV_SWEEP()
- add GCSCommands.checkerror()
- add GCSCommands.DEL()
- add new controllers
- add controller parameters
- fix for handling unicode in Python 3
- bugfixing of some GCS commands


### PIPython 1.3.2

- add GCSCommands.FSF()
- add GCSCommands.qFSF()
- add GCSCommands.qFSR()
- add pitools.getaxeslist()
- add pitools.ontarget()
- add pitools.waitonwalk()
- add pitools.waitonoma()
- add pitools.waitontrajectory()
- fix DLL function prefix
