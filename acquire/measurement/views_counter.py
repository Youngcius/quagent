"""
Data acquisition Counter mode
"""
from django.shortcuts import render
from TimeTaggerRPC import client
from utils.hardware.host import ipv4, tagger_port
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse, Http404
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

from ..utils import *
from ..models import *

# JsonResponse = json_response
# JsonError = json_error

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))
#
# counter_config = {
#     'binwidth': int(1e12),  # unit: ps
#     'n_values': int(1e3),
#     'channels': []
# }
n_channels = 8
counter = None
tagger = None

# tt = client.createProxy(host=ipv4, port=tagger_port)

import TimeTagger as tt


def index(request):
    interval = int(1e3)  # ps --> ms
    print('interval: ', interval)
    global tagger
    if tagger is None:
        print('...........................................creating...........................................')
        # tagger = tt.createTimeTagger(host=ipv4, port=tagger_port)
        print('=' * 20, tt.scanTimeTagger(), '=' * 20)
        tagger = tt.createTimeTagger()
        for ch in range(1, n_channels + 1):  # simulation signals
            tagger.setTestSignal(ch, True)
        # print(tagger,type(tagger))

    print(tagger)
    if request.user.username not in user_detector_map.keys():
        user_detector_map[request.user.username] = {}
    return render(request, 'acquire.html', {'channels': list(range(1, n_channels + 1)), 'interval': interval})


# lister = Lister(counter_config['n_values'])

from typing import Callable


class UserDetector:
    """
    Pair of one User and one Measurement instance
    """
    detector_types = ['Counter', 'Correlation',
                      'StartStop', 'CounterBetweenMarker',
                      'TimeDifferences', 'Histogram', 'Flim']

    def __init__(self, username: str):
        self.username = username
        self.type = type
        self.detector = None
        self.config = None

    def create_detector(self, create_func: Callable):
        """
        create_func: Callable, e.g. TimeTagger.Counter
        """
        self.detector = create_func(**self.config)

    def set_measure_config(self, **kwargs):
        self.config = kwargs


user_detector_map = {}


def update_config(request):
    # AJAX    GET
    print(request.GET)
    binwidth = int(request.GET.get('binwidth'))
    n_values = int(request.GET.get('n_values'))
    channels = list(map(int, request.GET.getlist('channels[]')))  # 注意参数名这里有个 []
    # channels_str = ''.join(request.GET.getlist('channels[]'))
    username = request.user.username
    # create user-specific Counter instance
    user_counter = UserDetector(username)
    user_counter.set_measure_config(**{
        'binwidth': binwidth,
        'n_values': n_values,
        'channels': channels
    })
    user_counter.create_detector(tt.Counter)
    user_detector_map[username] = {'Counter': user_counter}

    # ==================
    # user_counter_conf = Counter.objects.filter(user=username)
    # TODO: in shell verify the type? None?
    # if user_counter_conf:
    # 非空时候，更新 user-specific counter_config
    # user_counter_conf.binwidth = binwidth
    # user_counter_conf.n_values = n_values
    # user_counter_conf.channels = list_to_string(channels)
    # user_counter_conf.save()
    # else:
    # 创建
    # user_counter_conf = Counter(
    #     binwidth=binwidth,
    #     n_values=n_values,
    #     channels=list_to_string(channels)
    # )
    # user_counter_conf.save()

    # counter_config['binwidth'] = binwidth
    # counter_config['n_values'] = n_values
    # counter_config['channels'] = channels

    # print(counter_config)
    # 创建 Counter & auto-start
    # global counter
    # global lister
    # lister = Lister(counter_config['n_values'])
    # if counter is None:
    # counter_list = [
    #     tt.Counter(tagger, counter_config['channels'], binwidth=counter_config['binwidth'],
    #                n_values=counter_config['n_values'])
    #     for i in range(n_channels)
    # ]
    # for i in range()
    # counter = tt.Counter(tagger, counter_config['channels'], binwidth=counter_config['binwidth'],
    #                      n_values=counter_config['n_values'])
    print(user_detector_map[username]['Counter'])
    return HttpResponse('update successfully')


# ====================================================================
# 以下为真实的TimeTagger测试

def start_counter(request):
    username = request.user.username
    if username in user_detector_map.keys() and 'Counter' in user_detector_map[username].keys():
        counter = user_detector_map[username]['Counter'].detector
        counter.start()
        return HttpResponse('Has started the Counter Measurement')
    else:

        return HttpResponse('There is no Counter instance!')


def stop_counter(request):
    username = request.user.username
    if username in user_detector_map.keys() and 'Counter' in user_detector_map[username].keys():
        counter = user_detector_map[username]['Counter'].detector
        counter.stop()
        return HttpResponse('Has stopped the Counter Measurement')
    else:
        return HttpResponse('There is no Counter instance!')


def counter_fig(username) -> str:
    line = charts.Line()

    # global counter
    if username in user_detector_map.keys():
        if 'Counter' in user_detector_map[username].keys():
            counter_config = user_detector_map[username]['Counter'].config
            counter = user_detector_map[username]['Counter'].detector
            line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
            if counter.isRunning():
                counting = counter.getData()  # size [num_ch, n_values]
                for i, ch in enumerate(counter_config['channels']):
                    line.add_yaxis(series_name='channel {}'.format(ch), y_axis=counting[i].tolist())
    line.set_global_opts(
        title_opts=opts.TitleOpts(title='Counting'),
        xaxis_opts=opts.AxisOpts(type_='value'),
        yaxis_opts=opts.AxisOpts(type_='value'),

    )
    fig_str = line.dump_options_with_quotes()
    return fig_str


# class CounterChartView(APIView):
#     def get(self, request, *args, **kwargs):
#         return JsonResponse(json.loads(counter_fig()))
def counter_chart_view(request):
    return JsonResponse(json.loads(counter_fig(request.user.username)))


data_cache = []
# cnt = counter_config['n_values']


# class CounterChartUpdateView(APIView):
#     def get(self, request, *args, **kwargs):
#         global cnt
#         cnt += 1
#         return JsonResponse({'name': cnt, 'value': randrange(0, 100)})

# def counter_chart_update_view(request):
#     cnt = user_detector_map[request.user.username]
#     cnt += 1
#     return JsonResponse({'name': cnt, 'value': randrange(0, 100)})
#

from functools import partial


def get_data(counter):
    data_cache.append(counter.getData())


def counter_download(request):
    """
    根据指定采集时间采集和下载数据
    """
    # 视图响应本身就是多线程？
    username = request.user.username
    if username in user_detector_map.keys() and 'Counter' in user_detector_map[username]['Counter']:
        counter_config = user_detector_map[username]['Counter'].config
        counter = user_detector_map[username]['Counter'].detector
    else:
        return Http404('no Counter instance running')
    T = float(request.GET.get('T'))  # unit: s
    t = counter_config["binwidth"] * counter_config['n_values'] / 1e12  # ps --> s
    data_cache.clear()  # clear cache firstly
    N = int(T / t)

    print('==' * 30)
    print('下载时间：', T, '单位时间：', t)

    def create_get_data_thread(name=None):
        return threading.Thread(target=get_data, args=[counter], name=name)

    if N == 0:
        thread = create_get_data_thread()
        time.sleep(T)
        thread.start()
    else:
        for i in range(N + 1):
            thread = create_get_data_thread()
            time.sleep(t)
            thread.start()

    data_with_config = copy.deepcopy(counter_config)
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['time'] = T
    data_with_config['data'] = np.hstack(data_cache).tolist()
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    response['Content-Disposition'] = 'attachment;filename={}'.format(
        'counting' + str(datetime.date.today()) + str(uuid.uuid1()) + '.json')
    return response
