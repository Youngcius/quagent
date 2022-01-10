"""
Data acquisition in StartStop mode (Simulation)
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


def startstop_page(request):

    return render(request, 'measurement/startstop.html')


def update_config(request):
    """
    Update measurement parameters
    ---
    - click channel
    - start channel
    - binwidth
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
    pass

# =====================
correlator = Correlator(half_N=250)


def startstop_fig()->str:
    hist = charts.Bar()
    hist.add_xaxis(correlator.idx)  # time index
    hist.add_yaxis('time diff', correlator.new()[1])  # statistical counts
    hist.set_global_opts(
        title_opts=opts.TitleOpts('StartStop Time Diff Counting'),
        xaxis_opts=opts.AxisOpts(name='time (ps)'),
        yaxis_opts=opts.AxisOpts(type_='value', name='counts'),
        datazoom_opts=opts.DataZoomOpts()
    )
    fig_str = hist.dump_options_with_quotes()
    return fig_str


def startstop_chart_view(request):
    return JsonResponse(json.loads(startstop_fig()))

def startstop_chart_update_view(request):
    return JsonResponse({'name': 10, 'value': randrange(0, 5)})