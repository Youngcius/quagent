"""
Query data base via iLab API
"""
import threading
import time
import json
import requests
from typing import List, Tuple, Optional
from timeloop import Timeloop
from functools import partial
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

# from .models import UserLabMap, CrossLabUser
from .models import CrossLabQuagentUserMap, labs, labs_id, equipments, equipment_id_to_types
from hubinfo.views import apply_eps_linkage, apply_spds_linkage, release_eps_linkage, release_spds_linkage
from hubinfo.models import EPsLinks, SPDsLinks
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from utils.host import ipv4
from utils.variable import default_password


class Reservation:
    """
    iLab Reservation class
    """

    def __init__(self, start_time: datetime, end_time: datetime, owner: dict, lab: dict, equipment: dict):
        self.start_time = start_time
        self.end_time = end_time
        self.period = (end_time.timestamp() - start_time.timestamp())  # unit: s
        self.owner = owner
        self.lab = lab
        self.equipment = equipment

    @classmethod
    def from_json(cls, reservation: dict):
        """
        From raw JSON (actually Python dict instance) construct a Reservation instance
        """
        return cls(
            start_time=datetime.strptime(reservation['start_time'], '%Y-%m-%d %H:%M'),
            end_time=datetime.strptime(reservation['end_time'], '%Y-%m-%d %H:%M'),
            owner=reservation['owner'],
            lab=reservation['lab'],
            equipment=reservation['equipment']
        )


tl_query = Timeloop()
query_interval = 10  # unit: minute


def query_from_ilab_api(interval=query_interval) -> List[Reservation]:
    """
    Query satisfying reservations whose start time should be in [now, now + interval]
    :param interval: the unit is "minute"
    :return: all satisfying Reservation instances
    """
    dpath = 'static/data/reservations.json'

    now = datetime.now()

    with open(dpath, 'r') as f:
        reservations = json.load(f)['ilab_response']['reservations']
    start_times = [datetime.strptime(res['start_time'], '%Y-%m-%d %H:%M') for res in reservations]
    # end_times = [datetime.strptime(res['end_time'], '%Y-%m-%d %H:%M') for res in reservations]
    all_res = []
    # screen suitable reservations to construct Reservation instances
    for i, start_time in enumerate(start_times):
        if now < start_time < now + timedelta(minutes=interval):
            all_res.append(Reservation.from_json(reservations[i]))
    return all_res


# @tl_query.job(interval=timedelta(seconds=10))
def print_cur_time():
    print(datetime.now())


@tl_query.job(interval=timedelta(seconds=query_interval * 60))
def query_reservation():
    """
    Query reservation information every 15 minutes
    ---
    query information
    send email reminder
    """
    print('===== 执行查询 =====', datetime.now())
    reservations = query_from_ilab_api(query_interval)  # 结果要么是一个 reservation list，要么是 空列表
    print(reservations)
    print([equipment_id_to_types[res.equipment['id']] for res in reservations])
    # 潜在地规定了不能有时间的overlap
    for res in reservations:
        # 定时分配和释放资源
        # check and allocate resources
        user, equipment_type, in_ch = check_resource(res)
        print('For reservation {}, 分配资源: {}, {}, {}'.format(res, user, equipment_type, in_ch))
        time_to_start = int(res.start_time.timestamp() - datetime.now().timestamp())  # unit: s
        print('will {} s later'.format(time_to_start))
        alloc_timer = threading.Timer(time_to_start, partial(allocate_resource, user, in_ch, equipment_type))
        alloc_timer.start()  # after
        # release resources
        rele_timer = threading.Timer(time_to_start + res.period, partial(release_resource, user, in_ch, equipment_type))
        rele_timer.start()
        # send reminder email
        quagent_login_reminder(res)

        print('query done', datetime.now())


def check_resource(reservation: Reservation) -> Optional[Tuple[User, str, int]]:
    """
    Return resource information (user, equipment type, in_ch) or None
    """
    user = CrossLabQuagentUserMap.objects.get(ilab_lab_id=reservation.lab['id']).user
    equipment_type = equipment_id_to_types[reservation.equipment['id']]
    print(user, equipment_type)
    if equipment_type == 'ep':  # 属于 EPs
        links = EPsLinks.objects.filter(user=user)  # links for one user: 5 records or None
        for link in links:
            if link.linkage and not link.in_use:  # 就是当前用户在占据但没有使用
                return user, 'ep', link.in_ch
                # 遇到能用的 in_ch 就 break
            links_same_in_ch = EPsLinks.objects.filter(in_ch=link.in_ch)  # 16 records
            linkages = [l.linkage for l in links_same_in_ch]
            idx = linkages.index(True)
            if not links_same_in_ch[idx].in_use:  # 该 link 一定不是连接着该 user 的
                return user, 'ep', link.in_ch
    if equipment_type == 'spd':  # 属于 SNSPDs
        links = SPDsLinks.objects.filter(user=user)  # links for one user: 4 records or None
        for link in links:
            if link.linkage and not link.in_use:
                return user, 'spd', link.in_ch
            links_same_in_ch = SPDsLinks.objects.filter(in_ch=link.in_ch)  # 8 records
            linkages = [l.linkage for l in links_same_in_ch]
            idx = linkages.index(True)
            if not links_same_in_ch[idx].in_use:  # 该 link 一定不是连接着该 user 的
                return user, 'spd', link.in_ch
    return None


def allocate_resource(user: User, in_ch: int, equipment_type: str):
    print('===================', datetime.now(), 'has allocated:', equipment_type)
    if equipment_type == 'ep':
        link = EPsLinks.objects.get(user=user, in_ch=in_ch)
        print(link)
        apply_eps_linkage(in_ch, link.out_ch)
    if equipment_type == 'spd':
        link = SPDsLinks.objects.get(user=user, in_ch=in_ch)
        apply_spds_linkage(in_ch, link.out_ch)


def release_resource(user: User, in_ch: int, equipment_type: str):
    """
    Release `equipment_type` resource
    """
    print('===================', datetime.now(), 'has release:', equipment_type)
    if equipment_type == 'ep':
        link = EPsLinks.objects.get(user=user, in_ch=in_ch)
        release_eps_linkage(in_ch, link.out_ch)
    if equipment_type == 'spd':
        link = SPDsLinks.objects.get(user=user, in_ch=in_ch)
        release_spds_linkage(in_ch, link.out_ch)


def quagent_login_reminder(reservation: Reservation):
    """
    Email to reminder user to login Quagent after 15 minutes
    """
    user = CrossLabQuagentUserMap.objects.get(ilab_lab_id=reservation.lab['id']).user
    time_idle = int((datetime.now().timestamp() - reservation.start_time.timestamp()) / 60)
    recipient_list = [reservation.owner['email']]

    subject = '[Quagent] Reminder and Login URL to use Interdisciplinary Quantum Information Research and Engineering Facility'
    message = """
    This is a reminder about a reservation on INQUIRE facility The reservation starts in about {} minutes.

    Temporary user ID: {}
    Temporary user password: {}

    Appointment information:
        Start time: {}
        End time: {}
        Scheduled equipment: {}

    Use this website to login our the web operation platform: <a href="http://{}:8000/">[Quagent]</a>
    """.format(
        time_idle,
        user.username, default_password,
        reservation.start_time.strftime('%Y-%m-%d %H:%M'), reservation.end_time.strftime('%Y-%m-%d %H:%M'),
        reservation.equipment['name'],
        ipv4
    )
    send_mail(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        message=message
    )
