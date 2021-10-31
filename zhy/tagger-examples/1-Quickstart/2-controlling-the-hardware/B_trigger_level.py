"""The trigger level is the voltage value that is compared to your input signal in the very first
stage in the Time Tagger. The built-in test signal cannot be used to demonstrate the effect of the
trigger level setting as it is injected in a subsequent stage. However, we can check the accuracy
of the trigger level of your device in this example: At a setting of 0 V, the input noise of the
unconnected input will trigger the comparator randomly. We will scan the voltage range around 0 V
to determine the noise level."""

from matplotlib import pyplot as plt
from time import sleep
import numpy as np
import TimeTagger
import sys

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

inputs = tagger.getChannelList(TimeTagger.ChannelEdge.Rising)

# With getDACRange(), we can check the minimum and maximum values of the trigger level. A Time
# Tagger 20 will only accept positive values, while a Time Tagger Ultra takes negative values as well.
if tagger.getDACRange()[0] < 0:
    levels = np.linspace(start=-0.01, stop=0.01, num=200)
    print("Scan trigger levels from -10 mV to 10 mV:")
else:
    levels = np.linspace(start=0, stop=0.01, num=100)
    print("Scan trigger levels from 0 mV to 10 mV:")
countrate = TimeTagger.Countrate(tagger=tagger, channels=inputs)
results = list()

for level in levels:
    for inp in inputs:
        tagger.setTriggerLevel(channel=inp, voltage=level)
    countrate.startFor(int(1E8))
    countrate.waitUntilFinished()
    results.append(countrate.getData())
    sys.stdout.write("Trigger level: {:2.3f} mV, Overflows: {:<7}\r".format(level * 1000, tagger.getOverflowsAndClear()))
print("\nDone")
result_array = np.array(results)
if result_array.any():
    plt.figure()
    plots = plt.plot(levels, result_array)
    plt.title("Trigger level scan")
    plt.xlabel("Trigger level, V")
    plt.ylabel("Countrate, counts/s")
    plt.legend(plots, ["Input " + str(inp) for inp in inputs])
    plt.show()
else:
    print("""For your device, no noise clicks occured for the given trigger level range.
All acquired counts are 0.
You still can see from the code from this example how the trigger levels can be set.""")
