"""
Data acquisition in TimdeDifferences mode (Simulation)
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

def timedifferences_page(request):

    return render(request, 'measurement/timedifferences.html')


def update_config(request):
    """
    Update measurement parameters
    ---
    - click channel
    - start channel
    - next channel
    - sync channel (optional)
    - binwidth
    - n_bins
    - n_histogram
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




# =================


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
# ==============

def correlation_fig() ->str:


