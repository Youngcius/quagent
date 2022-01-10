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
from .measurement_sim import views_counter, views_correlation, views_startstop, views_timedifferences
from .views_sim import index

# from .measurement import views_counter, views_correlation, views_startstop, views_timedifferences
# from views import index


urlpatterns = [
    # measurement modes selection
    path('', index, name='acquire'),
    # 1. counter
    path('counter/update-config/', views_counter.update_config, name='counter-update-config'),
    path('counter', views_counter.counter_page, name='counter'),  # page with/without chart view
    path('counter/start/', views_counter.start, name='counter-start'),
    path('counter/stop/', views_counter.stop, name='counter-stop'),
    path('counter/download/', views_counter.download, name='counter-download'),

    # 2. correlation
    path('correlation/update-config/', views_correlation.update_config, name='correlation-update-config'),
    path('correlation', views_correlation.correlation_page, name='correlation'),
    path('correlation/start/', views_correlation.start, name='correlation-start'),
    path('correlation/stop/', views_correlation.stop, name='correlation-stop'),
    path('correlation/download/', views_correlation.download, name='correlation-download'),

    # 3. startstop
    path('startstop/update-config/', views_startstop.update_config, name='startstop-update-config'),
    path('startstop', views_startstop.startstop_page, name='startstop'),
    path('startstop/start/', views_startstop.start, name='startstop-start'),
    path('startstop/stop/', views_startstop.stop, name='startstop-stop'),
    path('startstop/download/', views_startstop.download, name='startstop-download'),

    # 4. timedifferences
    path('timedifferences/update-config/', views_timedifferences.update_config, name='timedifferences-update-config'),
    path('timedifferences', views_timedifferences.timedifferences_page, name='timedifferences'),
    path('timedifferences/start/', views_timedifferences.start, name='timedifferences-start'),
    path('timedifferences/stop/', views_timedifferences.stop, name='timedifferences-stop'),
    path('timedifferences/download/', views_timedifferences.download, name='timedifferences-download'),
]

# path('update-config/', views_sim.update_config, name='update-config'),
# path('counter/', views_sim.CounterChartView, name='counter'),
# # path('counter-update/', views_sim.CounterChartUpdateView, name='counter-update'),
# path('start-counter/', views_sim.start_counter, name='start-counter'),
# path('stop-counter/', views_sim.stop_counter, name='stop-counter'),
# path('counter-download/', views_sim.counter_download, name='counter-download'),
# path('select/', category.select)
