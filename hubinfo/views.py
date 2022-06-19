from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import EPsLinks, SPDsLinks, Reservation, Laboratory
from utils.switch import ep_switch, spd_switch


class EPInfo:
    def __init__(self, idx, avail, info, etime: str = None):
        self.idx = idx  # channel index
        self.avail = avail  # available status; 5.29 修改：如果available则显示倒计时, 显示“使用中”
        self.info = info  # remarks information
        self.etime = etime  # end time: if available, not None; format: 2022-05-29T02:34


class SPDInfo:
    def __init__(self, idx, avail, etime: str = None):
        self.idx = idx
        self.avail = avail
        self.etime = etime


eps_channel_details = {
    1: 'EPs1: Signal',
    2: 'EPs1: Idler',
    3: 'EPs1: Sync',
    4: 'EPs2: SPDC',
    5: 'EPs3: SPDC'
}


@login_required
def info(request: HttpRequest):
    """
    Display information about channels occupied by the current user
    ---
    EPs linkage form titles: Channel, Remark, Status, Operation
    SPDs linkage form titles: Channel, Status, Operation
    """
    usr = request.user

    group = usr.groups.all()[0]
    lab = Laboratory.objects.get(lab_name=group)

    # 实际：查询数据库，返回结果
    if len(EPsLinks.objects.filter(lab=lab)) == 0:
        return HttpResponseNotFound('There is not EPs channels linkage information of for {}'.format(usr.username))
    if len(SPDsLinks.objects.filter(lab=lab)) == 0:
        return HttpResponseNotFound('There is not SPDs channels linkage information of for {}'.format(usr.username))

    ep_links = EPsLinks.objects.filter(lab=lab)
    eps_info = []
    spd_links = SPDsLinks.objects.filter(lab=lab)
    spds_info = []
    now = datetime.now()

    for link in ep_links:
        if link.linkage and link.in_use:  # 一定有 reservation 在使用中的
            try:
                res = Reservation.objects.get(in_ch=link.in_ch, resource='ep', start_time__lte=now, end_time__gte=now)
                eps_info.append(EPInfo(
                    link.in_ch, True, eps_channel_details[link.in_ch],
                    etime=res.end_time.strftime('%Y-%m-%dT%H:%M')
                ))
            except Reservation.DoesNotExist:
                print(Reservation.DoesNotExist, "in_ch: {}, resource: ep, now: {}".format(link.in_ch, now))
                eps_info.append(EPInfo(link.in_ch, False, eps_channel_details[link.in_ch]))
        else:
            eps_info.append(EPInfo(link.in_ch, False, eps_channel_details[link.in_ch]))

    for link in spd_links:
        if link.linkage and link.in_use:
            # desirably, there is always one element in `res`
            try:
                res = Reservation.objects.get(in_ch=link.in_ch, resource='spd', start_time__lte=now, end_time__gte=now)
                spds_info.append(SPDInfo(
                    link.in_ch, True,
                    etime=res.end_time.strftime('%Y-%m-%dT%H:%M')
                ))
            except Reservation.DoesNotExist:
                print(Reservation.DoesNotExist, "in_ch: {}, resource: spd, now: {}".format(link.in_ch, now))
                spds_info.append(SPDInfo(link.in_ch, False))
        else:
            spds_info.append(SPDInfo(link.in_ch, False))

    return render(
        request, 'control.html',
        {
            'username': usr.username,
            'labname': str(lab.lab_name).upper(),
            'eps': eps_info,
            'spds': spds_info,
        }
    )


#############################################################
# new apply function
@csrf_exempt
def apply(request):
    print('============= apply =================')
    print(request.POST)
    res = Reservation(
        user=request.user,
        start_time=datetime.strptime(request.POST.get('start-time'), '%Y-%m-%dT%H:%M'),
        end_time=datetime.strptime(request.POST.get('end-time'), '%Y-%m-%dT%H:%M'),
        resource=request.POST.get('resource'),
        in_ch=request.POST.get('ch'),
    )

    # check from reservations with the same `in_ch` and the same `resource`
    reservations = Reservation.objects.filter(
        start_time__gt=datetime.now(),
        end_time__lt=datetime.now() + timedelta(days=7),
        in_ch=res.in_ch,
        resource=res.resource
    )
    if reservations:
        for r in reservations:
            if max(res.start_time, r.start_time) <= min(res.end_time, r.end_time):  # 时间区间重叠（冲突）
                print(max(res.start_time, r.start_time), min(res.end_time, r.end_time))
                return HttpResponse('apply fail')
    res.save()
    return HttpResponse('apply success')


#############################################################
# new release function
# 一般都是在使用过程中主动release，并且将对应reservation的end time改到now
@csrf_exempt
def release(request):
    """
    release后默认切换至 (<user id> + 1) % 16 + 1 的 user id 处
    """
    print('============= release =================')
    print(request.POST)
    usr = request.user
    lab = Laboratory.objects.get(lab_name=usr.groups.all()[0])
    resource = request.POST.get('resource')

    if request.POST.get('ch') == 'all':
        if resource == 'ep':
            links = EPsLinks.objects.filter(lab=lab)
            for link in links:
                release_eps_linkage(link.in_ch, link.out_ch)
        if resource == 'spd':
            links = SPDsLinks.objects.filter(lab=lab)
            for link in links:
                release_spds_linkage(link.in_ch, link.out_ch)
        reservations = Reservation.objects.filter(
            user=usr, resource=resource,
            start_time__lte=datetime.now(), end_time__gte=datetime.now()
        )
    else:
        in_ch = int(request.POST.get('ch'))
        if resource == 'ep':
            # release EP <user-in_ch-out_ch> linkage
            link = EPsLinks.objects.get(lab=lab, in_ch=in_ch)
            release_eps_linkage(in_ch, link.out_ch)
        if resource == 'spd':
            # release SPD <user-in_ch-out_ch> linkage
            link = SPDsLinks.objects.get(lab=lab, in_ch=in_ch)
            release_spds_linkage(in_ch, link.out_ch)
        reservations = Reservation.objects.filter(
            user=usr, resource=resource, in_ch=in_ch,
            start_time__lte=datetime.now(), end_time__gte=datetime.now()
        )

    # modify end_time of reservation to now
    for r in reservations:
        r.end_time = datetime.now()
        r.save()
    # return info(request)
    return HttpResponse('release success')


def apply_eps_linkage(in_ch, out_ch):
    """
    Switch EPs channel linkage to <in_ch, out_ch>
    :param in_ch: input channel index
    :param out_ch: output channel index whose linkage is to set as True
    """
    # 1) 改动数据库中对应记录，linkage 置 True
    # 2) 与 in_ch 关联的其他link的 linkage 都需要为 False
    link_old = EPsLinks.objects.get(in_ch=in_ch, linkage=True)
    link_new = EPsLinks.objects.get(in_ch=in_ch, out_ch=out_ch)
    link_old.linkage = False
    link_old.in_use = False
    link_new.linkage = True
    link_new.in_use = True
    link_old.save()
    link_new.save()
    ep_switch.set_outer_channel(in_ch, out_ch)
    print('EP allocated ...')


def apply_spds_linkage(in_ch, out_ch):
    """
    Switch SPDs channel linkage to <in_ch, out_ch>
    :param in_ch: input channel index
    :param out_ch: output channel index whose linkage is to set as True
    """
    link_old = SPDsLinks.objects.get(in_ch=in_ch, linkage=True)
    link_new = SPDsLinks.objects.get(in_ch=in_ch, out_ch=out_ch)
    link_old.linkage = False
    link_old.in_use = False
    link_new.linkage = True
    link_new.in_use = True
    link_old.save()
    link_new.save()
    spd_switch.set_outer_channel(in_ch, out_ch)
    print('SPD allocated ...')


def release_eps_linkage(in_ch, out_ch):
    """
    Switch EPs channel linkage from <in_ch, out_ch> to <in_ch, 16>
    :param in_ch: input channel index
    :param out_ch: output channel index whose linkage is to set as False
    """
    out_ch_new = 16
    link_old = EPsLinks.objects.get(in_ch=in_ch, out_ch=out_ch)
    link_new = EPsLinks.objects.get(in_ch=in_ch, out_ch=out_ch_new)
    link_old.linkage = False
    link_old.in_use = False
    link_new.linkage = True
    link_new.in_use = False
    link_old.save()
    link_new.save()
    ep_switch.set_outer_channel(in_ch, out_ch_new)


def release_spds_linkage(in_ch, out_ch):
    """
    Switch EPs channel linkage from <in_ch, out_ch> to <in_ch, out_ch + 1>
    :param in_ch: input channel index
    :param out_ch: output channel index whose linkage is to set as False
    """
    out_ch_new = out_ch % spd_switch.n_out + 1
    link_old = SPDsLinks.objects.get(in_ch=in_ch, out_ch=out_ch)
    link_new = SPDsLinks.objects.get(in_ch=in_ch, out_ch=out_ch_new)
    link_old.linkage = False
    link_old.in_use = False
    link_new.linkage = True
    link_new.in_use = False
    link_old.save()
    link_new.save()
    spd_switch.set_outer_channel(in_ch, out_ch_new)
