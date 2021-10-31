"""Welcome to the Time Tagger examples!
In this first example we show how a simply meaningful measurement can be implemented.
We use the built-in test signal within the Time Tagger. 
The applied signal is the very same but has a fixed temoral shift depending on the channel used.
We will compensate for this delay and repeat the measurement to verify the compensation."""

import TimeTagger
import numpy as np


def get_delay_and_jitter(x, y):
    # Helper method to calculate the mean time difference of a histogram and the standard deviation.
    mean = np.average(x, weights=y)
    std = np.sqrt(np.average((x-mean)**2, weights=y))
    return mean, std


print("Hello World Example\n")
# Now we connect the Time Tagger.
tagger = TimeTagger.createTimeTagger()

# To generate test data without physical inputs, the Time Tagger has a built-in oscillator providing a
# signal at ~800 kHz. It can be set for each channel individually and will disconnect external signals applied to that channel.
# There is a time offset between the test signals on the range of +/- 2 ns.
tagger.setTestSignal(1, True)
tagger.setTestSignal(2, True)

# We can set the trigger level of the input, although it has no effect if we use the built-in test signal.
# Not taking care of the trigger level is a common source of unexpected behavior!
# Learn more on trigger levels in example 2/B
tagger.setTriggerLevel(channel=1, voltage=0.5)
tagger.setTriggerLevel(channel=2, voltage=0.5)

# Now we create our first measurement, a 'Correlation' histogram between channel 1 and 2 that will show a maximum
# at the specific delay of between the channels. Learn more on creating measurements in example 1/A.
correlation = TimeTagger.Correlation(tagger=tagger,
                                     channel_1=1,
                                     channel_2=2,
                                     binwidth=10,
                                     n_bins=5000)

print("Acquire a 'Correlation' histogram between channel 1 and 2 for 5 seconds.")
# To run the measurement for exactly one second, we use the startFor method.
# Learn more on starting and stopping measurements in example 1/B.
correlation.startFor(capture_duration=int(5E12))
correlation.waitUntilFinished()

# Analysis of the delay and jitter of the acquired histogram. The data analyzed will reflect the channel-channel jitter
# for your respective Time Tagger.
delay, jitter_rms = get_delay_and_jitter(correlation.getIndex(), correlation.getData())
print("The measured delay is {:.1f} ps with an RMS of {:.1f} ps.".format(delay, jitter_rms))

# Compensate the test signal time offset.
tagger.setInputDelay(channel=2, delay=int(round(delay)))
print("The input delay of channel 2 has been set to {:d} to compensate the time offset of the test signal.".format(int(round(delay))))

# startFor does by default clear the measurement, so we resuse use our measurement again without a .clear() command.
# Repeat the measurement to confirm that the delay is compensated.
print("\nAcquire another 'Correlation' histogram between channel 1 and 2 for 5 seconds.")
correlation.startFor(capture_duration=int(5E12))
correlation.waitUntilFinished()

delay, jitter_rms = get_delay_and_jitter(correlation.getIndex(), correlation.getData())
print("The new measured delay is {:.1f} ps with an RMS of {:.1f} ps.".format(delay, jitter_rms))

# Close the connection to the Time Tagger.
del tagger
