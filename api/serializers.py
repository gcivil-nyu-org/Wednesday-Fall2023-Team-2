from rest_framework import serializers

from users.models import Post, Comment
from users.models import ParkingSpace, User
from map.models import OccupancyHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class OccupancyHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = OccupancyHistory
        fields = [
            "user",
            "parking_space",
            "updated_at",
            "occupancy_percent",
        ]


class ParkingSpaceSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    occupancy_history = OccupancyHistorySerializer(many=True, read_only=True)

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
            "user",
            "occupancy_history",
            "vehicle_spaces_capacity",
            "available_vehicle_spaces",
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = ["content", "author", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "post",
            "author",
            "created_at",
            "parking_space",
            "comments",
        ]
