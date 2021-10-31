"""In this example we learn how to remove events on the device containing
no information to save USB bandwidth."""

from time import sleep
from matplotlib import pyplot as plt
import TimeTagger
import sys


def find_random_signal(tt, threshold_rate):
    # This function scans the trigger level in the same way like
    # it is shown in example 2-B.
    level = max(-0.01, tt.getDACRange()[0])
    channels = tt.getChannelList(TimeTagger.ChannelEdge.Rising)
    count = TimeTagger.Countrate(tagger=tt, channels=channels)
    print("")
    while level < 0.01:
        sys.stdout.write("Searching level: {:2.1f} mV\r".format(level * 1000))
        for channel in channels:
            tt.setTriggerLevel(channel, level)
        count.startFor(int(1E8))
        count.waitUntilFinished()
        data = count.getData()
        if max(data) > threshold_rate:
            return channels[data.argmax()], level, True
        level += 0.0001
    return 0, .0, False


# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Set a threshold for the random counts according to the Time Tagger model
min_random_rate = 1E8 if tagger.getModel() == "Time Tagger Ultra" else 3E7

# Try to find a channel that exceeds the countrate threshold and set the
# trigger level accordingly
random_channel, random_level, random_found = find_random_signal(tagger, min_random_rate)
if random_found:
    print("\nFound a random signal on channel {} at {:2.3} mV.".format(random_channel, 1000 * random_level))
    tagger.setTriggerLevel(channel=random_channel, voltage=random_level)

    # The default dead-time is defined by the internal clock of the Time Tagger
    # TT Ultra: 500 MHz, TT 20: 166.6 MHz
    default_deadtime = tagger.getDeadtime(random_channel)

    # To measure the a count rate that exceeds the USB transfer limit without overflows,
    # we use the EventDivider. With divider=100, it will discard 99 out of 100 events and
    # lets only pass every 100th event, which is within the USB bandwidth
    tagger.setEventDivider(channel=random_channel, divider=100)
    count = TimeTagger.Countrate(tagger, [random_channel])
    count.startFor(int(1E12))
    count.waitUntilFinished()

    # To obtain the real count rate, we have to multiply by 100
    countrate = count.getData()[0] * 100
    specified_usb_rate = 65E6 if tagger.getModel() == "Time Tagger Ultra" else 7.5E6
    print("\nThe countrate of the random channel is {:.1f} Mtags/s".format(countrate / 1E6))
    print("This is {:.1f} % of the specified USB data rate and {:.1f} % of the maximal time-to-digital conversion rate.".format(
        100*countrate/specified_usb_rate, 100*countrate/(1E12/default_deadtime)
    ))

    # Switch off the EventDivider = set it to 1
    tagger.setEventDivider(channel=random_channel, divider=1)

    # Take a second input channel which is NOT the random channel and let it
    # measure the built-in test signal, i.e. a periodic signal
    periodic_channel = 2 if random_channel == 1 else 1
    tagger.setTestSignal(periodic_channel, True)

    # We want to measure only the very first random click after a periodic click.
    # This is achieved by the ConditionalFilter. It opens a gate for any event
    # on the 'trigger' channels and lets only one event of each 'filtered' channel
    # pass. After that, the gate is closed until the next trigger.
    tagger.setConditionalFilter(trigger=[periodic_channel], filtered=[random_channel])

    # We measure the correlation between the periodic channel an the FILTERED
    corr = TimeTagger.Correlation(tagger=tagger,
                                  channel_1=random_channel,
                                  channel_2=periodic_channel,
                                  binwidth=default_deadtime//100,
                                  n_bins=3000)
    plt.figure()
    print("\nMeasuring with different dead-times:")
    for i in range(1, 6):
        # We repeat this measurement for five different dead-times
        tagger.setDeadtime(random_channel, i * default_deadtime)
        deadtime = tagger.getDeadtime(random_channel)
        print("Default dead-time x {} = {}".format(i, deadtime))
        corr.startFor(int(1E12))
        corr.waitUntilFinished()
        plt.plot(corr.getIndex()/default_deadtime, corr.getData(), label="{} ps".format(deadtime))
    plt.title("Correlation for different dead-times")
    plt.xlabel("Delay/(default_deadtime = {} ps)".format(default_deadtime))
    plt.ylabel("Counts/bin")
    plt.annotate("""Within the dead-time,
the Correlation is more
or less constant, i.e
randomly distributed.
For larger delays, the
Correlation drops with
the propability to find
no preceding time-tag.""",
                 (2, max(corr.getData())),
                 xytext=(-150, 0),
                 textcoords='offset pixels',
                 ha='right',
                 arrowprops={'arrowstyle': '->'})
    plt.legend()
    plt.show()
