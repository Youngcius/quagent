import matplotlib.pyplot as plt
import TimeTagger
import numpy as np
import numba
from time import sleep


class CustomStartMultipleStop(TimeTagger.CustomMeasurement):
    """
    Example for a single start - multiple stop measurement.
        The class shows how to access the raw time-tag stream.
    """

    def __init__(self, tagger, click_channel, start_channel, binwidth, n_bins):
        TimeTagger.CustomMeasurement.__init__(self, tagger)
        self.click_channel = click_channel
        self.start_channel = start_channel
        self.binwidth = binwidth
        self.max_bins = n_bins

        # The method register_channel(channel) activates
        # that data from the respective channels is transferred
        # from the Time Tagger to the PC.
        self.register_channel(channel=click_channel)
        self.register_channel(channel=start_channel)

        self.clear_impl()

        # At the end of a CustomMeasurement construction,
        # we must indicate that we have finished.
        self.finalize_init()

    def __del__(self):
        # The measurement must be stopped before deconstruction to avoid
        # concurrent process() calls.
        self.stop()

    def getData(self):
        # Acquire a lock this instance to guarantee that process() is not running in parallel
        # This ensures to return a consistent data.
        self._lock()
        arr = self.data.copy()
        # We have gathered the data, unlock, so measuring can continue.
        self._unlock()
        return arr

    def getIndex(self):
        # This method does not depend on the internal state, so there is no
        # need for a lock.
        arr = np.arange(0, self.max_bins) * self.binwidth
        return arr

    def clear_impl(self):
        # The lock is already acquired within the backend.
        self.last_start_timestamp = 0
        self.data = np.zeros((self.max_bins,), dtype=np.uint64)

    def on_start(self):
        # The lock is already acquired within the backend.
        pass

    def on_stop(self):
        # The lock is already acquired within the backend.
        pass

    @staticmethod
    @numba.jit(nopython=True, nogil=True)
    def fast_process(
            tags,
            data,
            click_channel,
            start_channel,
            binwidth,
            last_start_timestamp):
        """
        A precompiled version of the histogram algorithm for better performance
        nopython=True: Only a subset of the python syntax is supported.
                       Avoid everything but primitives and numpy arrays.
                       All slow operation will yield an exception
        nogil=True:    This method will release the global interpreter lock. So
                       this method can run in parallel with other python code
        """
        for tag in tags:
            # tag.type can be: 0 - TimeTag, 1- Error, 2 - OverflowBegin, 3 -
            # OverflowEnd, 4 - MissedEvents
            if tag['type'] != 0:
                # tag is not a TimeTag, so we are in an error state, e.g. overflow
                last_start_timestamp = 0
            elif tag['channel'] == click_channel and last_start_timestamp != 0:
                # valid event
                index = (tag['time'] - last_start_timestamp) // binwidth
                if index < data.shape[0]:
                    data[index] += 1
            if tag['channel'] == start_channel:
                last_start_timestamp = tag['time']
        return last_start_timestamp

    def process(self, incoming_tags, begin_time, end_time):
        """
        Main processing method for the incoming raw time-tags.

        The lock is already acquired within the backend.
        self.data is provided as reference, so it must not be accessed
        anywhere else without locking the mutex.

        Parameters
        ----------
        incoming_tags
            The incoming raw time tag stream provided as a read-only reference.
            The storage will be deallocated after this call, so you must not store a reference to
            this object. Make a copy instead.
            Please note that the time tag stream of all channels is passed to the process method,
            not only the onces from register_channel(...).
        begin_time
            Begin timestamp of the of the current data block.
        end_time
            End timestamp of the of the current data block.
        """
        self.last_start_timestamp = CustomStartMultipleStop.fast_process(
            incoming_tags,
            self.data,
            self.click_channel,
            self.start_channel,
            self.binwidth,
            self.last_start_timestamp)


# Channel definitions
CHAN_START = 1
CHAN_STOP = 2

if __name__ == '__main__':

    print("""Custom Measurement example

Implementation of a custom single start, multiple stop measurement, histogramming
the time differences of the two input channels.

The custom implementation will be comparted to a the build-in Histogram class,
which is a multiple start, multiple stop measurement. But for the
selected time span of the histogram, multiple start does not make a difference.
""")

    tagger = TimeTagger.createTimeTagger()

    # enable the test signal
    tagger.setTestSignal([CHAN_START, CHAN_STOP], True)
    # delay the stop channel by 2 ns to make sure it is later than the start
    tagger.setInputDelay(CHAN_STOP, 2000)

    BINWIDTH = 1  # ps
    BINS = 4000

    # We first have to create a SynchronizedMeasurements object to synchronize several measurements
    with TimeTagger.SynchronizedMeasurements(tagger) as measurementGroup:
        # Instead of a real Time Tagger, we initialize the measurement with the proxy object measurementGroup.getTagger()
        # This adds the measurement to the measurementGroup. In contrast to a normal initialization of a measurement, the
        # measurement does not start immediately but waits for an explicit .start() or .startFor().
        custom_histogram = CustomStartMultipleStop(measurementGroup.getTagger(), CHAN_STOP, CHAN_START, binwidth=BINWIDTH, n_bins=BINS)
        histogram = TimeTagger.Histogram(measurementGroup.getTagger(), CHAN_STOP, CHAN_START, binwidth=BINWIDTH, n_bins=BINS)

        print("Acquire data...\n")
        measurementGroup.startFor(int(3e12))
        measurementGroup.waitUntilFinished()

        x_custom_histogram = custom_histogram.getIndex()
        y_custom_histogram = custom_histogram.getData()

        x_histogram = histogram.getIndex()
        y_histogram = histogram.getData()

        assert np.all(y_custom_histogram ==
                      y_histogram), "ERROR: The custom implementation has a different result than the Histogram from the API!"
        print("The custom implementation shows the very same data as the Histogram from the API.")

    plt.plot(x_custom_histogram, y_custom_histogram, label='custom histogram')
    plt.plot(x_histogram, y_histogram, '--', label='histogram')
    plt.xlabel('Time difference (ps)')
    plt.ylabel('Counts')
    plt.legend()
    plt.show()
