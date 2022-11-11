import json
import requests
from django.db import models
from django.contrib.auth.models import User
from .utils import *


#
# 1: 'ece-1',
# 2: 'ece-2',
# 3: 'mse-1',
# 4: 'pas-1',
# 5: 'pas-2',
# 6: 'osc-1',
# 7: 'osc-2',
# 8: 'osc-3',
# 9: 'osc-4',
# 10: 'osc-5',
# 11: 'bio-1',
# 12: 'bio-2',
# 13: 'bio-3',
# 14: '',
# 15: '',
# 16: ''


# class CrossLabUser(models.Model):
#     """
#     User model for CrossLab(iLab)
#     """
#     # "owner": {
#     #     "id": 1701472,
#     #     "name": "Zhaohui Yang",
#     #     "first_name": "Zhaohui",
#     #     "last_name": "Yang",
#     #     "email": "zhy@airzona.edu",
#     #     "phone": "5205247501",
#     #     "employee_id": "N/A"
#     # },
#     ilab_id = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=30)
#     first_name = models.CharField(max_length=20)
#     last_name = models.CharField(max_length=20)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20)
#     employee_id = models.CharField(max_length=20)
#
#
# class UserLabMap(models.Model):
#     """
#     Logical user -- Specific laboratory mapping information
#     """
#
#     class Meta:
#         unique_together = ['ilab_lab_id', 'ilab_user_id']
#
#     ilab_lab_id = models.CharField(max_length=20)
#     ilab_user_id = models.CharField(max_length=20)
#     lab_name = models.CharField(max_length=100)


class CrossLabQuagentUserMap(models.Model):
    """
    Mapping: Laboratories in iLab -> Physical users in Quagent
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ilab_lab_id = models.CharField(max_length=20, verbose_name='iLab laboratory id')
    ilab_lab_name = models.CharField(max_length=50, verbose_name='iLab laboratory name')
