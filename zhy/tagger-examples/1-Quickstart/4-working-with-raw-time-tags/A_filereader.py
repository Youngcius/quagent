"""The FileReader allows you to read data from files that have been stored by the FileWriter.
With the FileReader, you get access to the raw time tags which you can use for whatever you
want. If you want to use the highly efficient measurement classes provided by the API, however,
the Virtual Time Tagger (example 3-B) will be the better choice.
In this example, we first use the FileWriter to store test signal data for one second. In the
second part, we will use the FileReader to load the time tags from the ttbin file."""

import sys
if sys.version_info.major >= 3:
    import tempfile
else:
    from backports import tempfile
from time import sleep
import os
import TimeTagger

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Enable the test signal on channels 1 and 2
tagger.setTestSignal([1, 2], True)

# The FileWriter provides a temporary ttbin file for the example
tempdir = tempfile.TemporaryDirectory()
filename = tempdir.name + os.sep + "filewriter.ttbin"
filewriter = TimeTagger.FileWriter(tagger=tagger,
                                   filename=filename,
                                   channels=[1, 2])
sleep(1)
filewriter.stop()
del filewriter
print("\nFileWriter has prepared a ttbin file.")

# To read the data form the temporary file, we create a FileReader object
filereader = TimeTagger.FileReader(filename)

print('\nRead back the dumped stream from the filesystem using FileReader.\n')
input("-> Press Enter to show some selected time tags")

# The format for the table and the head of the table
format_string = '{:>8} | {:>17} | {:>7} | {:>14} | {:>13}'
print(format_string.format('TAG #', 'EVENT TYPE', 'CHANNEL', 'TIMESTAMP (ps)', 'MISSED EVENTS'))
print('---------+-------------------+---------+----------------+--------------')

n_events = 100000  # Number of events to read at once
event_name = ['0 (TimeTag)', '1 (Error)', '2 (OverflowBegin)', '3 (OverflowEnd)', '4 (MissedEvents)']
i = 0
while filereader.hasData():
    # getData() does not return timestamps, but an instance of TimeTagStreamBuffer
    # that contains more information than just the timestamp
    data = filereader.getData(n_events=n_events)

    # With the following methods, we can retrieve a numpy array for the particular information:
    channel = data.getChannels()            # The channel numbers
    timestamps = data.getTimestamps()       # The timestamps in ps
    overflow_types = data.getEventTypes()   # TimeTag = 0, Error = 1, OverflowBegin = 2, OverflowEnd = 3, MissedEvents = 4
    missed_events = data.getMissedEvents()  # The numbers of missed events in case of overflow

    # Output to table
    if i < 2 or not filereader.hasData():
        print(format_string.format(*" "*5))
        heading = ' Start of data chunk {} with {} events '.format(i+1, data.size)
        extra_width = 69 - len(heading)
        print('{} {} {}'.format("="*(extra_width//2), heading, "="*(extra_width - extra_width//2)))
        print(format_string.format(*" "*5))
        print(format_string.format(i*n_events + 1, event_name[overflow_types[0]], channel[0], timestamps[0], missed_events[0]))
        if data.size > 1:
            print(format_string.format(i*n_events + 2, event_name[overflow_types[1]], channel[1], timestamps[1], missed_events[1]))
        if data.size > 3:
            print(format_string.format(*["..."]*5))
        if data.size > 2:
            print(format_string.format(i*n_events + data.size, event_name[overflow_types[-1]], channel[-1], timestamps[-1], missed_events[-1]))
    if i == 1:
        print(format_string.format(*" "*5))
        for j in range(3):
            print(format_string.format(*"."*5))
    i += 1

# Close the FileReader and remove the temporary files
del filereader
tempdir.cleanup()
