from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def maps(request):
    return render(request, 'admin/maps.html')


def maps_status(request):
    res = {
        'actNode': ['mse-1', 'ece-1', 'osc-3', 'osc-5', 'pas-1', 'bio-1', 'bio-3']
    }
    return JsonResponse(res)

def tables(request):
        return render(request, 'tables.html')
