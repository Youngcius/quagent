"""
Data acquisition views functions.
"""
from django.shortcuts import render
from TimeTaggerRPC import client
from utils.hardware.host import ipv4, tagger_port
from django.http import HttpRequest, HttpResponse
import numpy as np
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts import charts
import os
from rest_framework.views import APIView
import json
from random import randrange

from .utils import *

JsonResponse = json_response
JsonError = json_error

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))

counter_config = {
    'binwidth': int(1e12),  # unit: ps
    'n_values': int(1e3),
    'channels': []
}
n_channels = 8
counter = None
tagger = None
tt = client.createProxy(host=ipv4, port=tagger_port)


def index(request):
    interval = int(counter_config['binwidth'] / 1e9)  # ps --> ms
    global tagger
    if tagger is None:
        tagger = tt.createTimeTagger(host=ipv4, port=tagger_port)
        for ch in range(1, n_channels + 1):
            tagger.setTestSignal(ch, True)

    return render(request, 'acquire.html', {'channels': list(range(1, n_channels + 1)), 'interval': interval})


def update_config(request):
    # AJAX    GET
    print(request.GET)
    binwidth = int(request.GET.get('binwidth'))
    n_values = int(request.GET.get('n_values'))
    channels = list(map(int, request.GET.getlist('channels[]')))  # 注意参数名这里有个 []
    counter_config['binwidth'] = binwidth
    counter_config['n_values'] = n_values
    counter_config['channels'] = channels

    print(counter_config)
    # 创建 Counter
    global counter
    # if counter is None:
    counter = tt.Counter(tagger, counter_config['channels'], binwidth=counter_config['binwidth'],
                         n_values=counter_config['n_values'])
    counter.stop()

    return HttpResponse('update successfully')


# ====================================================================
# 以下是 Example（模拟数据）
#
# lister = Lister(50)
#
#
# def counter_fig() -> str:
#     line = charts.Line()
#     line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
#     for ch in counter_config['channels']:
#         line.add_yaxis(series_name='channel {}'.format(ch), y_axis=lister.new())
#     line.set_global_opts(title_opts=opts.TitleOpts(title='Counting'),
#                          xaxis_opts=opts.AxisOpts(type_='value'),
#                          yaxis_opts=opts.AxisOpts(type_='value'))
#     fig_str = line.dump_options_with_quotes()
#
#     return fig_str
#
#
# class CounterChartView(APIView):
#     def get(self, request, *args, **kwargs):
#         return JsonResponse(json.loads(counter_fig()))
#
#
# cnt = 5000
#
#
# class CounterChartUpdateView(APIView):
#     def get(self, request, *args, **kwargs):
#         global cnt
#         cnt += 1
#         return JsonResponse({'name': cnt, 'value': randrange(0, 5)})

# ====================================================================
# 以下为真实的TimeTagger测试

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


def free_tagger():
    # global tagger
    pass


def start_counter(request):
    counter.start()
    return HttpResponse('Has started the Counter Measurement')


def stop_counter():
    counter.stop()
    return HttpResponse('Has stopped the Counter Measurement')


def counter_fig() -> str:
    line = charts.Line()
    line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
    # global counter
    counting = counter.getData()
    for i, ch in enumerate(counter_config['channels']):
        line.add_yaxis(series_name='channel {}'.format(ch), y_axis=counting[0].tolist())
    line.set_global_opts(
        title_opts=opts.TitleOpts(title='Counting'),
        xaxis_opts=opts.AxisOpts(type_='value'),
        yaxis_opts=opts.AxisOpts(type_='value'),

    )
    fig_str = line.dump_options_with_quotes()
    return fig_str


class CounterChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(counter_fig()))


cnt = counter_config['n_values']


class CounterChartUpdateView(APIView):
    def get(self, request, *args, **kwargs):
        global cnt
        cnt += 1
        return JsonResponse({'name': cnt, 'value': randrange(0, 100)})
