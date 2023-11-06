from django.urls import path
from django.conf import settings

from . import views

app_name = "map"

urlpatterns = [
    path("parking/", views.MapView.as_view(), name="parking"),
    path("post/<str:dca_license_number>/", views.PostView.as_view(), name="post"),
]
