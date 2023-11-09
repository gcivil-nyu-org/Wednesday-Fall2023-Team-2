from rest_framework import serializers
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
