#!/usr/bin/python
# -*- coding: utf-8 -*-

from pipython.pidevice.gcscommands import GCSCommands
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.interfaces.pisocket import PISocket
from pipython.pidevice.interfaces.piusb import PIUSB

__signature__ = 0xc2c1a0a44938c888c9ce69d225bc7c82


# TCP/IP Connect
# >>>>>>>>>>>>>>>>>>>>>
gateway = PISocket(host='192.168.90.116')
# <<<<<<<<<<<<<<<<<<<<<

# USB Connect
# >>>>>>>>>>>>>>>>>>>>>
#gateway = PIUSB()
#gateway.connect('987654321', 0x1024)
# <<<<<<<<<<<<<<<<<<<<<

messages = GCSMessages(gateway)
gcs = GCSCommands(messages)


#######################
# C-885 Motion Master #
#######################

# To Communicate with the C-885 motion master it is possible to use the GCS-Python functions or
# to send a GCS String

# PIPython function
print(gcs.qIDN())
# answer e.g:
# '(c)2015 - 2018 Physik Instrumente (PI) GmbH & Co. KG, C-885.M1 TCP-IP Master,987654321,1.0.1.0'

# GCS String
print(gcs.read('*IDN?'))
# answer e.g:
# '(c)2015 - 2018 Physik Instrumente (PI) GmbH & Co. KG, C-885.M1 TCP-IP Master,987654321,1.0.1.0'


# The identifiers of all axes in the system are unique. Call 'SAI?' to find out which identifiers are valid
axes_of_master = gcs.qSAI()
# answer e.g:
# 1
# 3

print(gcs.qPOS(axes_of_master))
# answer e.g:
# 1=-0.0004680
# 3=-2.2942890



##################################
# Sub module (e.g. E-873.10C855) #
##################################

# To Communicate with a sub module (e.g. E-87210C855) it is only possible to ust the GCS-Strings
# The address of the sub module has to precede the GCS command.
# In the answer you will find a preceding '0' and the number of the sub module form where the answer
# comes from.
print(gcs.read('2 *IDN?'))
# answer e.g:
# '0 2 (c)2016 Physik Instrumente (PI) GmbH & Co. KG, E-873.10C885, 117007101, 02.016'


# The identifier of the axes in a sub module are relative to the sub module. This means the identifiers of the axes
# are not the same as the identifiers of the axis at the C-855 motion module, even if they are physically
# the same. To find out the identifiers of the axis in a sub module call e.g. '2 SAI?'

axes_of_sub_module_2 = gcs.read('2 SAI?').split(' ')[2].replace('\n' , '')
# answer e.g:
# 0 2 X
# This means the identifier of the axis of the sub module is 'X' and not '1' as it is when commanding the motion master

axes_of_sub_module_3 = gcs.read('3 SAI?').split(' ')[2].replace('\n' , '')
# answer e.g:
# 0 3 X
# This means the identifier of the axis of the sub module is 'X' and not '3' as it is when commanding the motion master

# The following commands are reading the position form the same physically axes as the
# C-855 motion master sample above (gcs.read('POS? 1 3')).

print(gcs.read('2 POS? %s' % axes_of_sub_module_2))
# answer e.g:
# 0 2 X=-0.0004680

print(gcs.read('3 POS? %s' % axes_of_sub_module_3))
# answer e.g:
# 0 3 X=-2.2942890



#For Linear Stage Q-545
#1. Home Macros will turn on servo, find reference position, define home position, search forward limit switch,
# then reverse limit switch, then move to home position, report error code

# The Command HIN is not supported by the controller
gcs.send('2 SVO %s 1' % axes_of_sub_module_2)

gcs.send('2 FRF %s' % axes_of_sub_module_2)
ontarget=0
while not ontarget:
    ontarget=int(gcs.read('2 ONT? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , ''))

gcs.send('2 DFH %s' % axes_of_sub_module_2)

print(gcs.read('2 POS? %s' % axes_of_sub_module_2))

gcs.send('2 VEL %s 6.5' % axes_of_sub_module_2)

# The Command FPL is not supported by the controller. Call TMX and mov to the the returned position instead.
max_position= gcs.read('2 TMX? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , '')
gcs.send('2 MOV %s %s' % (axes_of_sub_module_2, max_position))
ontarget=0
while not ontarget:
    ontarget=int(gcs.read('2 ONT? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , ''))

print(gcs.read('2 TMX? %s' % axes_of_sub_module_2))

# The Command FNL is not supported by the controller. Call TMN and mov to the the returned position instead.
min_position= gcs.read('2 TMN? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , '')
gcs.send('2 MOV %s %s' % (axes_of_sub_module_2, min_position))
ontarget=0
while not ontarget:
    ontarget=int(gcs.read('2 ONT? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , ''))

print(gcs.read('2 TMN? %s' % axes_of_sub_module_2))

gcs.send('2 GOH %s' % axes_of_sub_module_2)
ontarget=0
while not ontarget:
    ontarget=int(gcs.read('2 ONT? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , ''))

print(gcs.read('2 POS? %s' % axes_of_sub_module_2))

print(gcs.read('2 ERR?'))


#
#2.Move Macros is simple, Check the error status, current position, and move to target position and check
# the move status and report error code
#
print(gcs.read('2 ERR?'))
print(gcs.read('2 POS? %s' % axes_of_sub_module_2))

gcs.send('2 MOV %s 5' % axes_of_sub_module_2)
ontarget=0
while not ontarget:
    ontarget=int(gcs.read('2 ONT? %s' % axes_of_sub_module_2).split('=')[1].replace('\n' , ''))

print(gcs.read('2 POS? %s' % axes_of_sub_module_2))
print(gcs.read('2 ERR?'))



gateway.close()
