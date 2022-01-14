from django.db import models
from django.contrib.auth.models import User

# EPS1: signal, idler, sync; EPS2: SPDC photons;
# EPS3: SPDC photons

# Create your models here.
class EPsLinks(models.Model):
    """
    Timely linkage status of the 5*16 switches.
    At most consists of 80 records.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 每个用户 16 条记录, 每个 user 实际代表一个 ”lab“
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~5
    linkage = models.BooleanField(verbose_name='linkage status')  # True/False
    out_ch = models.IntegerField(verbose_name='output channel')  # 1~16


class SPDsLinks(models.Model):
    """
    Timely linkage status of the 8*8 switches.
    At most consists of 64 records.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 每个用户 4 条记录
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~8
    linkage = models.BooleanField(verbose_name='linkage status')  # True/False
    out_ch = models.IntegerField(verbose_name='output channel')  # 1~8

# class SPDLogicPhysicMap(models.Model):
#     pass
