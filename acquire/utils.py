from django.http import HttpResponse
import json
from random import randrange
import numpy as np


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
