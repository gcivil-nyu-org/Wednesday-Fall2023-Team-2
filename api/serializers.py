from rest_framework import serializers

from users.models import Post, Comment
from users.models import ParkingSpace, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ParkingSpaceSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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
