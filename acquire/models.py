from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User


# 内置User字段：
# username, first_name, last_name, email, password, groups, user_permissions, ...
# ---
# e.g. user = User.objects.create_user(username='xujin',email='qq@qq.com',password='111111')

# User-specific Measurement Configuration classes
class Counter(Model):
    binwidth = models.IntegerField(name='binwidth', help_text='bin width (unit: ps)')
    n_values = models.IntegerField(name='n_values', help_text='number of data points')
    channels = models.CharField(max_length=8)  # e.g. '1246'
    username = models.ForeignKey(User, on_delete=models.CASCADE)


class CounterBetweenMarker(Model):
    pass


class Correlation(Model):
    pass


class Countrate(Model):
    pass


class Histogram(Model):
    pass


class StartStop(Model):
    pass


class TimeDifferences(Model):
    pass


class Film(Model):
    pass



