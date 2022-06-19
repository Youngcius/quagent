from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

from quagent import settings

from hubinfo.models import Laboratory


def home(request):
    """
    Home page
    """
    if request.user.is_authenticated:
        print('authenticated!')
        print(request.user)
    else:
        print('unauthenticated!')
        print(request.user)
    return render(request, 'home.html')


class RegisterView(View):
    """
    Register class view
    """

    def get(self, request):
        lab_names = list(Laboratory.objects.values_list('lab_name', flat=True))
        return render(request, "registration/register.html", {'labs': lab_names})

    def post(self, request):
        return register_handle(request)


@csrf_exempt
def register_handle(request):
    """
    Process register request
    """
    username = request.POST.get("username")
    password = request.POST.get("password")
    email = request.POST.get("email")
    lab_name = request.POST.get('labname')
    token = request.POST.get('token')
    group = Group.objects.get(name=lab_name)
    lab = Laboratory.objects.get(lab_name=group)
    print(username, password, email, lab, token)

    # check username
    if User.objects.filter(username=username):
        return JsonResponse({"errmsg": "This username has existed!", 'result': False})

    # check token
    if token != lab.token:
        print(token, lab.token)
        return JsonResponse({'errmsg': 'The token of {} is not correct!'.format(lab.lab_name.upper()), 'result': False})

    send_mail(
        subject='[Quagent] New Account Registration',
        from_email=settings.EMAIL_FROM,
        recipient_list=[email],
        message="""
        Thank you for your registration for Quagent (University of Arizona)!
        
        Account: {}
        Password: {}
        
        Please keep your personal login information properly!
        """.format(username, password)
    )

    # if not request.POST.get("allow") == "on":
    #     return render(request, "registration/register.html", {"errmsg": '请先同意用户协议'})

    usr = User.objects.create_user(username, email, password)
    if not usr.groups.filter(name=lab_name):
        usr.groups.add(group)
    return JsonResponse({'alert': 'Register success. Now you can login!', 'result': True})
