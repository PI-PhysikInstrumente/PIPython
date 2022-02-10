# PIPython

PIPython is a collection of Python modules to access a PI device and process
GCS data. It can be used with Python 3.6+ on Windows, Linux and OS X
and without the GCS DLL also on any other platform.

## Installation

By using PIPython you agree to the license agreement, see the provided file:

    eula.md

### From local folder 

Unzip the file PIPython.zip, open a command entry (Linux Console or Windows CMD window) and run:

    python setup.py install

For further reading open the *index.html* file in your browser and see the samples in the
*samples* folder.

### From GitHub

[PIPython on GitHub](https://github.com/PI-PhysikInstrumente/PIPython)

    git clone git@github.com:PI-PhysikInstrumente/PIPython.git
    python setup.py install

### From pypi.org

    pip install PIPython    

### Feedback 

We appreciate your feedback at:

    service@pi.de

## Quickstart

Communicate to a PI device via `GCSDevice` which wraps the GCS DLL functions
and provides methods to connect to the device. Call `GCSDevice` with the
controller name as argument.

~~~python
from pipython import GCSDevice
pidevice = GCSDevice('C-884')
pidevice.InterfaceSetupDlg()
print pidevice.qIDN()
pidevice.CloseConnection()
~~~

`GCSDevice` is a context manager which closes the connection if an exception
raises inside the `with` statement.

~~~python
from pipython import GCSDevice
with GCSDevice('C-884') as pidevice:
    pidevice.InterfaceSetupDlg()
    print(pidevice.qIDN())
~~~

See also the provided samples in the `samples` subdirectory. Start with `quickstart.py`.



## Requirements

Download these python packages with pip install:

- PyUSB
- PySocket
- PySerial

With pipython.interfaces.piusb you can connect a USB device without using the GCS DLL.
This works only with Linux and requires LibUSB which usually is provided by the OS.



## Arguments

From now on `pidevice` refers to a connected `GCSDevice` instance.


### Setter functions

Usually you can call a setter function with
- a dictionary of axes/channels and values
- a list for axes/channels and a list of the values
- a single item for axis/channel and a single value

~~~python
gcs.MOV({'X': 1.23, 'Y': 2.34})
gcs.MOV(['X', 'Y'], [1.23, 2.34])
gcs.MOV('X', 1.23)
~~~

For channels and numeric axis names you can omit the quotes.

~~~python
gcs.MOV({1: 1.23, 2: 2.34})
gcs.MOV([1, 2], [1.23, 2.34])
gcs.MOV(1, 1.23)
~~~


### Getter functions

#### GCS 2.0

Usually getter commands can be called with

- a list of axes/channels.
- a single item for axis/channel, without quotes if numeric
- without any arguments which will return the answer for all available axes/channels

~~~python
gcs.qPOS(['X', 'Y'])
gcs.qPOS('X')
gcs.qPOS(1)
gcs.qPOS()
~~~


#### GCS 3.0

Usually getter commands can be called with

- a single axis
- without any arguments which will return the answer for all available axes

~~~python
gcs.qPOS('AXIS_1')
gcs.qPOS()
~~~

## Return values

Axes or channel related answers are returned as (ordered) dictionary.

~~~python
pidevice.qPOS()
>>>{'X': 1.23, 'Y': 2.34}
~~~


If you do not provide arguments you always have to use strings as keys.

~~~python
pos = pidevice.qPOS()
print(pos['1'])
~~~

The following sample will move all `axes` to `targets` and waits until the motion has finished.
It shows how to use only the values from the returned dictionary.

~~~python
from time import sleep
...
pidevice.MOV(axes, targets)
while not all(list(pidevice.qONT(axes).values())):
    sleep(0.1)
~~~

#### GCS 2.0

If you provide arguments their types are preserved and you can use these as keys.

~~~python
pos = pidevice.qPOS([1, 2, 3])
print(pos[1])
~~~

#### GCS 3.0

If you provide arguments their types are preserved and you can use these as keys.

~~~python
pos = pidevice.qPOS('AXIS_1') # only one axis is possible
print(pos['AXIS_1'])
~~~


## Some hints...


### Helpers

In `pipython.pitools` you will find some helper funtions for your convenience. See the provided
samples for how to use them. The sample above can then be written as:

~~~python
from pipython import pitools
...
pidevice.MOV(axes, targets)
pitools.waitontarget(pidevice, axes)
~~~


### Enable debug logging

To log debug messages on the console just enter these lines prior to calling `GCSDevice`.

~~~python
from pipython import PILogger, DEBUG, INFO, WARNING, ERROR, CRITICAL

PILogger.setLevel(DEBUG)
~~~


### GCSError and error check

By default an "ERR?" command is sent after each command to query if an error
occurred on the device which then will be raised as `GCSError` exception. If communication
speed is an issue you can disable error checking.

~~~python
pidevice.errcheck = False
~~~

To handle a catched `GCSError` exception you can use the defines provided by
`gcserror` instead of pure numeric values. Remember the difference between `GCSError` which
is the exception class and `gcserror` which is the according module.

~~~python
from pipython import GCSDevice, GCSError, gcserror
with GCSDevice('C-884') as pidevice:
    try:
        pidevice.MOV('X', 1.23)
    except GCSError as exc:
        if exc == gcserror.E_1024_PI_MOTION_ERROR:
            print('There was a motion error, please check the mechanics.')
        else:
            raise
~~~

The exception class `GCSError` will translate the error code into a readable message.

~~~python
from pipython import GCSError, gcserror
raise GCSError(gcserror.E_1024_PI_MOTION_ERROR)
>>>GCSError: Motion error: position error too large, servo is switched off automatically (-1024)
~~~

#### GCS 3.0

- to reset the error state of 1 or more axes 
~~~python
for axis in device.axes:
    if axis_has_error(device):
        while check_axis_status_bit(device, axis, AXIS_STATUS_FAULT_REACTION_ACTIVE):
            pass
        print('reset axis error: ', axis)
        device.RES(axis)
~~~


### Big data

Commands like `qDRR()` for GCS 2.0 syntax, or `qREC_DAT()` for GCS 3.0 syntax
which read a large amount of GCS data return immediately with
the header dictionary containing information about the data. Then they will start
a background task that carries on reading data from the device into an internal buffer. The
`bufstate` property returns the progress of the reading as floating point number in the range
0 to 1 and turns to `True` when reading has finished. Hence, when using it in a loop check for
`is not True`. (Remember, this is not the same as `!= True`.)

#### GCS 2.0

~~~python
header = pidevice.qDRR(1, 1, 8192)
while pidevice.bufstate is not True:
    print('read data {:.1f}%...'.format(pidevice.bufstate * 100))
    sleep(0.1)
data = pidevice.bufdata
~~~

#### GCS 3.0

~~~python
header = pidevice.qREC_DAT('REC_1', 'ASCII', 1, 1, 8192)
while pidevice.bufstate is not True:
    print('read data {:.1f}%...'.format(pidevice.bufstate * 100))
    sleep(0.1)
data = pidevice.bufdata
~~~


### Textual interface

Besides the functions implemented in GCSCommands you can send GCS commands as strings to the
controller. Use `read()` for commands returning an answer, `read_gcsdata()` for commands returning
GCS data and `send()` for non-answering commands.

~~~python
print(pidevice.read('POS?'))
print(pidevice.read_gcsdata('DRR? 1 100 1'))
pidevice.send('MOV X 1.23')
~~~

They return the raw string or GCS data from the controller. If `errorcheck` is enabled the
error state is queried from the device automatically. We recommend to use the provided
functions instead of sending raw strings.

In line with the C++ GCS DLL the functions `ReadGCSCommand()` and `GcsCommandset()` are also
available. They will never query an error from the device.

~~~python
print(pidevice.ReadGCSCommand('POS?'))
pidevice.GcsCommandset('MOV X 1.23')
~~~
