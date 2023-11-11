from django.urls import path
from django.conf import settings

from . import views

app_name = "api"

urlpatterns = [
    path(
        "spots/",
        views.ParkingSpaceNearCenterAPIView.as_view(),
        name="spots-near-center",
    ),
    path(
        "spot/occupancy/",
        views.ParkingSpaceChangeOccupancyAPIView.as_view(),
        name="change-occupancy",
    ),
    path(
        "spot/posts/<str:spotId>/",
        views.ParkingSpacePostsAPIView.as_view(),
        name="get-spot-posts",
    ),
]
