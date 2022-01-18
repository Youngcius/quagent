from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
import random

from .models import *


# Create your views here.

class EPInfo:
    def __init__(self, idx, info, avail):
        self.idx = idx
        self.avail = avail
        self.info = info


class SPDInfo:
    def __init__(self, idx, avail):
        self.idx = idx
        self.avail = avail


@login_required
def info(request: HttpRequest):
    """
    Display information about channels occupied by the current user
    """
    usr = request.user
    ###############
    # 实际：查询数据库，返回结果
    # TODO: SQL
    ############
    # 模拟
    ep_avails = [bool(random.randint(0, 1)) for i in range(5)]
    # EPS1: signal, idler, sync; EPS2: SPDC photons;
    # EPS3: SPDC photons
    details = [
        'EPs1: signal photons',
        'EPs1: idler photons',
        'EPs1: sync photons',
        'EPs2: SPDC photons',
        'EPs3: SPDC photons'
    ]
    eps_info = [EPInfo(*paras) for paras in zip(range(1, 5 + 1), details, ep_avails)]

    spd_avails = [bool(random.randint(0, 1)) for i in range(4)]
    spds_info = [SPDInfo(*paras) for paras in zip(range(1, 4 + 1), spd_avails)]
    return render(
        request, 'control.html',
        {
            'user': usr,
            'eps': eps_info,
            'spds': spds_info,
        }
    )
