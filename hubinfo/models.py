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
    class Meta:
        verbose_name = 'Entangled-Photon Sources Linkage Status'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 每个用户 16 条记录, 每个 user 实际代表一个 ”lab“
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~5
    out_ch = models.IntegerField(verbose_name='output channel')  # 1~16
    linkage = models.BooleanField(verbose_name='linkage status')  # True/False

    # def __str__(self):
    #     return 'Links to Entangled-Photon Sources'


class SPDsLinks(models.Model):
    """
    Timely linkage status of the 8*8 switches.
    At most consists of 64 records.
    """
    class Meta:
        verbose_name = 'SPD Channels Linkage Status'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 每个用户 4 条记录
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~8
    out_ch = models.IntegerField(verbose_name='output channel')  # 1~8
    linkage = models.BooleanField(verbose_name='linkage status')  # True/False


    # def __str__(self):
    #     return 'Links to SPD Channels'
# class SPDLogicPhysicMap(models.Model):
#     pass



