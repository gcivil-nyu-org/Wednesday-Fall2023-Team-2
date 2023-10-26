from django.urls import path
from django.conf import settings

from . import views

app_name = "map"

urlpatterns = [
    path('parking/', views.MapView.as_view(), name='parking')
]