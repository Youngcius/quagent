import csv
import uuid
from datetime import datetime
from typing import List,Dict
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
        # init_labs()
        modify_labs()
        init_links()
        init_switches()
        check_reservations()


def modify_labs():
    from django.contrib.auth.models import User, Group
    from .models import Laboratory

    labs_form = read_csv_as_json('static/data/labs.csv')

    for i, lab in enumerate(labs_form):
        name = lab.pop('lab_name')
        group = Group.objects.get(name=name)

        lab_db = Laboratory.objects.get(lab_name=group)

        lab_db.pi_email = lab['pi_email']
        lab_db.pi_phone = lab['pi_phone']
        lab_db.location = lab['location']
        lab_db.pi_name = lab['pi_name']

        lab_db.save()

        # +-----------------+--------------+------+-----+---------+----------------+
        # | id              | bigint       | NO   | PRI | NULL    | auto_increment |
        # | lab_order       | int          | NO   | UNI | NULL    |                |
        # | pi_name         | varchar(30)  | NO   |     | NULL    |                |
        # | pi_email        | varchar(254) | NO   |     | NULL    |                |
        # | pi_phone        | varchar(15)  | NO   |     | NULL    |                |
        # | location        | varchar(50)  | NO   |     | NULL    |                |
        # | token           | varchar(30)  | NO   |     | NULL    |                |
        # | default_user_id | int          | NO   | MUL | NULL    |                |
        # | lab_name_id     | varchar(150) | NO   | UNI | NULL    |                |
        # +-----------------+--------------+------+-----+---------+----------------+

        # +----+-----------+----------------+----------+----------+----------+----------------------+-----------------+-------------+
        # | id | lab_order | pi_name        | pi_email | pi_phone | location | token                | default_user_id | lab_name_id |
        # +----+-----------+----------------+----------+----------+----------+----------------------+-----------------+-------------+
        # |  1 |         1 | Zhesheng Zhang |          |          |          | 607aca5ee1b94d32a2ea |               1 | ece-1       |
        # |  2 |         2 |                |          |          |          | e4495e4f9def4dffabcc |               2 | ece-2       |
        # |  3 |         3 | Zhesheng Zhang |          |          |          | 74b49bf25e1b4c85a8f2 |               3 | mse-1       |
        # |  4 |         4 |                |          |          |          | 99f4d91b07b542c19fd6 |               4 | pas-1       |
        # |  5 |         5 |                |          |          |          | 41db7733e3fc4232ab39 |               5 | pas-2       |
        # +----+-----------+----------------+----------+----------+----------+----------------------+-----------------+-------------+

        # lab_name, lab_order, pi_name, pi_email, pi_phone, location
        # ece - 1, 1, Zhesheng
        # Zhang, zsz @ arizona.edu, 5206216075,
#         [{'lab_name': 'ece-1', 'lab_order': '1', 'pi_name': 'Zhesheng Zhang', 'pi_email': '', 'pi_phone': '', 'location': ''},
#         {'lab_name': 'ece-2', 'lab_order': '2', 'pi_name': '', 'pi_email': '', 'pi_phone': '', 'location': ''},
#         {'lab_name': 'mse-1', 'lab_order': '3', 'pi_name': 'Zhesheng Zhang', 'pi_email': '', 'pi_phone': '', 'location': ''}]



def init_labs():
    """
    script to create initial laboratories info, i.e., database
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


def read_csv_as_json(fname: str) -> List[Dict[str,str]]:
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
