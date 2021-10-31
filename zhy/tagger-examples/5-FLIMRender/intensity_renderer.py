import TimeTagger
import numpy
import numba

# Create a new IntensityRenderer based on the TimeDifferencesRender backend class


class IntensityRenderer(TimeTagger.FlimBase):

    def __init__(self, tagger, start_channel, click_channel, pixel_begin_channel, pixels_x, pixels_y, n_bins, binwidth, pixel_end_channel=TimeTagger.CHANNEL_UNUSED, frame_begin_channel=TimeTagger.CHANNEL_UNUSED, num_frames=0, divider=1, is_resonant=False):
        TimeTagger.FlimBase.__init__(self, tagger, start_channel, click_channel, pixel_begin_channel,
                                     pixels_x * pixels_y, n_bins, binwidth, pixel_end_channel, frame_begin_channel, num_frames, divider, False)
        self.pixels_x = pixels_x
        self.pixels_y = pixels_y
        self.frames = []
        self.bins = n_bins
        self.is_resonant = is_resonant

        # When inheriting from a measurement, initialization must be done manually and after all
        # needed variables/resources are initialized.
        self.initialize()

    # render will be called by the backend every time it finishes a frame, the backend
    # will pass the current histogram as read-only(shouldn't be modified). This method
    # will then use the current histogram to generate a frame and store it. Due to the speed
    # needs of this class, it is suggested to break it into smaller functions and use numba, so
    # most hard processing is done as fast as possible
    def frameReady(self, frame_number, frame_data, pixels_start_times, pixels_end_times, frame_start_time, frame_end_time):
        # the received data isd a 1 dimensional array of [pixels_x * pixels_y * bins]
        # we must reshape it.
        alt_data = frame_data.reshape(self.pixels_y, self.pixels_x, self.bins)
        alt_pixel_start_times = pixels_start_times.reshape(
            self.pixels_y, self.pixels_x)
        alt_pixel_end_times = pixels_end_times.reshape(self.pixels_y, self.pixels_x)
        frame = numpy.empty([self.pixels_y - 1, self.pixels_x - 1])
        # intensity is calculated differently in resonant and non resonant scan,
        # for resonant we must alternate the lines direction every odd line.
        if (not self.is_resonant):
            IntensityRenderer.__calculate_intensity(
                alt_data, frame, alt_pixel_start_times, alt_pixel_end_times, False)
        else:
            IntensityRenderer.__calculate_intensity(
                alt_data, frame, alt_pixel_start_times, alt_pixel_end_times, True)
        self.frames.append(frame)

    def getFrames(self):
        return self.frames

    def hasFrames(self):
        return len(self.frames) != 0

    def getLastFrame(self):
        return self.frames[-1]

    # This function calculates the intensity as the sum of all the histogram.
    # Special care has been taken in order to make sure it compiles in numba.
    # Among those things: set it as static method, only use numpy arrays,
    # don't use lists, dictionaries or complex python types, etc.
    @staticmethod
    @numba.jit(nopython=True, nogil=True)
    def __calculate_intensity(data, frame, start_pixel_times, end_pixel_times, flip):
        for y in range(1, data.shape[0]):
            if ((not flip) or y % 2 == 0):
                for x in range(1, data.shape[1]):
                    sum = 0
                    for b in range(0, data.shape[2]):
                        sum = sum + data[y][x][b]
                    frame[y - 1][x - 1] = (end_pixel_times[y]
                                           [x] - start_pixel_times[y][x]) * sum
            else:
                for x in range(data.shape[1] - 1, 0, -1):
                    sum = 0
                    for b in range(0, data.shape[2]):
                        sum = sum + data[y][x][b]
                    frame[y - 1][frame.shape[1] -
                                 x] = (end_pixel_times[y][x] - start_pixel_times[y][x]) * sum
