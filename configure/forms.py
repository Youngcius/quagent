from django import forms

"""
显示、查询、请求&分配分配可用硬件资源
配置仪器参数
"""


class TaggerSettingForm(forms.Form):
    """
    Form used to submit parameters of Time Tagger
    """
    # avail = forms.CharField(label='Available Tagger')
    binwidth = forms.FloatField(min_value=0.0)
    # n_values = forms.IntegerField(max_value=int(1e5))


