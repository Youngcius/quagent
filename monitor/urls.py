from django.urls import path
from . import views

urlpatterns = [
    path('maps/', views.maps, name='maps'),
    path('maps/status/', views.maps_status, name='maps-status'),
]
