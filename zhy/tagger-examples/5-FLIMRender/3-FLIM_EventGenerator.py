import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from intensity_renderer import IntensityRenderer
from TimeTagger import createTimeTaggerVirtual, EventGenerator

data_file = 'Pollen_b.ttbin'

laser = 1
cfd1 = 9
cfd2 = 10
frameStart = 5
frameStop = 4
line = 6
line_n = -6
bins = 100
binwidth = 125
xDim = 512
yDim = 512

laser_frequency = 80e6

print("This is a example not including the binary dump file required for the analysis.")
print("Please contact the support@swabianinstruments.com for further assistance.\n")

t = createTimeTaggerVirtual()

# shift the laser signal by one period to compensate for the shift due to the conditional filter
# you could also take the inverted time difference from the t_laser - t_photon with the inputDelay set to 0
t.setInputDelay(laser, int(-1/laser_frequency*1e12))

# obtained from StartStop(t, line_n, line, 1000)
line_time = 41674000
pixel_time = line_time / xDim
pixel_pattern = []
pixel_end_pattern = []

for i in range(xDim):
    step = pixel_time * i
    end_step = pixel_time * (i + 1) - 1
    pixel_pattern.append(int(step))
    pixel_end_pattern.append(int(end_step))

pixel_measurement = EventGenerator(t, line, pixel_pattern)
pixel = pixel_measurement.getChannel()

pixel_end_measurement = EventGenerator(t, line, pixel_end_pattern)
pixelEnd = pixel_end_measurement.getChannel()

# if the sync channel is defined - the measurement start with the very first sync
# the integration time per pixel is then defined via n_bins * binwidth
# if you know the number of frame triggers in before - you can use
# td.setMaxCount = xyz
# and ask with
# if td.ready():
# whether the desired numbers of frame triggers have been received

# with the parameter 'divider', you can select how many input frames are integrated over to get one output frame
intensity = IntensityRenderer(t, start_channel=laser, click_channel=cfd1, pixel_begin_channel=pixel, pixels_x=xDim, pixels_y=yDim,
                              n_bins=bins, binwidth=binwidth, pixel_end_channel=pixelEnd, frame_begin_channel=frameStart, num_frames=0, divider=4, is_resonant=True)

# %% Create image view
app = QtGui.QApplication([])

# Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(1024, 800)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()

imv.setPredefinedGradient('viridis')

t.setReplaySpeed(0.7)
replay = t.replay(data_file)

# Update view periodically
while not t.waitForCompletion(timeout=50):
    if (intensity.hasFrames()):
        frame = intensity.getLastFrame()
        imv.setImage(frame.T, levels=(0, 1e6))
        pg.QtGui.QApplication.processEvents()
