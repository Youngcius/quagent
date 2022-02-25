from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('maps/', views.maps, name='maps'),
    path('maps2/', views.maps2, name='maps2'),

    path('maps/status/', views.maps_status, name='maps-status'),

    path('tables/', views.tables, name='table')
]
