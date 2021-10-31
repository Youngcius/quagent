"""A custom implementation of Counter that also tracks overflows.
This custom measurement is used in example 2-E to check the overflows at low TestSignalDivider.
You can find another and even more detailed example for a CustomMeasurement in the
folder '4-Custom-Measurements' -> CustomStartStop.py"""

import matplotlib.pyplot as plt
import TimeTagger
import numpy as np
import numba


class CustomCounter(TimeTagger.CustomMeasurement):
    """
    A Counter Measurement that takes overflows into account.
    """

    def __init__(self, tagger, channels, binwidth, n_values):
        TimeTagger.CustomMeasurement.__init__(self, tagger)
        self.channels = np.array(channels)
        self.n_values = n_values
        self.binwidth = binwidth

        self.channel_dict = {channel: index for index, channel in enumerate(self.channels)}
        self.data = np.zeros([n_values + 1, len(channels)], dtype=np.int32)
        self.overflows = np.zeros(n_values + 1, dtype=bool)
        self.active_bin = np.zeros(len(channels))
        self.first_timestamp = 0
        self.last_bin_number = 0
        self.bin_index = 0
        self.next_edge = 0
        self.overflow_state = False

        # Each used channel must be registered
        for channel in channels:
            self.register_channel(channel)

        self.clear_impl()

        # At the end of a Measurement construction we must indicate that we
        # have finished
        self.finalize_init()

    def __del__(self):
        # The measurement must be stopped before deconstruction to avoid
        # concurrent measure() calls
        self.stop()

    def getData(self, exclude_overflows=False):
        # lock this instance to avoid conflicting results while measure is
        # running apart.
        self._lock()
        result = np.array(self.data, dtype=float)
        self._unlock()
        result *= 1E12 / self.binwidth
        if exclude_overflows:
            result[self.overflows, :] = np.nan
        # We have gathered the data, unlock so measuring can continue
        # return result
        return np.roll(result, -self.bin_index, axis=0)[1:]

    def getIndex(self):
        # this method does not depend on the internal state, so there is no
        # need for a lock
        arr = np.arange(0, self.n_values, dtype=np.int64) * self.binwidth
        return arr

    def clear_impl(self):
        # the lock is already aquired
        self.data[:, :] = 0
        self.overflows[:] = False
        self.bin_index = 0
        self.next_edge = 0
        self.overflow_state = False

    def on_start(self):
        # the lock is already aquired
        pass

    def on_stop(self):
        # the lock is already aquired
        pass

    @staticmethod
    @numba.jit(nopython=True, nogil=True)
    def fast_process(
            tags,
            channels,
            data,
            overflows,
            binwidth,
            n_values,
            bin_index,
            next_edge,
            overflow_state):
        """
        A recompiled version of the histogram algorithm for better performance
        nopython=True: Only a subset of the python syntax is supported.
                       Avoid everything but primitives and numpy arrays.
                       All slow operation will yield an exception
        nogil=True:    This method will release the global interpreter lock. So
                       this method can run in parallel with other python code
        """
        for tag in tags:
            while tag['time'] >= next_edge:
                next_edge += binwidth
                bin_index += 1
                if bin_index == n_values:
                    bin_index = 0
                data[bin_index, :] = 0
                overflows[bin_index] = overflow_state
            if tag['type'] == 0:
                for i in range(len(channels)):
                    if channels[i] == tag['channel']:
                        data[bin_index, i] += 1
                        break
            elif tag['type'] == 2:
                overflows[bin_index] = True
                overflow_state = True
            elif tag['type'] == 3:
                overflows[bin_index] = True
                overflow_state = False
            elif tag['type'] == 4:
                overflows[bin_index] = True
        return bin_index, next_edge, overflow_state

    def process(self, incoming_tags, begin_time, end_time):
        # the lock is already acquired
        # self.data is provided as reference, so it must not be accessed
        # anywhere else without locking the mutex.
        # incoming_tags is provided as a read-only reference. The storage will
        # be deallocated after this call, so you must not store a reference to
        # this object. Make a copy instead.
        if not self.next_edge:
            self.next_edge = begin_time + self.binwidth
        self.bin_index, self.next_edge, self.overflow_state = CustomCounter.fast_process(
            incoming_tags,
            np.array(self.channels),
            self.data, self.overflows,
            self.binwidth,
            self.n_values + 1,
            self.bin_index,
            self.next_edge,
            self.overflow_state)


def get_channels_for_overflow(tagger):
    """Using the test signal, it is hard on the Time Tagger Ultra to reach the overflow mode,
    so we take eight channels in this case. For the Time Tagger 20, one channel is sufficient."""
    if tagger.getModel() == 'Time Tagger Ultra':
        rising_edges = tagger.getChannelList(TimeTagger.ChannelEdge.Rising)[:4]
        return list(rising_edges) + list(map(tagger.getInvertedChannel, rising_edges))
    return tagger.getChannelList()[:1]


if __name__ == '__main__':
    tt = TimeTagger.createTimeTagger()

    channels = get_channels_for_overflow(tt)

    tt.setTestSignalDivider(3)
    tt.setTestSignal(tt.getChannelList(TimeTagger.ChannelEdge.Rising), True)

    BINWIDTH = int(1E9)
    custom_counter = CustomCounter(tt, channels, binwidth=BINWIDTH, n_values=6000)

    custom_counter.startFor(int(6E12))
    fig = plt.figure()
    is_running = True
    while is_running:
        is_running = custom_counter.isRunning()
        fig.clear()
        plt.plot(custom_counter.getIndex(), custom_counter.getData())
        plt.xlabel('Time, s')
        plt.ylabel('Count rate, counts/s')
        plt.pause(.1)

    del tt

    plt.show()
