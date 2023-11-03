from rest_framework import serializers
from map.models import ParkingSpace

class ParkingSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpace
        fields = ['dca_license_number', 'address_zip', 'longitude', 'latitude', 'business_name']