from django.shortcuts import render
# from TimeTaggerRPC import client
from utils.hardware.host import ipv4, tagger_port
from django.http import HttpRequest, HttpResponse

# Create your views here.
##################
# Tagger Counter 表单功能设定


counter_config = {
    'binwidth': int(1e12),  # unit: ps
    'n_values': int(1e3),
    # 'channels': [1, 3, 5],
    'channels': []
}

counter = None


def update_config(request: HttpRequest):
    """
    更新参数
    """

    # form 表单形式
    # binwidth = request.POST.get(key='binwidth')
    # n_values = request.POST.get(key='n_values')
    # channels = request.POST.getlist(key='channels')
    # binwidth = int(request.GET.get('binwidth'))
    # n_values = int(request.GET.get('n_values'))
    # channels = list(map(int, request.GET.getlist('channels')))
    # print(binwidth)
    # print(n_values)
    # print('new channels:', channels, type(channels))
    # counter_config['binwidth'] = binwidth
    # counter_config['n_values'] = n_values
    # counter_config['channels'] = channels
    # # 没有返回HTTP响应
    # # pass
    # interval = int(counter_config['binwidth'] / 1e9)  # ps --> ms
    # print('interval:', interval)
    # return render(request, 'tagger.html', {'channels': list(range(1, 9)), 'interval': interval})

    # AJAX 形式 / fetch
    print('------------=================')
    print('----------',request.GET)
    binwidth = int(request.GET.get('binwidth'))
    n_values = int(request.GET.get('n_values'))
    channels = list(map(int, request.GET.getlist('channels'))) # 注意参数名这里有个 []
    counter_config['binwidth'] = binwidth
    counter_config['n_values'] = n_values
    counter_config['channels'] = channels

    print(counter_config)

    return HttpResponse('update successfully')


def measure_display(request):
    """
    实时显示数据图像
    """
    tt = client.createProxy(host=ipv4, port=tagger_port)
    tagger = tt.createTimeTagger()
    counter = tt.Counter(tagger, counter_config["channels"], binwidth=counter_config['binwidth'],
                         n_values=counter_config['n_values'])
    # tagger.setTestSignal(1, True)
    # tagger.setTestSignal(2, True)


N = 50
import numpy as np


class Lister:
    def __init__(self):
        self.l = np.random.randint(0, 100, N).tolist()

    def new(self):
        a = randrange(0, 100)
        self.l = self.l[1:] + [a]
        return self.l


lister = Lister()
lister2 = Lister()

from pyecharts import charts


def counter_fig() -> str:
    line = Line()
    line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
    for ch in counter_config['channels']:
        line.add_yaxis(series_name='channel {}'.format(ch), y_axis=lister.new())
    line.set_global_opts(title_opts=opts.TitleOpts(title='Counting'),
                         xaxis_opts=opts.AxisOpts(type_='value'),
                         yaxis_opts=opts.AxisOpts(type_='value'))
    fig_str = line.dump_options_with_quotes()

    return fig_str


from rest_framework.views import APIView


class CounterChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(counter_fig()))


cnt = N


class CounterChartUpdateView(APIView):
    def get(self, request, *args, **kwargs):
        global cnt
        cnt += 1
        return JsonResponse({'name': cnt, 'value': randrange(0, 100)})


# def tagger(request: HttpRequest):

# return render(request, 'tagger.html', {'channels': list(range(1, 9))})
# class TaggerView(APIView):
#     def get(self, request, *args, **kwargs):
#         interval = int(counter_config['binwidth'] / 1e9)  # ps --> ms
#         return render(request, 'tagger.html', {'channels': list(range(1, 9)), 'interval': interval})

def tagger_demo(request):
    interval = int(counter_config['binwidth'] / 1e9)  # ps --> ms
    print('interval:', interval)
    return render(request, 'tagger.html', {'channels': list(range(1, 9)), 'interval': interval})


# def line_base() -> Line:
#     line = (
#         Line()
#             .add_xaxis(list(range(N)))
#             .add_yaxis(series_name="List 1", y_axis=lister.new())  # y_axis=[randrange(0, 100) for _ in range(N)])
#             .add_yaxis(series_name="List 2", y_axis=lister2.new())
#             .set_global_opts(
#             title_opts=opts.TitleOpts(title="动态数据"),
#             xaxis_opts=opts.AxisOpts(type_="value"),
#             yaxis_opts=opts.AxisOpts(type_="value")
#         )
#             .dump_options_with_quotes()
#     )
#     return line
#
#
# class LineChartView(APIView):
#     def get(self, request, *args, **kwargs):
#         return JsonResponse(json.loads(line_base()))
#
#
# cnt = 9
#
#
# class LineChartUpdateView(APIView):
#     def get(self, request, *args, **kwargs):
#         global cnt
#         cnt = cnt + 1
#         return JsonResponse({"name": cnt, "value": randrange(0, 100)})
#
#
# class LineIndexView(APIView):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse(content=open("./template/refresh.html").read())

# ==================================================================

#
# def create_tagger():
#     with client.createProxy(host=ipv4, port=tagger_port) as TT:
#         tagger = TT.createTimeTagger()
#         tagger.setTestSignal(1, True)
#         tagger.setTestSignal(2, True)
#
#         hist = TT.Correlation(tagger, 1, 2, binwidth=5, n_bins=2000)
#         hist.startFor(int(10e12), clear=True)
#
#         x = hist.getIndex()
#         while hist.isRunning():
#             plt.pause(0.1)
#             y = hist.getData()
#             plt.cla()
#             plt.plot(x, y)
#
#         TT.freeTimeTagger(tagger)


from django.http import HttpResponse
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))
from pyecharts import options as opts
from pyecharts.charts import Bar

import os


def index(request):
    # return HttpResponse('Acquire')
    title_opts = opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题")
    c = (Bar().add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]).add_yaxis("商家A", [5, 20, 36, 10, 75, 90]).add_yaxis(
        "商家B",
        [15,
         25,
         16,
         55,
         48,
         8]).set_global_opts(title_opts=title_opts))
    # c.render()
    # return HttpResponse(c.render(template_name='simple_chart.html'))
    # print(os.getcwd())
    return HttpResponse(c.render_embed())


def separate(request):
    """
    前后端分离
    """
    pass


def timely(request):
    """
    定量实时刷新
    """
    pass


import json
from random import randrange

from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Bar
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


def bar_base() -> Bar:
    c = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
            .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
            .dump_options_with_quotes()
    )
    return c


class BarChartView(APIView):
    # 后端数据绘图
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class BarIndexView(APIView):
    # 前端展示
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./template/separate.html").read())


# Create your views here.


# 前后端分离 实时刷新
import json
from random import randrange

from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Line
from pyecharts import options as opts


class Lister:
    def __init__(self):
        self.l = np.random.randint(0, 100, N).tolist()

    def new(self):
        a = randrange(0, 100)
        self.l = self.l[1:] + [a]
        return self.l


def line_base() -> Line:
    line = (
        Line()
            .add_xaxis(list(range(N)))
            .add_yaxis(series_name="List 1", y_axis=lister.new())  # y_axis=[randrange(0, 100) for _ in range(N)])
            .add_yaxis(series_name="List 2", y_axis=lister2.new())
            .set_global_opts(
            title_opts=opts.TitleOpts(title="动态数据"),
            xaxis_opts=opts.AxisOpts(type_="value"),
            yaxis_opts=opts.AxisOpts(type_="value")
        )
            .dump_options_with_quotes()
    )
    return line


class LineChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(line_base()))


cnt = 9


class LineChartUpdateView(APIView):
    def get(self, request, *args, **kwargs):
        global cnt
        cnt = cnt + 1
        return JsonResponse({"name": cnt, "value": randrange(0, 100)})


class LineIndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./template/refresh.html").read())
