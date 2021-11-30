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

from .utils import *

# JsonResponse = json_response
# JsonError = json_error

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))

counter_config = {
    'binwidth': int(1e12),  # unit: ps
    'n_values': int(1e3),
    'channels': []
}
n_channels = 8
counter = None
tagger = None

# tt = client.createProxy(host=ipv4, port=tagger_port)

import TimeTagger as tt


def index(request):
    interval = int(counter_config['binwidth'] / 1e9)  # ps --> ms
    print('inverval: ', interval)
    global tagger
    if tagger is None:
        print('creating...........................................')
        # tagger = tt.createTimeTagger(host=ipv4, port=tagger_port)
        print('=' * 20, tt.scanTimeTagger(), '=' * 20)
        tagger = tt.createTimeTagger()
        for ch in range(1, n_channels + 1):  # simulation signals
            tagger.setTestSignal(ch, True)
        print(tagger,type(tagger))

    print(tagger)

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
    counter = tt.Counter(tagger, counter_config['channels'], binwidth=counter_config['binwidth'],
                         n_values=counter_config['n_values'])

    return HttpResponse('update successfully')


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

#
# def free_tagger():
#     # global tagger
#     pass
#
#
def start_counter(request):
    if counter is None:
        return HttpResponse('There is no Counter instance!')
    else:
        counter.start()
        return HttpResponse('Has started the Counter Measurement')


def stop_counter(request):
    if counter is None:
        return HttpResponse('There is no Counter instance!')
    else:
        counter.stop()
        return HttpResponse('Has stopped the Counter Measurement')


def counter_fig() -> str:
    line = charts.Line()
    line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
    # global counter
    if counter is not None and counter.isRunning():
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


data_cache = []
cnt = counter_config['n_values']


class CounterChartUpdateView(APIView):
    def get(self, request, *args, **kwargs):
        global cnt
        cnt += 1
        return JsonResponse({'name': cnt, 'value': randrange(0, 100)})


def get_data():
    data_cache.append(counter.getData())


def counter_download(request):
    """
    根据指定采集时间采集和下载数据
    """
    # 视图响应本身就是多线程？
    T = float(request.GET.get('T'))  # unit: s
    t = counter_config["binwidth"] * counter_config['n_values'] / 1e12  # ps --> s
    data_cache.clear()  # clear cache firstly
    N = int(T / t)

    print('==' * 30)
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
    response['Content-Disposition'] = 'attachment;filename={}'.format(
        'counting' + str(datetime.date.today()) + str(uuid.uuid4()) + '.json')
    return response
