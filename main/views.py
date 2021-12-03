from django.shortcuts import render, HttpResponse


# Create your views here.


def home(request):
    """
    主界面
    """
    if request.user.is_authenticated:
        print('用户已经授权')
        print(request.user)
        request.user
    else:
        print('未授权')
        print(request.user)
    return render(request, 'home.html')
    # return HttpResponse('Hello, this is QUAGENT!')


from django.shortcuts import render

# Create your views here.

import json
from random import randrange

from django.http import HttpResponse
# from rest_framework.views import APIView

from pyecharts.charts import Bar, Pie
from pyecharts.faker import Faker
from pyecharts import options as opts


# Create your views here.
def response_as_json(data):
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


JsonResponse = json_response
JsonError = json_error


def pie_base() -> Pie:
    c = (
        Pie()
            .add("", [list(z) for z in zip(Faker.choose(), Faker.values())])
            .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple"])
            .set_global_opts(title_opts=opts.TitleOpts(title="Pie-示例"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .dump_options_with_quotes()
    )
    return c


# class ChartView(APIView):
#     def get(self, request, *args, **kwargs):
#         return JsonResponse(json.loads(pie_base()))
#
#
# class IndexView(APIView):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse(content=open("./templates/index.html").read())
