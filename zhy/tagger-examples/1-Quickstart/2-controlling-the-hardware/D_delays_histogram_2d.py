"""Similar to the 'hello world' example, we align channel delays to each other.
In this example, we use even three channels. One will act as the START_CH, the
channel under investigation. We will measure its temporal delay compared to two other
test signal channels, INPUT_T1 and INPUT_T2, respectively. The two-dimensional
distribution of time-tags will be tracked by the Histogram2D measurement class.
Adjusting the delays is necessary to place the measured delays in the center of the
Histogram2D window.
"""

import matplotlib.pyplot as plt
from time import sleep
import TimeTagger

tagger = TimeTagger.createTimeTagger()

# Channel definitions
START_CH = 1
INPUT_T1 = 2
INPUT_T2 = 3

# Histogram parameters
binwidth_1 = 1
binwidth_2 = binwidth_1
n_bins_1 = 400
n_bins_2 = 300

# Enable test signal
tagger.setTestSignal([START_CH, INPUT_T1, INPUT_T2], True)

# Use Correlation measurement for both inputs to measure signal delays relative to start
corr1 = TimeTagger.Correlation(tagger, INPUT_T1, START_CH, 10, 10000)
corr2 = TimeTagger.Correlation(tagger, INPUT_T2, START_CH, 10, 10000)

sleep(2)

x1 = corr1.getIndex()
sd1 = corr1.getData()
idx1 = sd1.argmax()
delay1 = x1[idx1]

print('Measured delay at INPUT_T1: {:0.0f} ps'.format(delay1))

x2 = corr2.getIndex()
sd2 = corr2.getData()
idx2 = sd2.argmax()
delay2 = x2[idx2]

print('Measured delay at INPUT_T2: {:0.0f} ps'.format(delay2))

# Delays signals such that T1 and T2 by half of the histogram span
T1_delay = -delay1 + round(binwidth_1*n_bins_1/2)
T2_delay = -delay2 + round(binwidth_2*n_bins_2/2)

# We use setInputDelay to adjust the delays of T1 and T2. This method will call the setDelayHardware method if possible.
# Otherwise, the call is redirected to setDelaySoftware. Refer to the Time Tagger manual to learn about the difference.
tagger.setInputDelay(INPUT_T1, int(T1_delay))
tagger.setInputDelay(INPUT_T2, int(T2_delay))

# Create 2D Histogram measurement
h2d = TimeTagger.Histogram2D(tagger,
                             start_channel=START_CH,
                             stop_channel_1=INPUT_T1,
                             stop_channel_2=INPUT_T2,
                             binwidth_1=binwidth_1,
                             binwidth_2=binwidth_2,
                             n_bins_1=n_bins_1,
                             n_bins_2=n_bins_2
                             )

# Wait for data to accumulate
plt.pause(2)

# Get and plot Histogram2D data
data2d = h2d.getData()
time1 = h2d.getIndex_1()
time2 = h2d.getIndex_2()

fig, ax = plt.subplots()

ax.pcolormesh(time1, time2, data2d.transpose())
ax.set_title('Histogram 2D')
ax.set_xlabel('T1 (ps)')
ax.set_ylabel('T2 (ps)')

del tagger

plt.show()
