"""
Data acquisition views functions.
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

from .utils import *
from .models import *


def select(request):
    """
    Select one kind of Measurement experiment
    """

    return render(request, 'select.html')

#
# class CounterBetweenMarker(Model):
#     pass
#
#
# class Correlation(Model):
#     pass
#
#
# class Countrate(Model):
#     pass
#
#
# class Histogram(Model):
#     pass
#
#
# class StartStop(Model):
#     pass
#
#
# class TimeDifferences(Model):
#     pass
#
#
# class Film(Model):
#     pass

