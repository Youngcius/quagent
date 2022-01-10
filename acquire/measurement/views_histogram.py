"""
Data acquisition in Histogram mode
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
