
from glob import glob


class TimeTagger:
    def __init__(self):
        self.name = 'TimeTagger'


class UserDetector:
    """
    Pair of one User and one Measurement instance
    """
    detector_types = ['Counter', 'CounterBetweenMarkers',
                      'StartStop', 'Correlation',
                      'TimeDifferences', 'Histogram']

    def __init__(self, username: str, mode: str):
        """
        Initialize object, set its username and measurement mode
        """
        self.username = username
        if mode not in self.detector_types:
            raise ValueError('{} is not a supported measurement mode'.format(mode))
        else:
            self.mode = mode
        self.detector = None
        self.config = None

    def create_detector(self, tagger: TimeTagger):
        """
        :param tagger: Time Tagger instance
        """
        self.detector = getattr(tt, self.mode)(tagger, **self.config)

    def set_measure_config(self, **kwargs):
        """
        Set configuration parameters for some specific measurement mode
        """
        self.config = kwargs



x = 1

def func():
    global x    
    x = x + 2

func()
print(x)


class A:
    a = 10

def func():
    print(A.__name__)

    