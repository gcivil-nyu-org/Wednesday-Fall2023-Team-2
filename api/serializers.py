from rest_framework import serializers

from users.models import Post
from users.serializers import UserSerializer
from map.models import ParkingSpace


class ParkingSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpace
        fields = [
            "parking_spot_id",
            "parking_spot_name",
            "longitude",
            "latitude",
            "operation_hours",
            "type",
            "detail",
            "occupancy_percent",
        ]


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Post
        fields = ["title", "post", "author", "created_at", "parking_space"]
