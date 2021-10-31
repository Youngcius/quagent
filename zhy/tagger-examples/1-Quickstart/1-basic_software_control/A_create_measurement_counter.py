"""In this example, we learn how to start a simple measurement. We use the Counter class to measure a
count rate trace on channels 1 and 2 while switching on the built-in test signals."""


from matplotlib import pyplot as plt
from time import sleep
import TimeTagger

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Create an instance of the Counter measurement class. It will start acquiring data immediately.
counter = TimeTagger.Counter(tagger=tagger, channels=[1, 2], binwidth=int(1e9), n_values=1000)

# Apply the built-in test signal (~0.8 to 0.9 MHz) to channel 1
tagger.setTestSignal(1, True)
print("Test signal on channel 1 enabled")
sleep(.5)

# Apply test signal to channel 2
tagger.setTestSignal(2, True)
print("Test signal on channel 2 enabled")

# After waiting two times for 0.5 s, the 1000 values should be filled
sleep(.5)

# Data is retrieved by calling the method "getData" on the measurement class.
data = counter.getData()

# Plot the result
plt.figure()
plt.plot(counter.getIndex()/1e12, data[0]*1e-3, label='channel 1') # unit: ps (1e-12 s)
plt.plot(counter.getIndex()/1e12, data[1]*1e-3, label='channel 2')
plt.xlabel('Time [s]')
plt.ylabel('Countrate [MHz]')
plt.legend()
plt.title('Time trace of the click rate on channel 1 and 2')
# plt.text(0.1, 2,
#          '''The built-in test signal(~ 800 to 900 kHz) is applied first to channel 1
# and 0.5 s later to channel 2. The total delay time within the script is 1 s.
# As you can see, the counts are still 0 at 0.
# The Time Tagger and the analysis software are running asynchronously. Therefore the total processed data is less than 1 s.
# To have an exact measurement duration, please take startFor instead of pause.''')
plt.annotate('''The built-in test signal(~ 800 to 900 kHz) is applied
first to channel 1 and 0.5 s later to channel 2.
The total delay time within the script is 1 s.
As you can see, the counts are still 0 at 0.
The Time Tagger and the analysis software are
running asynchronously. Therefore the total processed
data is less than 1 s. To have an exact measurement
duration, please take startFor instead of pause.''',
             (0, 0),
             xytext=(100, 100),
             textcoords='offset pixels',
             arrowprops={'arrowstyle': '->'},
             va='bottom')
plt.tight_layout()
plt.show()

