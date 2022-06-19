"""
Query data base via iLab API
"""
import threading
from timeloop import Timeloop
from functools import partial
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

from hubinfo.views import apply_eps_linkage, apply_spds_linkage, release_eps_linkage, release_spds_linkage
from hubinfo.models import EPsLinks, SPDsLinks
from utils.host import ipv4
from .models import Reservation, Laboratory

tl_query = Timeloop()
query_interval = 10  # unit: minute


@tl_query.job(interval=timedelta(seconds=query_interval * 60))
def query_reservation():
    """
    Query reservation information every 15 minutes
    ---
    query information
    send email reminder
    """
    print('===== 执行查询 =====', datetime.now())
    now = datetime.now()
    interval = timedelta(minutes=query_interval)  # interval threshold
    reservations = Reservation.objects.filter(start_time__gte=now, start_time__lte=now + interval)
    print('Current time {}, Reservations: {}'.format(now, reservations))

    for res in reservations:
        lab = Laboratory.objects.get(lab_name=res.user.groups.all()[0])

        # allocate/release resources via timer
        inter = res.start_time - now  # actual interval
        resource = res.resource
        print('For reservation {}:: user: {}, ch: {}, resource: {}, interval: {}'.format(res, res.user, res.in_ch,
                                                                                         res.resource, inter))
        if resource == 'ep':
            link = EPsLinks.objects.get(lab=lab, in_ch=res.in_ch)
            alloc_timer = threading.Timer((res.start_time - now).seconds,
                                          partial(apply_eps_linkage, link.in_ch, link.out_ch))
            rele_timer = threading.Timer((res.end_time - now).seconds,
                                         partial(release_eps_linkage, link.in_ch, link.out_ch))

        else:
            link = SPDsLinks.objects.get(lab=lab, in_ch=res.in_ch)
            alloc_timer = threading.Timer((res.start_time - now).seconds,
                                          partial(apply_spds_linkage, link.in_ch, link.out_ch))
            rele_timer = threading.Timer((res.end_time - now).seconds,
                                         partial(release_spds_linkage, link.in_ch, link.out_ch))
        alloc_timer.start()
        rele_timer.start()

        # send reminder email
        quagent_login_reminder(res)

    print('===== query done =====', datetime.now())


def quagent_login_reminder(reservation: Reservation):
    """
    Email to reminder user to login Quagent after 15 minutes
    """
    subject = '[Quagent] Reminder and Login URL to use Interdisciplinary Quantum Information Research and Engineering Facility'

    message = """
    <p>
        This is a reminder about a reservation on INQUIRE facility The reservation starts in about {} minutes.
    </p>
    
    <p>
        <strong>Appointment information:</strong>
    <ul>
        <li>Instrument resource: {}</li>
        <li>Channel: {}</li>
        <li>Start time: {}</li>
        <li>End time: {}</li>
    </ul>
    
    </p>
    
    <p>
        Use this website to login our the web operation platform: <a href="http://{}:8000/">[Quagent]</a>
    </p>
    """.format(
        int((reservation.start_time - datetime.now()).seconds / 60),
        'Entangled-Photon Source' if reservation.resource == 'ep' else 'Single-Photon Detector',
        reservation.in_ch,
        reservation.start_time.strftime('%Y-%m-%d %H:%M'), reservation.end_time.strftime('%Y-%m-%d %H:%M'),
        ipv4
    )
    send_mail(
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipient_list=[reservation.user.email],
        message='',
        html_message=message
    )
