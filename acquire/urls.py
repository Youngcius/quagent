"""quagent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from . import views_sim

#
# urlpatterns = [
#     path('', views_reference.index),
#     # path('separate/', views.separate),
#     path('timely/', views_reference.timely),
#     path('bar/', views_reference.BarChartView.as_view(), name='demo-bar'),
#     path('separate/', views_reference.BarIndexView.as_view(), name='demo-separate'),
#     path('line/', views_reference.LineChartView.as_view(), name='demo-line'),
#     path('line-update/', views_reference.LineChartUpdateView.as_view(), name='demo-update'),
#     path('refresh/', views_reference.LineIndexView.as_view(), name='demo-refresh'),
#     path('tagger/updata-config', views_reference.update_config, name='update-config'),
#     path('tagger/', views_reference.tagger_demo, name='tagger'),
#     # path('tagger/', views.TaggerView.as_view(), name='tagger'),
#
#     path('tagger/counter', views_reference.CounterChartView.as_view(), name='counter'),
#     path('tagger/counter-update', views_reference.CounterChartUpdateView.as_view(), name='counter-update'),
#
# ]
from . import category

urlpatterns = [
    path('', views_sim.index, name='acquire'),
    path('update-config/', views_sim.update_config, name='update-config'),
    path('counter/', views_sim.CounterChartView, name='counter'),
    # path('counter-update/', views_sim.CounterChartUpdateView, name='counter-update'),
    path('start-counter/', views_sim.start_counter, name='start-counter'),
    path('stop-counter/', views_sim.stop_counter, name='stop-counter'),
    path('counter-download/', views_sim.counter_download, name='counter-download'),
    path('select/', category.select)
]
