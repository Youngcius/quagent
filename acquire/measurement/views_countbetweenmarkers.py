"""
Data acquisition in CountBetweenMarkers mode
"""

import copy
import datetime
import uuid
import TimeTagger as tt

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.http import HttpResponseServerError  # 5xx error
from django.views.decorators.csrf import csrf_exempt
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts import charts

from ..utils import *
from ..models import *
from ..globvar import tagger, usr_cbm_map

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))


def countbetweenmarkers_page(request):
    """
    Data acquisition and visualization page for CountBetweenMarkers measurement mode
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

        return render(request, 'measurement/countbetweenmarkers.html', {'channels': avail_channels})


@csrf_exempt
def update_config(request):
    """
    Update measurement parameters
    ---
    - n_values
    - click channel
    - begin channel
    - end channel (optional)
    """
    n_values = int(request.POST.get('n_values'))
    ch_click = int(request.POST.get('ch_click'))
    ch_begin = int(request.POST.get('ch_begin'))
    if request.POST.get('ch_end') == '':
        ch_end = ch_begin
    else:
        ch_end = int(request.POST.get('ch_end'))
    username = request.user.username

    user_cbm = UserDetector(username, 'CountBetweenMarkers')
    user_cbm.set_measure_config(**{
        'n_values': n_values,
        'click_channel': ch_click,
        'begin_channel': ch_begin,
        'end_channel': ch_end
    })
    user_cbm.create_detector(tagger)
    usr_cbm_map[username] = user_cbm
    return HttpResponse('update successfully')


def start(request):
    """
    Start data acquisition and displaying
    """
    username = request.user.username
    if username in usr_cbm_map.keys():
        usr_cbm_map[username].detector.start()
        return HttpResponse('Has started the CountBetweenMarkers Measurement')
    else:
        return HttpResponse('There is no CountBetweenMarkers instance!')


def stop(request):
    """
    Stop data acquisition and displaying
    """
    username = request.user.username
    if username in usr_cbm_map.keys():
        usr_cbm_map[username].detector.stop()
        return HttpResponse('Has stopped the CountBetweenMarkers Measurement')
    else:
        return HttpResponse('There is no CountBetweenMarkers instance!')


def download(request):
    """
    Download real-time data according to designated time interval
    """
    username = request.user.username
    if username in usr_cbm_map.keys():
        cbm_config = usr_cbm_map[username].config
        cbm = usr_cbm_map[username].detector
    else:
        return Http404('no Counter instance running')
    T = float(request.GET.get('T'))  # unit: s
    t = 10  # unit: s
    data_cache = get_data_in_long_time(cbm, T, t)
    data_cache = list(map(np.ravel, data_cache))
    data_cache = np.hstack(data_cache).tolist()

    data_with_config = copy.deepcopy(cbm_config)
    data_with_config['username'] = username
    data_with_config['measure-mode'] = 'CountBetweenMarkers'
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['time'] = T
    data_with_config['data'] = data_cache
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    filename = '_'.join(['data', username, str(datetime.date.today()), str(uuid.uuid1()) + '.json'])
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    return response


def countbetweenmarkers_fig(username: str, x_unit: str = 'ps') -> str:
    """
    Line chart
    :param username: to acquire user-specific measurement instance
    :param x_unit: to set x-axis unit, e.g., ns
    """
    line = charts.Line()
    x_scale = 1e-12 / unit_to_num[x_unit]
    ymax, ymin = None, None
    if username in usr_cbm_map.keys():
        cbm = usr_cbm_map[username].detector
        if cbm.isRunning():
            vals = cbm.getData()
            ymax, ymin = cal_max_min_limits(vals)
            cbm_config = usr_cbm_map[username].config
            ch_click = cbm_config['click_channel']
            ch_begin, ch_end = cbm_config['begin_channel'], cbm_config['end_channel']
            # line.add_xaxis(list(range(1, cbm_config['n_values'] + 1)))
            line.add_xaxis((cbm.getIndex() * x_scale).tolist())
            line.add_yaxis(
                series_name='click: channel-{}, begin: channel-{}, end: channel-{}'.format(ch_click, ch_begin, ch_end),
                y_axis=vals.tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title='Counting'),
        xaxis_opts=opts.AxisOpts(type_='value', name='Time ({})'.format(x_unit)),
        yaxis_opts=opts.AxisOpts(type_='value', name='Count', min_=ymin, max_=ymax)
    )
    fig_str = line.dump_options_with_quotes()
    return fig_str


def countbetweenmarkers_chart_view(request):
    return JsonResponse(json.loads(countbetweenmarkers_fig(
        request.user.username,
        request.POST.get('unit_name')
    )))

#
# def countbetweenmarkers_chart_update_view(request):
#     return JsonResponse({'name': 10, 'value': randrange(0, 5)})
