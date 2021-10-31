"""A measurement can be stopped, resumed, started for a defined period of time or cleared."""

from time import sleep
import TimeTagger

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Activate test signal on channel 1
tagger.setTestSignal(1, True)

print("""
                        | getCountsTotal() | getCaptureDuration()
------------------------+------------------+---------------------""")

# We create a Countrate instance, it will acquire data immediately
countrate = TimeTagger.Countrate(tagger=tagger, channels=[1])
sleep(.5)
print("(1) Init, sleep(0.5s)   | {:>16,d} | {:>20,d}".format(
    countrate.getCountsTotal()[0], countrate.getCaptureDuration()))

# Stop the measurement
countrate.stop()
sleep(.5)
print("(2) ... stop            | {:>16,d} | {:>20,d}".format(
    countrate.getCountsTotal()[0], countrate.getCaptureDuration()))

# By calling start, we can resume the measurement
countrate.start()
print("(3) ... resume          | {:>16,d} | {:>20,d}".format(
    countrate.getCountsTotal()[0], countrate.getCaptureDuration()))
sleep(.5)
print("(4) ... sleep(0.5s)     | {:>16,d} | {:>20,d}".format(
    countrate.getCountsTotal()[0], countrate.getCaptureDuration()))

# We can clear the acquired data while the measurement is running
countrate.clear()
sleep(.5)
print("(5) clear, sleep(0.5s)  | {:>16,d} | {:>20,d}".format(
    countrate.getCountsTotal()[0], countrate.getCaptureDuration()))
countrate.startFor(500000000000)
countrate.waitUntilFinished()

print("(6) startFor(0.5s)      | {:>16,d} | {:>20,d}".format(
    countrate.getCountsTotal()[0], countrate.getCaptureDuration()))

print("""
Please note the following:

(1),(2),(3)
The measurements can have the very same 'CaptureDuration' and Counts, but must not.
The total acquire time can be less than 0.5s, because the acquire
does not start right away, but the initialization is non-blocking.

(5) vs (1)
The acquire time can be the same but must not.

(6)
Only startFor guarantees a defined acquire time down to the ps.

How multiple measurements can be synchronized is shown in a following example.""")
