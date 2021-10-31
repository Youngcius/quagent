"""The TimeTagStream measurement class"""

import TimeTagger

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Enable the test signal on channels 1 and 2
tagger.setTestSignal([1, 2], True)

stream = TimeTagger.TimeTagStream(tagger=tagger,
                                  n_max_events=1000000,
                                  channels=[1, 2])

format_string = '{:>8} | {:>17} | {:>7} | {:>14} | {:>13}'
print(format_string.format('TAG #', 'EVENT TYPE', 'CHANNEL', 'TIMESTAMP (ps)', 'MISSED EVENTS'))
print('---------+-------------------+---------+----------------+--------------')
event_name = ['0 (TimeTag)', '1 (Error)', '2 (OverflowBegin)', '3 (OverflowEnd)', '4 (MissedEvents)']

stream.startFor(int(5E11))
event_counter = 0
chunk_counter = 1
while stream.isRunning():
    # getData() does not return timestamps, but an instance of TimeTagStreamBuffer
    # that contains more information than just the timestamp
    data = stream.getData()

    if data.size:
        # With the following methods, we can retrieve a numpy array for the particular information:
        channel = data.getChannels()            # The channel numbers
        timestamps = data.getTimestamps()       # The timestamps in ps
        overflow_types = data.getEventTypes()   # TimeTag = 0, Error = 1, OverflowBegin = 2, OverflowEnd = 3, MissedEvents = 4
        missed_events = data.getMissedEvents()  # The numbers of missed events in case of overflow

        print(format_string.format(*" "*5))
        heading = ' Start of data chunk {} with {} events '.format(chunk_counter, data.size)
        extra_width = 69 - len(heading)
        print('{} {} {}'.format("="*(extra_width//2), heading, "="*(extra_width - extra_width//2)))
        print(format_string.format(*" "*5))

        print(format_string.format(event_counter + 1, event_name[overflow_types[0]], channel[0], timestamps[0], missed_events[0]))
        if data.size > 1:
            print(format_string.format(event_counter + 1, event_name[overflow_types[1]], channel[1], timestamps[1], missed_events[1]))
        if data.size > 3:
            print(format_string.format(*["..."]*5))
        if data.size > 2:
            print(format_string.format(event_counter + data.size, event_name[overflow_types[-1]], channel[-1], timestamps[-1], missed_events[-1]))

        event_counter += data.size
        chunk_counter += 1
