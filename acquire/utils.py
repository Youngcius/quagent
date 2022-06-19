import json
import time
import threading
import numpy as np
from django.http import HttpResponse
from random import randrange
from scipy.stats import norm

unit_to_num = {
    's': 1,
    'ms': 1e-3,
    'us': 1e-6,
    'ns': 1e-9,
    'ps': 1e-12
}


def response_as_json(data):
    # dumps: dict --> str
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


def string_to_list(s):
    """
    e.g. '124' --> [1, 2, 4]
    """
    return list(map(int, list(s)))


def list_to_string(l):
    """
    e.g. [1, 2, 4] --> '124'
    """
    return ''.join(list(map(str, l)))


class Lister:
    def __init__(self, N: int):
        self.l = np.random.randint(0, 100, N).tolist()

    def new(self):
        a = randrange(0, 100)
        self.l = self.l[1:] + [a]
        return self.l

    def cur(self):
        return self.l


class Correlator:
    def __init__(self, half_N: int):
        self.idx = np.arange(-half_N, half_N).tolist()
        self.val = norm.pdf(self.idx, loc=0, scale=half_N / 2).tolist()

    def new(self):
        self.randomize()
        return self.idx, self.val

    def cur(self):
        return self.idx, self.val

    def randomize(self):
        half_N = int(len(self.idx) / 2)
        replaced_num = int(0.1 * half_N)
        replaced_idx = np.random.choice(self.idx, size=replaced_num, replace=False).tolist()
        self.val = np.array(self.val)
        self.val[replaced_idx] = self.val[replaced_idx] * (1 + np.random.randn(replaced_num) * 0.1)
        self.val = np.abs(self.val)
        self.val = self.val.tolist()


def get_data(detector, cache):
    cache.append(detector.getData())


def get_data_in_long_time(detector, T, t):
    """
    Get data in a long time interval
    :param detector: Measurement instance defined in TimeTagger library
    :param t: time interval for slicing the T if T is too large
    :return: a list whose elements are also lists
    """
    data_cache = []
    N = int(T / t)
    if N == 0:
        thread = threading.Thread(target=get_data, args=[detector, data_cache])
        time.sleep(T)
        thread.start()
    else:
        for i in range(N + 1):
            thread = threading.Thread(target=get_data, args=[detector, data_cache])
            time.sleep(t)
            thread.start()

    time.sleep(5)
    return data_cache


def cal_max_min_limits(arr, extend=0.05):
    max_val, min_val = np.max(arr), np.min(arr)
    max_val += extend * (max_val - min_val)
    min_val -= extend * (max_val - min_val)
    max_val, min_val = np.ceil(max_val), int(min_val)
    return max_val, min_val
