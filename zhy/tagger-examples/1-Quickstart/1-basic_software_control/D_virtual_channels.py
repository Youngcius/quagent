"""Virtual channels are used to generate new data streams from given input streams. These data streams
can be used just like physical channels. It is also possible to cascade virtual channels
to create mighty filters that operate on the fly.
We will use virtual channels in this example to answer the question: If the rising edges of the
built-in test signal on two channels are quite close to each other, will the subsequent falling
edges be close as well? We will use a cascade of virtual channels:
1. "Coincidence" will tell us whether two rising edges are close or not.
2. The result will act as a start signal for the "GatedChannel" for the falling edges of channel 1.
3. A "DelayedChannel" generated from the "Coincidence" will close this gate after one edge.
4. A second "GatedChannel" with swapped opener/closer will include complimentary data (falling edges
of input 1 following rising edges which are far apart)
Finally, we will compare the Correlations of channel 2 and the two GatedChannel, respectively."""

from matplotlib import pyplot as plt
from time import sleep
import numpy as np
import TimeTagger

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Enable the test signal on channel 1 and channel 2
tagger.setTestSignal([1, 2], True)

# We use a Correlation measurement to determine the delay between channel 1 and 2
calibration = TimeTagger.Correlation(tagger=tagger,
                                     channel_1=1,
                                     channel_2=2,
                                     binwidth=1,
                                     n_bins=10000)
calibration.startFor(int(1E12))
calibration.waitUntilFinished()

# The delay between the channels is given by the center of mass of the count distribution
delay = int(np.round(sum(calibration.getIndex() * calibration.getData()) / sum(calibration.getData())))
print("Measured delay: {:0.0f} ps".format(delay))

# Now we want to distinguish two cases: Rising edges that are quite close, an those which are more far apart.
# As a tool, we use the virtual channel Coincidence with our measured average delay as coincidenceWindow.
# This means: If two edges are relatively close (= inside coincidenceWindow), there will be one timestamp
# in the virtual channel, right at the average of both input timestamps (determined by "timestamp" attribute)
open_gate = TimeTagger.Coincidence(tagger=tagger,
                                   channels=[1, 2],
                                   coincidenceWindow=int(abs(delay)),
                                   timestamp=TimeTagger.CoincidenceTimestamp.Average)
# To close the gate after one falling edge, we create a DelayedChannel from "open_gate". It is an exact
# copy, but delayed by 900000 ps. Note how the channel number of "open_gate" is passed to then new virtual
# channel: We call the getChannel() method to retrieve the number assigned by the Time Tagger backend.
close_gate = TimeTagger.DelayedChannel(tagger=tagger,
                                       input_channel=open_gate.getChannel(),
                                       delay=900000)

# Now we can create a reduced copy of the falling edges of input 1 that contains only those following a
# narrow pair of rising edges (those present in "open_gate"). We use the getInvertedChannel() method
# here to keep the example compatible with first generation Time Taggers that used another numbering
# scheme (starting with channel 0). If your Time Tagger starts at channel 1, you can use channel number
# -1 directly.
falling_narrow = TimeTagger.GatedChannel(tagger=tagger,
                                         input_channel=tagger.getInvertedChannel(1),
                                         gate_start_channel=open_gate.getChannel(),
                                         gate_stop_channel=close_gate.getChannel())
# The complementary data can be obtained by swapping "gate_start_channel" and "gate_stop_channel"
falling_wide = TimeTagger.GatedChannel(tagger=tagger,
                                       input_channel=tagger.getInvertedChannel(1),
                                       gate_start_channel=close_gate.getChannel(),
                                       gate_stop_channel=open_gate.getChannel())
# In the same way, we create GatedChannels from the later one of channel 1 and 2. Because the Conincidence
# timestamp is always the average of both, we can use it to gate the second one.
rising_narrow = TimeTagger.GatedChannel(tagger=tagger,
                                        input_channel=1 if delay > 0 else 2,
                                        gate_start_channel=open_gate.getChannel(),
                                        gate_stop_channel=close_gate.getChannel())
rising_wide = TimeTagger.GatedChannel(tagger=tagger,
                                      input_channel=1 if delay > 0 else 2,
                                      gate_start_channel=close_gate.getChannel(),
                                      gate_stop_channel=open_gate.getChannel())

# Create a SynchronizedMeasurement to ensure that the same data set is used in both cases
synchronized = TimeTagger.SynchronizedMeasurements(tagger=tagger)
binwidth = 1
n_bins = abs(3 * delay) // binwidth
corr_falling_narrow = TimeTagger.Correlation(tagger=synchronized.getTagger(),
                                             channel_1=falling_narrow.getChannel(),
                                             channel_2=tagger.getInvertedChannel(2),
                                             binwidth=binwidth,
                                             n_bins=n_bins)
corr_falling_wide = TimeTagger.Correlation(tagger=synchronized.getTagger(),
                                           channel_1=falling_wide.getChannel(),
                                           channel_2=tagger.getInvertedChannel(2),
                                           binwidth=binwidth,
                                           n_bins=n_bins)

corr_rising_narrow = TimeTagger.Correlation(tagger=tagger,
                                            channel_1=rising_narrow.getChannel() if delay > 0 else 1,
                                            channel_2=2 if delay > 0 else rising_narrow.getChannel(),
                                            binwidth=binwidth,
                                            n_bins=n_bins)
corr_rising_wide = TimeTagger.Correlation(tagger=tagger,
                                          channel_1=rising_wide.getChannel() if delay > 0 else 1,
                                          channel_2=2 if delay > 0 else rising_wide.getChannel(),
                                          binwidth=binwidth,
                                          n_bins=n_bins)

# Run the measurement for 1 s
synchronized.startFor(capture_duration=int(1E12))
synchronized.waitUntilFinished()

# Plot the result
fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
axes[0].plot(corr_rising_narrow.getIndex(), corr_rising_narrow.getData())
axes[0].plot(corr_rising_wide.getIndex(), corr_rising_wide.getData())
axes[0].set_title("Rising edges")
# We use getDataNormalized() instead of getData() to account for a non-perfect
# 50:50 ratio of the counts of the two GatedChannels.
axes[1].plot(corr_falling_narrow.getIndex(), corr_falling_narrow.getDataNormalized())
axes[1].plot(corr_falling_wide.getIndex(), corr_falling_wide.getDataNormalized())
axes[1].set_title("Falling edges")
plt.show()
