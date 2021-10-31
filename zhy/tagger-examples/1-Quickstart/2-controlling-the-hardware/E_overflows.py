"""In this example we observe the overflow behavior of the Time Tagger. Overflows occur when the data
rate is too high and the buffer onboard the Time Tagger is completely filled. In this situation, data
loss occurs."""

import sys
import os
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import TimeTagger

try:
    # We load the CustomCounter class that we will discuss in detail in example 4-C.
    # It is a sub-class of CustomMeasurement and resembles the standard Counter class,
    # but in comparison Counter it is able to track overflows.
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../4-working-with-raw-time-tags")
    from C_custom_measurement import CustomCounter, get_channels_for_overflow
except ModuleNotFoundError as e:
    print(e)
    exit()

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

CHANNELS = get_channels_for_overflow(tagger)

# Activate test signal on the selected channels
tagger.setTestSignal(CHANNELS, True)

# We use the CustomCounter class that we loaded from example 4-C
counter = CustomCounter(tagger=tagger,
                        channels=CHANNELS,
                        binwidth=1000000000,
                        n_values=60000)

default_divider = tagger.getTestSignalDivider()
print("The test signal divider will be reduced until overflows occur.")
print("The default test signal divider is: {}".format(default_divider))

sleep(2)

# We increase the data rate successively by reducing the TestSignalDivider
divider = default_divider
while divider > 1 and not tagger.getOverflows():
    divider //= 2
    sys.stdout.write("divider = {:2}\r".format(divider))
    tagger.setTestSignalDivider(divider)
    sleep(5)
print("\nOverflows occurred at test signal divider of {}".format(divider))

# We let the Time Tagger run for two more seconds in the overflow
sleep(5)

# Reset TestSignalDivider to the default value to recover from overflow mode
tagger.setTestSignalDivider(default_divider)
sleep(3)
counter.stop()

# Plot the result
fig = plt.figure()
index = counter.getIndex()/1E12
plt.plot(index, counter.getData(exclude_overflows=True))
plt.xlabel("Time, s")
plt.ylabel("Counts/s")
data_for_annotation = counter.getData(exclude_overflows=False)[:, 0]
annotation_y = np.max(data_for_annotation)
annotation_x = index[np.where(data_for_annotation == annotation_y)[0][0]]
plt.annotate("""In the overflow mode,
there are gaps in the curve.
After the overflown buffer is
emptied by the USB transfer, it
can accumulate normal time-tags
for a short period, before
it overflows again. These
time-tags are displayed between
the gaps.""",
             (annotation_x, annotation_y),
             xytext=(-100, 0),
             textcoords='offset pixels',
             va='top',
             ha='right',
             arrowprops={'arrowstyle': '->'})
plt.show()
