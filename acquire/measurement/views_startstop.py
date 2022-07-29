"""
Data acquisition in StartStop mode
"""
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse, Http404
from django.http import HttpResponseServerError  # 5xx error
from django.views.decorators.csrf import csrf_exempt
import uuid
import datetime
import copy
import TimeTagger as tt
from pyecharts import options as opts
from pyecharts import charts

from ..utils import *
from ..models import *
from ..globvar import tagger, usr_stsp_map
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))


def startstop_page(request):
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
        return render(request, 'measurement/startstop.html', {'channels': avail_channels})


@csrf_exempt
def update_config(request):
    """
    Update measurement parameters
    ---
    - click channel
    - start channel
    - binwidth
    """
    username = request.user.username
    binwidth = int(request.POST.get('binwidth'))
    ch_click, ch_start = int(request.POST.get('ch_click')), int(request.POST.get('ch_start'))

    # create user-specific Correlation instance
    user_start_stop = UserDetector(username, 'StartStop')
    user_start_stop.set_measure_config(**{
        'binwidth': binwidth,
        'click_channel': ch_click,
        'start_channel': ch_start,
    })
    user_start_stop.create_detector(tagger)
    usr_stsp_map[username] = user_start_stop
    return HttpResponse('update successfully')


def start(request):
    """
    Start data acquisition and displaying
    """
    username = request.user.username
    if username in usr_stsp_map.keys():
        usr_stsp_map[username].detector.start()
        return HttpResponse('Has started the StartStop measurement instance')
    else:
        return HttpResponse('There is no StartStop measurement instance!')


def stop(request):
    """
    Stop data acquisition and displaying
    """
    username = request.user.username
    if username in usr_stsp_map.keys():
        usr_stsp_map[username].detector.stop()
        return HttpResponse('Has stopped the StartStop measurement instance')
    else:
        return HttpResponse('There is not StartStop measurement instance!')


def download(request):
    """
    Download real-time data according to designated time interval
    """
    username = request.user.username
    if username in usr_stsp_map.keys():
        stsp_config = usr_stsp_map[username].config
        startstop = usr_stsp_map[username].detector
    else:
        return Http404('no StartStop instance running')

    T = float(request.GET.get('T'))  # unit: s
    time.sleep(T)

    data_with_config = copy.deepcopy(stsp_config)
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['username'] = username
    data_with_config['measure-mode'] = 'StartStop'
    # An array of tuples (array of shape Nx2)
    data_with_config['time'] = T
    data_with_config['data'] = startstop.getData().tolist()
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # header information, to tell Web browser this is a file
    filename = '_'.join(['data', username, str(datetime.date.today()), str(uuid.uuid1()) + '.json'])
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    return response


def startstop_fig(username: str, x_unit: str = 'ps') -> str:
    """
    An array of tuples (array of shape Nx2) containing the times (in ps) and counts of each bin
    :param username: to acquire user-specific measurement instance
    :param x_unit: to set x-axis unit, e.g., ns
    """
    hist = charts.Bar()
    x_scale = 1e-12 / unit_to_num[x_unit]
    ymax, ymin = None, None
    if username in usr_stsp_map.keys():
        startstop = usr_stsp_map[username].detector
        if startstop.isRunning():
            data = startstop.getData()  # size [N ,2]
            ymax, ymin = cal_max_min_limits(data[:, 1])  # data长度可能不超过1
            # vals = np.abs(np.random.randn(len(data)))  # delete this
            hist.add_xaxis((data[:, 0] * x_scale).tolist())
            hist.add_yaxis(
                series_name='time difference',
                y_axis=data[:, 1].tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )
    hist.set_global_opts(
        title_opts=opts.TitleOpts(title='StartStop Counting'),
        xaxis_opts=opts.AxisOpts(name='Time ({})'.format(x_unit)),
        yaxis_opts=opts.AxisOpts(type_='value', name='Count', min_=ymin, max_=ymax)
    )
    fig_str = hist.dump_options_with_quotes()
    return fig_str


def startstop_chart_view(request):
    return JsonResponse(json.loads(startstop_fig(
        request.user.username,
        request.POST.get('unit_name')
    )))
