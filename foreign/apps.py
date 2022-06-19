import json
from django.apps import AppConfig
from django.contrib.auth.models import User
from .models import CrossLabQuagentUserMap


class ForeignConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foreign'

    def ready(self):

        # TODO: 后期可能将这些 dict 替换为数据库记录

        # load information of 16 laboratories, list of dicts
        with open('static/data/labs.json', 'r') as f:
            labs = json.load(f)
            labs_id = [lab['id'] for lab in labs]

        # TODO: temporarily take two records as user-lab-map
        for i, lab in enumerate(labs):  # 只能先用13个lab
            if i >= 13:
                break
            username = 'u' + '{}'.format(i + 1).zfill(2)
            print('--' * 20)
            print(User.objects.get(username=username))
            # if not CrossLabQuagentUserMap.objects.filter(user=User.objects.get(username=username)):
            if not CrossLabQuagentUserMap.objects.filter(ilab_lab_id=lab['id'], ilab_lab_name=lab['name']):
                CrossLabQuagentUserMap.objects.create(
                    # user=User.objects.get(username=User.objects.get(username=username))
                    user=User.objects.get(username=username),
                    ilab_lab_id=lab['id'],
                    ilab_lab_name=lab['name']
                )
                print('>>> created lab-user-map', i)

        # query current equipments via iLab API

        # necessary information of INQUIRE facility
        # data type: dict
        # facility = requests.get(core_url + '/{}/'.format(facility_id), headers=headers).json()['ilab_response']['cores']
        # equipments = requests.get(ilab_urls['equipment'], headers=headers).json()['ilab_response']['equipment']

        with open('static/data/facility.json', 'r') as f:
            facility = json.load(f)
        with open('static/data/equipments.json', 'r') as f:
            equipments = json.load(f)

        # TODO: 目前的状况是，equipments包含五个设备：
        #   polarized entangled photon signal、time-energy sync signal 1550、time-energy sync signal 1340、SNSPD、Draft equipment
        #   本来的打算是：极化纠缠 source、极化纠缠 idle、极化纠缠 sync、time-energy sync 1550、time-energy sync 1340、SNSPD

        equipment_id_to_types = {
            487862: 'ep',
            487863: 'ep',
            487865: 'ep',
            487864: 'spd'
        }
