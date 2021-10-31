import matplotlib.pyplot as plt
import numpy as np
from TimeTagger import TimeTagStream, Flim, CountBetweenMarkers, createTimeTaggerVirtual

show_timing_information = True

data_file = 'Pollen_Galvo_c.ttbin'

laser = 1
click1 = -2
click2 = -3
frame = 4
pixel = 5
line = 6
bins = 100
binwidth = 125
xDim = 513
yDim = 513

laser_frequency = 80e6
total_frames = 2

print("This is a example not including the binary dump file required for the analysis.")
print("Please contact the support@swabianinstruments.com for further assistance.\n")

print("Initialize the Time Tagger Virtual")
t = createTimeTaggerVirtual()

print("Setup the config and measurements")
# shift the laser signal by one period to compensate for the shift due to the conditional filter
# you could also take the inverted time difference from the t_laser - t_photon with the inputDelay set to 0
t.setInputDelay(laser, int(-1/laser_frequency*1e12))

if show_timing_information:
    maxtags = 10 ** 6
    tts = TimeTagStream(
        t, maxtags, [frame, pixel, line, laser, click1, click2])
    cbm_pixels_per_line = CountBetweenMarkers(t, pixel, line)
    cbm_lines_per_frame = CountBetweenMarkers(t, line, frame)
    cbm_pixels_per_frame = CountBetweenMarkers(t, pixel, frame)

flim1 = Flim(t, start_channel=laser, click_channel=click1, pixel_begin_channel=pixel, n_pixels=xDim*yDim,
             n_bins=bins, binwidth=binwidth, frame_begin_channel=frame, finish_after_outputframe=total_frames, n_frame_average=1)
flim2 = Flim(t, start_channel=laser, click_channel=click2, pixel_begin_channel=pixel, n_pixels=xDim*yDim,
             n_bins=bins, binwidth=binwidth, frame_begin_channel=frame, finish_after_outputframe=total_frames, n_frame_average=1)

print("Read the dumped binary file.")
replay = t.replay(data_file)
t.waitForCompletion()

if show_timing_information == True:
    print("Plotting timing information")
    stream = tts.getData()
    timestamps = stream.getTimestamps()
    channels = stream.getChannels()
    t_start = timestamps[0]
    timestamps_pixel = timestamps[channels == pixel] - t_start
    timestamps_frame = timestamps[channels == frame] - t_start
    timestamps_line = timestamps[channels == line] - t_start
    timestamps_laser = timestamps[channels == laser] - t_start
    timestamps_click1 = timestamps[channels == click1] - t_start
    timestamps_click2 = timestamps[channels == click2] - t_start
    diff_pixel = np.diff(timestamps_pixel)
    diff_frame = np.diff(timestamps_frame)
    diff_line = np.diff(timestamps_line)
    plt.figure(1000)
    plt.clf()
    plt.plot(timestamps_laser,  timestamps_laser * 0 + 5, '.', label='laser')
    plt.plot(timestamps_click2, timestamps_click2 *
             0 + 4, '.', label='detector2')
    plt.plot(timestamps_click1, timestamps_click1 *
             0 + 3, '.', label='detector1')
    plt.plot(timestamps_pixel,  timestamps_pixel * 0 + 2, '.', label='pixel')
    plt.plot(timestamps_line,   timestamps_line * 0 + 1, '.', label='line')
    plt.plot(timestamps_frame,  timestamps_frame * 0 + 0, '.', label='frame')
    plt.legend(loc="lower left")

print("Plotting intensities")

# convert into 2D and take out the first pixel row and line
frames1 = []
for i in range(total_frames):
    base_frame = flim1.getReadyFrameEx(i)
    sums = base_frame.getIntensities()
    trans = sums.reshape(yDim, xDim)
    frames1.append(trans[1:, 1:])

frames2 = []
for i in range(total_frames):
    base_frame = flim2.getReadyFrameEx(i)
    sums = base_frame.getIntensities()
    trans = sums.reshape(yDim, xDim)
    frames2.append(trans[1:, 1:])

# plotting
fig = plt.figure(1)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_aspect('equal')
for i, frame in enumerate(frames1):
    plt.clf()
    plt.imshow(frame)
    plt.colorbar()
    plt.title('Intensity detector 1, frame %03d' % i)
    fname = 'flim_simple_detector1_%03d.png' % i
    plt.savefig(fname, bbox_inches='tight', pad_inches=0)

fig = plt.figure(2)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_aspect('equal')
for i, frame in enumerate(frames2):
    plt.clf()
    plt.imshow(frame)
    plt.colorbar()
    plt.title('Intensity detector 2, frame %03d' % i)
    fname = 'flim_simple_detector2_%03d.png' % i
    plt.savefig(fname, bbox_inches='tight', pad_inches=0)

plt.show()
