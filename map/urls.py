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
    path(
        "spot-redirect/<str:parking_spot_id>/",
        views.ProfileSpotRedirectView.as_view(),
        name="spot-redirect",
    ),
    path(
        "peak-time/<str:parking_spot_id>/",
        views.PeakTimeView.as_view(),
        name="peak-time",
    ),
]
