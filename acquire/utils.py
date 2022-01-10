from django.http import HttpResponse
import json
from random import randrange
import numpy as np
from numpy.core.fromnumeric import size
from scipy.stats import norm


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
