"""
Data acquisition in Correlation mode (Simulation)
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

from ..utils import *


def correlation_page(request):
    return render(request, 'measurement/correlation.html')


# ==================================
# glocal variables
half_N = 30
correlator = Correlator(half_N)
# data_cache = []
correlation_config = {
    'binwidth': int(1e3),  # unit: ps
    'n_bins': half_N * 2,
    'channel 1': 1,
    'channel 2': 2
}


# ==================================


def update_config(request):
    """
    Update measurement parameters
    ---
    - binwidth
    - n_bins
    - channel 1
    - channel 2 (optional)
    """
    pass


def start(request):
    """
    Start data acquisition
    """
    pass


def stop(request):
    """
    Stop data acquisition and display
    """
    pass


def download(request):
    """
    Download real-time data acquired
    """
    T = float(request.GET.get('T'))  # unit: s
    time.sleep(T)

    data_with_config = copy.deepcopy(correlation_config)
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['time'] = T
    data_with_config['index'] = correlator.val
    data_with_config['value'] = correlator.idx
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    fname = 'correlation' + str(datetime.date.today()) + str(uuid.uuid1()) + '.json'
    print('==' * 30)
    print('fname: {}'.format(fname))
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(fname)
    return response


# ===============================


def correlation_fig() -> str:
    """
    diff_t = t(ch1) - t(ch2), ch1 在前则 diff_t 为负数
    """
    hist = charts.Bar()
    hist.add_xaxis([i * correlation_config['binwidth'] for i in correlator.idx])  # time index
    hist.add_yaxis('time diff', correlator.new()[1])  # statistical counts
    hist.set_global_opts(
        title_opts=opts.TitleOpts('Time Correlation Counting'),
        xaxis_opts=opts.AxisOpts(name='time (ps)'),
        yaxis_opts=opts.AxisOpts(type_='value', name='counts')
    )
    fig_str = hist.dump_options_with_quotes()
    return fig_str


def correlation_chart_view(request):
    return JsonResponse(json.loads(correlation_fig()))

def correlation_chart_update_view(request):
    return JsonResponse({'name': 10, 'value': randrange(0, 5)})