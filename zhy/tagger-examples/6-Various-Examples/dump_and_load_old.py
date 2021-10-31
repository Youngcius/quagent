"""
Please note that the Dump measurement is deprecated and will be removed in
future versions of the Time Tagger software. 
Please use FileWriter and FileReader instead.
"""

import tempfile
import os
from time import sleep
import numpy as np

from TimeTagger import createTimeTagger, Dump

# create a timetagger instance
tagger = createTimeTagger()

print("*******************************************************")
print("*** Demonstrate how to dump the raw time tag stream ***")
print("*******************************************************")
print("")
print("Enabling test signal on channel 1 and 2.")
print("Frequency channel 1: ~800 kHz")
tagger.setTestSignal(1, True)
print("Frequency channel 2: ~800/2 kHz")
tagger.setTestSignal(2, True)
tagger.setEventDivider(2, 2)

print("")
tempdir = tempfile.gettempdir()
tmpfile = tempdir + os.sep + 'dump.tt'
print("1: Dump the data to " + tmpfile)
channels = [1, 2]
# The number of maximum tags which should be dumped is limited only by the size of your storage device.
# Required space: tags * 16 byte
maximum_tags = 10**6
dump = Dump(tagger, tmpfile, maximum_tags, channels)
sleep(1)
print("Stop dumping and close the file.")
# by removing the measurement the output file is closed the dump stops
del dump
print("")
print("2: Load the data from " + tmpfile)
# This is a representation of the struct Tag from TimeTagger.h
tagformat = np.dtype([
    # TimeTag = 0, Error = 1, OverflowBegin = 2, OverflowEnd = 3, MissedEvents = 4
    ('type',          'u1'),
    # ('reserved',      'i1'),
    ('missed_events', '<u2'),
    ('channel',       '<i4'),
    ('time',          '<i8'),
], align=True)
data = np.fromfile(tmpfile, dtype=tagformat)
print("Show the first 15 tags dumped:")
print("type, missed_events, channel, time (ps)")
for tag in data[:15]:
    print(tag)

print("Total amount of events per channel:")
timetag_events = data['type'] == 0
missed_events = data['type'] == 4
for c in channels:
    coresponding_events = data['channel'] == c
    total_timetag_events = sum(timetag_events & coresponding_events)
    total_missed_events = sum(
        data['missed_events'][missed_events & coresponding_events])
    total_events = total_timetag_events + total_missed_events
    print("  channel %d: %d events" % (c, total_events))

print("")
print("Delete dump file.")
os.remove(tmpfile)
