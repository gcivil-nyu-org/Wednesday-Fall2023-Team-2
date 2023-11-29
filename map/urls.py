from django.urls import path
from django.conf import settings

from . import views

app_name = "map"

urlpatterns = [
    path("parking/", views.MapView.as_view(), name="parking"),
    path(
        "post/<str:parking_spot_id>/",
        views.PostView.as_view(),
        name="post",
    ),
    path(
        "parking/add-spot/",
        views.ParkingSpaceView.as_view(),
        name="add-parking-space",
    ),
]
