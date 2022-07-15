import csv
import uuid
from datetime import datetime
from django.apps import AppConfig
from utils.variable import default_password, default_email
from utils.switch import ep_switch, spd_switch


class HubinfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hubinfo'
    verbose_name = 'User Hub Information'

    def ready(self):
        """
        Configure necessary data items if not existing
        """
        init_labs()
        init_links()
        init_switches()
        check_reservations()


def init_labs():
    """
    script to create initial laboratories database
    ---
    order: 1, 2, ..., 16
    """

    from django.contrib.auth.models import User, Group
    from .models import Laboratory
    labs_form = read_csv_as_json('static/data/labs.csv')

    for i, lab in enumerate(labs_form):
        # 1) create group
        name = lab.pop('lab_name')
        try:
            group = Group.objects.get(name=name)
        except Group.DoesNotExist:
            group = Group.objects.create(name=name)

        # 2) create default user
        username = 'u' + lab['lab_order'].zfill(2)
        try:
            usr = User.objects.get(username=username)
        except User.DoesNotExist:
            usr = User.objects.create_user(username=username, email=default_email, password=default_password)
        if not usr.groups.filter(name=name):  # make the default user correlate to this group
            usr.groups.add(group)

        # 3) create laboratory
        if not Laboratory.objects.filter(lab_name=group):
            Laboratory.objects.create(
                lab_name=group,
                default_user=usr,
                token=uuid.uuid4().hex[:20],
                **lab
            )


def init_links():
    """
    script to create initial linkage information database, and initial 16 users corresponding to 16 laboratories
    """
    from .models import EPsLinks, SPDsLinks, Laboratory

    ###################################################
    # 1. create links

    # 1) Entangled-Photons Switch linkage
    eps_form = read_csv_as_json('static/data/eps.csv')

    for link in eps_form:
        # lab, in_ch, out_ch, linkage
        if not EPsLinks.objects.filter(in_ch=link['in_ch'], out_ch=link['out_ch']):
            EPsLinks.objects.create(
                lab=Laboratory.objects.get(lab_order=int(link['lab'])),
                in_ch=link['in_ch'],
                out_ch=link['out_ch'],
                linkage=link['linkage'],
                in_use=False
            )
            print('created link', link)

    # 2) Single-Photon Detector Switch linkage
    spd_form = read_csv_as_json('static/data/spd.csv')

    for link in spd_form:
        # username, in_ch, out_ch, linkage
        if not SPDsLinks.objects.filter(in_ch=link['in_ch'], out_ch=link['out_ch']):
            SPDsLinks.objects.create(
                lab=Laboratory.objects.get(lab_order=int(link['lab'])),
                in_ch=link['in_ch'],
                out_ch=link['out_ch'],
                linkage=link['linkage'],
                in_use=False
            )
            print('created link', link)

    ###################################################
    # 2. initialize linkage status
    eps_links = EPsLinks.objects.all()
    spds_links = SPDsLinks.objects.all()
    for link in eps_links:
        if link.out_ch == 16:
            link.linkage = True
        else:
            link.linkage = False
        link.in_use = False
        link.save()

    for link in spds_links:
        if link.out_ch == 1:
            link.linkage = True
        else:
            link.linkage = False
        link.in_use = False
        link.save()


def init_switches():
    """
    Initialize linkage status of two fiber switches
    """
    from .models import EPsLinks, SPDsLinks

    # according to database, initialize status of optical switches
    # EPs & SPDs
    ep_links = EPsLinks.objects.filter(linkage=True)
    spd_links = SPDsLinks.objects.filter(linkage=True)
    print(ep_links, spd_links, sep='\n')
    print('initialize EPs switches ... ')
    for link in ep_links:
        ep_switch.set_outer_channel(link.in_ch, link.out_ch)
    print('initialize SPDs switches ... ')
    for link in spd_links:
        spd_switch.set_outer_channel(link.in_ch, link.out_ch)
    print('=== Switches status ===')
    print(ep_switch.name, ep_switch.status)
    print(spd_switch.name, spd_switch.status)


def check_reservations():
    """
    If there are reservations whose end time is greater than now, set it to now
    """
    from .models import Reservation
    now = datetime.now()
    reservations = Reservation.objects.filter(end_time__gte=now)
    for res in reservations:
        res.end_time = now
        res.save()


def read_csv_as_json(fname: str):
    """
    Read CSV file as JSON format, i.e., dict type in Python
    """
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
        fields = rows[0]
        n = len(fields)
        rows.pop(0)
        return [{fields[i]: row[i] for i in range(n)} for row in rows]
