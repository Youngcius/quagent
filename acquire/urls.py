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
from django.urls import path

from .measurement import views_counter, views_countbetweenmarkers
from .measurement import views_correlation, views_startstop, views_histogram

from .views import index

urlpatterns = [
    # measurement modes selection
    path('', index, name='acquire'),
    # 1. counter
    path('counter/update-config/', views_counter.update_config, name='counter-update-config'),
    path('counter/', views_counter.counter_page, name='counter'),  # page with/without chart view
    path('counter/chart/', views_counter.counter_chart_view, name='counter-chart'),
    path('counter/start/', views_counter.start, name='counter-start'),
    path('counter/stop/', views_counter.stop, name='counter-stop'),
    path('counter/download/', views_counter.download, name='counter-download'),

    # 2. correlation
    path('correlation/update-config/', views_correlation.update_config, name='correlation-update-config'),
    path('correlation/', views_correlation.correlation_page, name='correlation'),
    path('correlation/chart/', views_correlation.correlation_chart_view, name='correlation-chart'),
    path('correlation/start/', views_correlation.start, name='correlation-start'),
    path('correlation/stop/', views_correlation.stop, name='correlation-stop'),
    path('correlation/download/', views_correlation.download, name='correlation-download'),

    # 3. startstop
    path('startstop/update-config/', views_startstop.update_config, name='startstop-update-config'),
    path('startstop/', views_startstop.startstop_page, name='startstop'),
    path('startstop/chart/', views_startstop.startstop_chart_view, name='startstop-chart'),
    path('startstop/start/', views_startstop.start, name='startstop-start'),
    path('startstop/stop/', views_startstop.stop, name='startstop-stop'),
    path('startstop/download/', views_startstop.download, name='startstop-download'),

    # 4. histogram
    path('histogram/update-config/', views_histogram.update_config, name='histogram-update-config'),
    path('histogram/', views_histogram.histogram_page, name='histogram'),
    path('histogram/chart/', views_histogram.histogram_chart_view, name='histogram-chart'),
    path('histogram/start/', views_histogram.start, name='histogram-start'),
    path('histogram/stop/', views_histogram.stop, name='histogram-stop'),
    path('histogram/download/', views_histogram.download, name='histogram-download'),

    # 5. countbetweenmarker
    path('countbetweenmarkers/update-config/', views_countbetweenmarkers.update_config,
         name='countbetweenmarkers-update-config'),
    path('countbetweenmarkers/', views_countbetweenmarkers.countbetweenmarkers_page, name='countbetweenmarkers'),
    path('countbetweenmarkers/chart/', views_countbetweenmarkers.countbetweenmarkers_chart_view,
         name='countbetweenmarkers-chart'),
    path('countbetweenmarkers/start/', views_countbetweenmarkers.start, name='countbetweenmarkers-start'),
    path('countbetweenmarkers/stop/', views_countbetweenmarkers.stop, name='countbetweenmarkers-stop'),
    path('countbetweenmarkers/download/', views_countbetweenmarkers.download, name='countbetweenmarkers-download'),

]
