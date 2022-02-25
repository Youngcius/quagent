"""
Data acquisition Counter mode
"""
from django.shortcuts import render

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
from functools import partial

from ..utils import *
from ..models import *
from ..globvar import tagger, usr_cnt_map

from TimeTaggerRPC import client
from utils.hardware.host import ipv4, tagger_port

import TimeTagger as tt

print('counter 模块载入')


# JsonResponse = json_response
# JsonError = json_error

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))


n_channels = 8



def counter_page(request):
    interval = int(1e3)  # ps --> ms
    print('interval: ', interval)
    global tagger
    if tagger is None:
        print('...........................................creating tagger...........................................')
        # tagger = tt.createTimeTagger(host=ipv4, port=tagger_port)
        print('available tagger(s):', '=' * 10, tt.scanTimeTagger(), '=' * 10)
        try:
            tagger = tt.createTimeTagger()
        except RuntimeError:
            return HttpResponseServerError('Sorry, The Time Tagger on server is not available now!')

        # for ch in range(1, n_channels + 1):  # simulation signals TODO 改动nchannels
        #     tagger.setTestSignal(ch, True)

    # 查询全局路由表
    avail_channels = get_avail_ch(request.user.username) # e.g. [1, 3], or [5,7,8]

    if len(avail_channels) ==0:
        return HttpResponseServerError('There is not available detection channel(s) for you.\nYou should book some of them first.')
    else:
        return render(request, 'measurement/counter.html', {'channels': avail_channels})


class UserDetector:
    """
    Pair of one User and one Measurement instance
    """
    detector_types = ['Counter', 'CounterBetweenMarkers',
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
        self.detector = getattr(tt, self.mode)(tagger, **self.config)

    def set_measure_config(self, **kwargs):
        """
        Set configuration parameters for some specific measurement mode
        """
        self.config = kwargs


def update_config(request):
    """
    Request: consist user-specific information
    Response: must consist user-specific information, too
    """
    # AJAX    GET

    print(request.GET)
    binwidth = int(request.GET.get('binwidth'))
    n_values = int(request.GET.get('n_values'))
    channels = list(map(int, request.GET.getlist('channels[]')))  #note that there must be a [] in the parameter name
    username = request.user.username

    # create user-specific Counter instance
    user_counter = UserDetector(username, 'Counter')
    user_counter.set_measure_config(**{
        'binwidth': binwidth,
        'n_values': n_values,
        'channels': channels
    })
    user_counter.create_detector(tagger)
    # user_detector_map[username] = {'Counter': user_counter}
    usr_cnt_map[username] = user_counter
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
    print(usr_cnt_map[username])
    return HttpResponse('update successfully')

# TODO: 页面关闭时候 delete user_counter_map[username]

# ====================================================================
# 以下为真实的TimeTagger测试

def start_counter(request):
    username = request.user.username
    # if username in user_detector_map.keys() and 'Counter' in user_detector_map[username].keys():
    if username in usr_cnt_map.keys():
        # counter = user_detector_map[username]['Counter'].detector
        counter = usr_cnt_map[username].detector
        counter.start()
        return HttpResponse('Has started the Counter Measurement')
    else:
        return HttpResponse('There is no Counter instance!')


def stop_counter(request):
    username = request.user.username
    # if username in user_detector_map.keys() and 'Counter' in user_detector_map[username].keys():
    if username in usr_cnt_map.keys():
        # counter = user_detector_map[username]['Counter'].detector
        counter = usr_cnt_map[username].detector
        counter.stop()
        return HttpResponse('Has stopped the Counter Measurement')
    else:
        return HttpResponse('There is no Counter instance!')


def counter_fig(username) -> str:
    line = charts.Line()

    # global counter
    if username in usr_cnt_map.keys():
        counter_config = usr_cnt_map[username].config
        counter = usr_cnt_map[username].detector
        line.add_xaxis(list(range(0, counter_config['n_values'] + 1)))
        if counter.isRunning():
            counts = counter.getData()  # size [num_ch, n_values]
            for i, ch in enumerate(counter_config['channels']):
                line.add_yaxis(series_name='channel {}'.format(ch), y_axis=counts[i].tolist())
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




def get_data(counter):
    data_cache.append(counter.getData())


def counter_download(request):
    """
    根据指定采集时间采集和下载数据
    """
    # 视图响应本身就是多线程？
    username = request.user.username
    if username in usr_cnt_map.keys():
        counter_config = usr_cnt_map[username].config
        counter = usr_cnt_map[username].detector
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
    data_with_config['username'] = username
    data_with_config['measure-mode'] = 'Counter'
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['time'] = T
    data_with_config['data'] = np.hstack(data_cache).tolist()
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    filename = '_'.join(['data', username, str(datetime.date.today()), str(uuid.uuid1()) + '.json'])
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    return response



# TODO
# 图形库，user-specific figure

# TODO
# 每一个新标签页生成一个token uuid

