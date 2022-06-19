from django.db import models
from django.contrib.auth.models import User, Group


class Laboratory(models.Model):
    """
    Laboratory, corresponding to Group model in Django
    Each Laboratory instance corresponds to a Group instance
    """

    class Meta:
        verbose_name = 'Terminal Laboratory'

    lab_order = models.IntegerField(verbose_name='lab order', unique=True)  # order: 1~16
    lab_name = models.OneToOneField(Group, to_field='name', on_delete=models.CASCADE, verbose_name='lab name')
    default_user = models.ForeignKey(User, on_delete=models.CASCADE)  # 对于每个实验室都创建一个初始用户，e.g. u01, u02, ..., u16
    pi_name = models.CharField(max_length=30, verbose_name='principal investigator')  # principal investogator
    pi_email = models.EmailField(verbose_name='lab email')
    pi_phone = models.CharField(max_length=15, verbose_name='lab contact')
    location = models.CharField(max_length=50, verbose_name='lab address')  # e.g. which building, which room
    token = models.CharField(max_length=30, verbose_name='lab token')  # 使用 uuid.uuid4().hex 生成

    def __str__(self):
        return str(self.lab_name)


# Create your models here.
class EPsLinks(models.Model):
    """
    Timely linkage status of the 5*16 switches.
    At most consists of 80 records.
    """

    class Meta:
        verbose_name = 'Entangled-Photon Sources Linkage Status'
        unique_together = ['in_ch', 'out_ch']

    # 每个用户 16 条记录, 每个 user 实际代表一个 ”lab“
    lab = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~5
    out_ch = models.IntegerField(verbose_name='output channel')  # 1~16
    linkage = models.BooleanField(verbose_name='linkage status')  # True/False
    in_use = models.BooleanField(default=False, verbose_name='in use or idle')

    def __str__(self):
        return 'Entangled-Photon Sources Linkage Status'


class SPDsLinks(models.Model):
    """
    Timely linkage status of the 8*8 switches.
    At most consists of 64 records.
    """

    class Meta:
        verbose_name = 'SPD Channels Linkage Status'
        unique_together = ['in_ch', 'out_ch']

    # 每个用户 4 条记录
    lab = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~8
    out_ch = models.IntegerField(verbose_name='output channel')  # 1~8
    linkage = models.BooleanField(verbose_name='linkage status')  # True/False
    in_use = models.BooleanField(default=False, verbose_name='in use or idle')

    def __str__(self):
        return 'SPD Channels Linkage Status'


class Reservation(models.Model):
    """
    Resource reservation table
    """

    class Meta:
        verbose_name = 'Reservation information'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name='start time')
    end_time = models.DateTimeField(verbose_name='end time')
    resource = models.CharField(max_length=10, verbose_name='resource type (EPs or SPDs)')
    in_ch = models.IntegerField(verbose_name='input channel')  # 1~8 or 1~5
