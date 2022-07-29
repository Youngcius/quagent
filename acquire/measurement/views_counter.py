"""
Data acquisition Counter mode
"""
import copy
import datetime
import uuid
import TimeTagger as tt

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse, Http404
from django.http import HttpResponseServerError  # 5xx error
from django.views.decorators.csrf import csrf_exempt

from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts import charts

from ..utils import *
from ..models import *
from acquire import tagger, usr_cnt_map

print('counter 模块载入')

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./template/pyecharts"))


def counter_page(request):
    """
    Data acquisition and visualization page for Counter measurement mode
    """
    interval = int(1e3)  # ps --> ms
    print('interval: ', interval)
    global tagger
    if tagger is None:
        print('...........................................creating tagger...........................................')
        # tagger = tt.createTimeTagger(host=ipv4, port=tagger_port)
        print('available tagger(s):', '=' * 10, tt.scanTimeTagger(), '=' * 10)
        try:
            tagger = tt.createTimeTagger()
        except RuntimeError:
            return HttpResponseServerError('Sorry, The Time Tagger on server is not available now!')
    else:
        print('已经存在 tagger instance')

    # query the global routing table
    avail_channels = get_avail_ch(request.user)  # e.g. [1, 3], or [5,7,8]

    if len(avail_channels) == 0:
        return HttpResponseServerError(
            'There is not available detection channel(s) for you.\nYou should book some of them first.')
    else:
        return render(request, 'measurement/counter.html', {'channels': avail_channels})


@csrf_exempt
def update_config(request):
    """
    Update measurement parameters
    Request: consist user-specific information
    Response: must consist user-specific information, too
    ---
    - binwidth
    - n_values
    - channels
    """
    # AJAX POST
    binwidth = int(request.POST.get('binwidth'))
    n_values = int(request.POST.get('n_values'))
    channels = list(map(int, request.POST.getlist('channels[]')))  # note that there must be a [] in the parameter name
    username = request.user.username

    # create user-specific Counter instance
    user_counter = UserDetector(username, 'Counter')
    user_counter.set_measure_config(**{
        'binwidth': binwidth,
        'n_values': n_values,
        'channels': channels
    })
    user_counter.create_detector(tagger)
    usr_cnt_map[username] = user_counter
    return HttpResponse('update successfully')


# TODO: 页面关闭时候 delete user_cnt_map[<username>]


def start(request):
    """
    Start data acquisition process
    """
    username = request.user.username
    if username in usr_cnt_map.keys():
        usr_cnt_map[username].detector.start()
        return HttpResponse('Has started the Counter measurement instance')
    else:
        return HttpResponse('There is no Counter measurement instance!')


def stop(request):
    """
    Stop data acquisition process
    """
    username = request.user.username
    # if username in user_detector_map.keys() and 'Counter' in user_detector_map[username].keys():
    if username in usr_cnt_map.keys():
        # counter = user_detector_map[username]['Counter'].detector
        usr_cnt_map[username].detector.stop()
        return HttpResponse('Has stopped the Counter measurement instance')
    else:
        return HttpResponse('There is no Counter measurement instance!')


def download(request):
    """
    Download real-time data according to designated time interval
    """
    # 视图响应本身就是多线程？
    username = request.user.username
    if username in usr_cnt_map.keys():
        counter_config = usr_cnt_map[username].config
        counter = usr_cnt_map[username].detector
    else:
        return Http404('no Counter instance running')
    T = float(request.GET.get('T'))  # unit: s
    t = counter_config["binwidth"] * counter_config['n_values'] / 1e12  # ps --> s
    print('==' * 30)
    print('下载时间：', T, '单位时间：', t)
    data_cache = get_data_in_long_time(counter, T, t)

    data_with_config = copy.deepcopy(counter_config)
    data_with_config['username'] = username
    data_with_config['measure-mode'] = 'Counter'
    data_with_config['binwidth'] /= 1e12  # ps --> s
    data_with_config['time'] = T
    data_with_config['data'] = np.hstack(data_cache).tolist()
    data_with_config['timestamp'] = str(datetime.datetime.now())
    response = FileResponse(json.dumps(data_with_config))  # dict --> str
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    filename = '_'.join(['data', username, str(datetime.date.today()), str(uuid.uuid1()) + '.json'])
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    return response


def counter_fig(username: str, x_unit: str = 'ps') -> str:
    """
    Return information of Counter figure in string format
    :param username: to acquire user-specific measurement instance
    :param x_unit: to set x-axis unit, e.g., ns
    """
    line = charts.Line()
    x_scale = 1e-12 / unit_to_num[x_unit]
    ymax, ymin = None, None
    # global counter
    if username in usr_cnt_map.keys():
        counter_config = usr_cnt_map[username].config
        counter = usr_cnt_map[username].detector
        if counter.isRunning():
            counts = counter.getData()  # size [num_ch, n_values]
            ymax, ymin = cal_max_min_limits(counts)
            line.add_xaxis((counter.getIndex() * x_scale).tolist())
            for i, ch in enumerate(counter_config['channels']):
                line.add_yaxis(
                    series_name='channel {}'.format(ch),
                    # y_axis=(counts[i] / counter_config['binwidth']).tolist(),
                    y_axis=counts[i].tolist(),
                    label_opts=opts.LabelOpts(is_show=False)
                )
        print('\t\t\t binwidth:', counter_config['binwidth'])
    line.set_global_opts(
        title_opts=opts.TitleOpts(title='Counting'),
        xaxis_opts=opts.AxisOpts(type_='value', name='Time ({})'.format(x_unit)),
        yaxis_opts=opts.AxisOpts(type_='value', name='Count/s', min_=ymin, max_=ymax)
    )
    fig_str = line.dump_options_with_quotes()
    return fig_str


# class CounterChartView(APIView):
#     def get(self, request, *args, **kwargs):
#         return JsonResponse(json.loads(counter_fig()))
def counter_chart_view(request):
    return JsonResponse(json.loads(counter_fig(request.user.username, request.POST.get('unit_name'))))


def randomize(arr):
    return np.random.randn(*np.shape(arr)) * np.mean(arr) / 30 + np.array(arr)
