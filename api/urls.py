from django.urls import path
from django.conf import settings

from . import views

app_name = "api"

urlpatterns = [path("spots/", views.ParkingSpaceAPIView.as_view(), name="spots")]
