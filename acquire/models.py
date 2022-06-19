from typing import List
from django.db.models import Model
from django.contrib.auth.models import User

from hubinfo.models import Laboratory, SPDsLinks

import TimeTagger as tt


def get_avail_ch(usr: User) -> List[int]:
    """
    Query the routing table to get corresponding available channels of the specific user
    :return: a list of integers
    """
    lab = Laboratory.objects.get(lab_name=usr.groups.all()[0])
    res = SPDsLinks.objects.filter(lab=lab, linkage=True, in_use=True)
    return [item.in_ch for item in res]
    # return [1, 2, 4, 5]  # 纯属测试用


class UserDetector:
    """
    Pair of one User and one Measurement instance
    """
    detector_types = ['Counter', 'CountBetweenMarkers',
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

    def create_detector(self, tagger: tt.TimeTagger):
        """
        :param tagger: Time Tagger instance
        """
        if self.config is None:
            raise ValueError('You should set UserDetector.config property before creating it detector instance')
        self.detector = getattr(tt, self.mode)(tagger, **self.config)

    def set_measure_config(self, **kwargs):
        """
        Set configuration parameters for its specific measurement mode
        """
        self.config = kwargs
