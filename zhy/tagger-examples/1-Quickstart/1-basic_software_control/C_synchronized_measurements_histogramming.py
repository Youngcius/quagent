"""In this example, we compare the behavior of histogramming measurement classes (Correlation, Histogram,
HistogramLogBins, and StartStop). We use SynchronizedMeasurements to ensure that all parallel
measurements use the very same subset of time tags.
Besides, the example shows the capabilities of the Time Tagger engine. Some of the histograms have 4 million bins.
The visualization is only getting slow because matplotlib is reaching its limits here."""

from matplotlib import pyplot as plt
import numpy as np
import TimeTagger

# Create a TimeTagger instance to control your hardware
tagger = TimeTagger.createTimeTagger()

# Enable the test signal on channel 1 and channel 2 and delay channel 2 by 2 ns
tagger.setTestSignal([1, 2], True)
tagger.setInputDelay(1, 2000)

TimeTagger.TimeDifferences()

# Create a SynchronizedMeasurements instance that allows you to control all child
synchronized = TimeTagger.SynchronizedMeasurements(tagger)

# To create synchronized measurement instances, we need a special TimeTagger object
# that we can obtain by the getTagger method. The returned proxy object is not identical
# with the "tagger" object we created above. If we pass the "sync_tagger_proxy" object to a
# measurement, the measurement will NOT start immediately on creation.
# Instead, the "synchronized" object takes control
sync_tagger_proxy = synchronized.getTagger()

# Create a Correlation object. We double the amount of n_bins because Correlation will
# provide results for both, positive and negative values
correlation = TimeTagger.Correlation(tagger=sync_tagger_proxy,
                                     channel_1=1,
                                     channel_2=2,
                                     binwidth=1,
                                     n_bins=2*2*10**6)
# Histogram is very similar to Correlation, but with fixed roles of start and click channel
# instead of both channels playing both roles.
histogram = TimeTagger.Histogram(tagger=sync_tagger_proxy,
                                 click_channel=1,
                                 start_channel=2,
                                 binwidth=1,
                                 n_bins=2*10**6)

# StartStop is a little bit different: Firstly, it is single-start/single-stop, so with the
# periodic test signal, we will obtain only a single peak. Secondly, it has no pre-defined
# set of bins and not even a defined number of bins, only the binwidth is fixed. It will create
# bins as they are needed and return pairs of (x, y) values.
start_stop = TimeTagger.StartStop(tagger=sync_tagger_proxy,
                                  click_channel=1,
                                  start_channel=2,
                                  binwidth=1)
# HistogramLogBins is similar to Histogram, but not with a linearly distributed set of equally
# sized bins, but with a bins growing from 10^exp_start
histogram_log = TimeTagger.HistogramLogBins(tagger=sync_tagger_proxy,
                                            click_channel=1,
                                            start_channel=2,
                                            exp_start=-12,
                                            exp_stop=-5,
                                            n_bins=1000)

print("Acquire the histograms for 5 seconds.")
# We let the synchronized measurements run for 5 s
synchronized.startFor(int(5E12))
synchronized.waitUntilFinished()

# Create the plot
plt.figure()
histogram_log_edges = histogram_log.getBinEdges()
histogram_log_data = histogram_log.getDataNormalizedCountsPerPs()
np.nan_to_num(histogram_log_data, copy=False)
plt.bar(x=histogram_log_edges[:-1],
        height=histogram_log_data,
        width=np.diff(histogram_log_edges),
        align="edge",
        color=(1, 0, 0),
        edgecolor=(0, 0, 0),
        label="HistogramLogBins",
        zorder=1)
corr_index = correlation.getIndex()
corr_data = correlation.getData()
plt.plot(corr_index,
         corr_data,
         linewidth=3,
         label="Correlation",
         zorder=2)
plt.plot(histogram.getIndex(),
         histogram.getData(),
         linestyle="--",
         label="Histogram",
         zorder=3)
start_stop_data = start_stop.getData()
plt.scatter(start_stop_data[:, 0],
            start_stop_data[:, 1],
            color="green",
            marker=".",
            label="StartStop",
            zorder=4)
plt.xlabel("Time [ps]")
plt.ylabel("Counts in 1 ps bin")
plt.legend(loc='upper right')

# Add some annotations to illustrate the graph
peak = np.argmax(corr_data)
neg_sidepeak = np.argmax(corr_data[:int(.8*2e6)])
pos_sidepeak = -np.argmax(corr_data[:int(-.8*2e6):-1])
plt.annotate("Zoom x axis here:\nAll results are\nvery similar",
             (corr_index[peak], corr_data[peak]/2),
             xytext=(100, 0),
             textcoords="offset pixels",
             arrowprops={"arrowstyle": "->"})
plt.annotate("Zoom here:\nOnly\nCorrelation\nprovides\nneg. data",
             (corr_index[neg_sidepeak], corr_data[neg_sidepeak]),
             xytext=(0, 100),
             textcoords="offset pixels",
             horizontalalignment='center',
             verticalalignment='bottom',
             arrowprops={"arrowstyle": "->"})
plt.annotate("Zoom here:\nStartStop does not\nsee the second peak",
             (corr_index[pos_sidepeak], corr_data[pos_sidepeak]),
             xytext=(0, 100),
             textcoords="offset pixels",
             arrowprops={"arrowstyle": "->"})
last_filled_log_bin = -np.argmax(histogram_log_data[::-1] > 0) - 1
plt.annotate("Zoom here:\nHistogramLogBins\nshows bins for\nlarge delays",
             ((histogram_log_edges[last_filled_log_bin-1] + histogram_log_edges[last_filled_log_bin])/2,
                 histogram_log_data[last_filled_log_bin]),
             xytext=(-100, 100),
             textcoords="offset pixels",
             horizontalalignment='center',
             verticalalignment='bottom',
             arrowprops={"arrowstyle": "->"})
plt.show()
