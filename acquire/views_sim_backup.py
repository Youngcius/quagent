"""
Data acquisition views functions.
"""
from django.shortcuts import render
from TimeTaggerRPC import client
from utils.hardware.host import ipv4, tagger_port
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse
from django.http import HttpResponseServerError  # 5xx error
import numpy as np
import uuid
import threading
import time
import datetime
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts import charts
import os
import copy
import tempfile
from rest_framework.views import APIView
import json
from random import randrange
from django.contrib.auth.decorators import login_required

from .utils import *

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))

counter_config = {
    'binwidth': int(1e12),  # unit: ps
    'n_values': int(1e3),
    'channels': []
}
n_channels = 8
counter = None
tagger = None


@login_required
def index(request):
    interval = int(counter_config['binwidth'] / 1e9)  # ps --> ms
    print('inverval: ', interval)
    global tagger
    # if tagger is None:
    # tagger = tt.createTimeTagger(host=ipv4, port=tagger_port)
    # tagger = tt.createTimeTagger()
    # for ch in range(1, n_channels + 1):
    #     tagger.setTestSignal(ch, True)

    return render(request, 'acquire.html', {'channels': list(range(1, n_channels + 1)), 'interval': interval})


lister = Lister(counter_config['n_values'])


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
    # 创建 Counter & auto-start
    global counter
    global lister
    lister = Lister(counter_config['n_values'])
    # if counter is None:

    return HttpResponse('update successfully')


#
def start_counter(request):
    # counter.start()
    return HttpResponse('Has started the Counter Measurement')


def stop_counter(request):
    # counter.stop()
    return HttpResponse('Has stopped the Counter Measurement')


# ====================================================================
# 以下是 Example（模拟数据）


def counter_fig() -> str:
    line = charts.Line()
    line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
    for ch in counter_config['channels']:
        line.add_yaxis(series_name='channel {}'.format(ch), y_axis=lister.new())
    line.set_global_opts(title_opts=opts.TitleOpts(title='Counting'),
                         xaxis_opts=opts.AxisOpts(type_='value'),
                         yaxis_opts=opts.AxisOpts(type_='value'))
    fig_str = line.dump_options_with_quotes()

    return fig_str


# JsonResponse = json_response

# class CounterChartView(APIView):
#     def get(self, request, *args, **kwargs):
#         return JsonResponse(json.loads(counter_fig()))


def CounterChartView(request):
    return JsonResponse(json.loads(counter_fig()))


# cnt = 5000


# class CounterChartUpdateView(APIView):
#     def get(self, request, *args, **kwargs):
#         global cnt
#         cnt += 1
#         return JsonResponse({'name': cnt, 'value': randrange(0, 5)})


def CounterChartUpdateView(request):
    # global cnt
    # cnt += 1
    return JsonResponse({'name': 10, 'value': randrange(0, 5)})


data_cache = []


def counter_download(request):
    """
    模拟数据
    """
    # 视图响应本身就是多线程？
    T = float(request.GET.get('T'))  # unit: s
    t = counter_config["binwidth"] * counter_config['n_values'] / 1e12  # ps --> s
    data_cache.clear()  # clear cache firstly

    def get_data():
        data_cache.append(lister.cur())

    N = int(T / t)

    print('下载时间：', T, '单位时间：', t)

    def create_get_data_thread(name=None):
        return threading.Thread(target=get_data, name=name)

    if N == 0:
        thread = create_get_data_thread()
        time.sleep(T)
        thread.start()
        thread.join()
    else:
        for i in range(N + 1):
            thread = create_get_data_thread()
            time.sleep(t)
            thread.start()
            thread.join()

    data_with_config = copy.deepcopy(counter_config)
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['time'] = T
    data_with_config['data'] = np.hstack(data_cache).tolist()
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    fname = 'counting' + str(datetime.date.today()) + str(uuid.uuid4()) + '.json'
    print('==' * 30)
    print('fname: {}'.format(fname))
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(fname)
    return response



# TODO
# 图形库，user-specific figure

# TODO
# 每一个新标签页生成一个token uuid