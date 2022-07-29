"""
Data acquisition in Correlation mode
"""
import uuid
import datetime
import copy
import TimeTagger as tt

from pyecharts import options as opts
from pyecharts import charts

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse, Http404
from django.http import HttpResponseServerError  # 5xx error
from django.views.decorators.csrf import csrf_exempt

from ..utils import *
from ..models import *
from ..globvar import tagger, usr_corr_map

from pyecharts.globals import CurrentConfig
from jinja2 import Environment, FileSystemLoader

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))


def correlation_page(request):
    """
    Data acquisition and visualization page for Correlation measurement mode
    """
    global tagger
    if tagger is None:
        try:
            tagger = tt.createTimeTagger()
        except RuntimeError:
            return HttpResponseServerError('Sorry, The Time Tagger on server is not available now!')

    # query the global routing table
    avail_channels = get_avail_ch(request.user)  # e.g. [1, 3], or [5,7,8]

    if len(avail_channels) == 0:
        return HttpResponseServerError(
            'There is not available detection channel(s) for you.\nYou should book some of them first.')
    else:
        return render(request, 'measurement/correlation.html', {'channels': avail_channels})


@csrf_exempt
def update_config(request):
    """
    Update measurement parameters
    ---
    - binwidth
    - n_bins
    - channel 1
    - channel 2 (optional)
    """
    username = request.user.username
    binwidth = int(request.POST.get('binwidth'))
    n_bins = int(request.POST.get('n_bins'))
    ch1, ch2 = int(request.POST.get('ch1')), int(request.POST.get('ch2'))

    # create user-specific Correlation instance
    user_correlation = UserDetector(username, 'Correlation')
    user_correlation.set_measure_config(**{
        'binwidth': binwidth,
        'n_bins': n_bins,
        'channel_1': ch1,
        'channel_2': ch2
    })
    user_correlation.create_detector(tagger)
    usr_corr_map[username] = user_correlation
    return HttpResponse('update successfully')


def start(request):
    """
    Start data acquisition and displaying
    """
    username = request.user.username
    if username in usr_corr_map.keys():
        usr_corr_map[username].detector.start()
        return HttpResponse('Has started the Correlation measurement instance')
    else:
        return HttpResponse('There is no Correlation measurement instance!')


def stop(request):
    """
    Stop data acquisition and displaying
    """
    username = request.user.username
    if username in usr_corr_map.keys():
        usr_corr_map[username].detector.stop()
        return HttpResponse('Has stopped the Correlation measurement instance')
    else:
        return HttpResponse('There is not Correlation measurement instance!')


def download(request):
    """
    Download real-time data according to designated time interval
    """
    username = request.user.username
    if username in usr_corr_map.keys():
        corr_config = usr_corr_map[username].config
        correlation = usr_corr_map[username].detector
    else:
        return Http404('no Correlation instance running')

    T = float(request.GET.get('T'))  # unit: s
    time.sleep(T)

    data_with_config = copy.deepcopy(corr_config)
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['username'] = username
    data_with_config['measure-mode'] = 'Correlation'
    data_with_config['time'] = T
    data_with_config['data'] = correlation.getData().tolist()
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # header information, to tell Web browser this is a file
    filename = '_'.join(['data', username, str(datetime.date.today()), str(uuid.uuid1()) + '.json'])
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    return response


def correlation_fig(username: str, x_unit: str = 'ps') -> str:
    """
    diff_t = t(ch1) - t(ch2), ch1 在前则 diff_t 为负数
    :param username: to acquire user-specific measurement instance
    :param x_unit: to set x-axis unit, e.g., ns"""
    hist = charts.Bar()
    x_scale = 1e-12 / unit_to_num[x_unit]
    print()
    print('x_scale', x_scale)
    ymax, ymin = None, None
    if username in usr_corr_map.keys():
        correlation = usr_corr_map[username].detector
        if correlation.isRunning():
            vals = correlation.getData()
            ymax, ymin = cal_max_min_limits(vals)
            hist.add_xaxis((correlation.getIndex() * x_scale).tolist())
            hist.add_yaxis(
                series_name='time difference',
                y_axis=vals.tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )

    hist.set_global_opts(
        title_opts=opts.TitleOpts(title='Time Correlation Counting'),
        xaxis_opts=opts.AxisOpts(name='Time ({})'.format(x_unit)),
        yaxis_opts=opts.AxisOpts(type_='value', name='Count', min_=ymin, max_=ymax)
    )
    fig_str = hist.dump_options_with_quotes()
    return fig_str


def correlation_chart_view(request):
    return JsonResponse(json.loads(correlation_fig(
        request.user.username,
        request.POST.get('unit_name')
    )))
