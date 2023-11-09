from django.db import models


# Create your models here.
class ParkingSpace(models.Model):
    parking_spot_id = models.CharField(max_length=200, primary_key=True)
    address_zip = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    latitude = models.CharField(max_length=200)
    parking_spot_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, default="unknown")
    borough = models.CharField(max_length=200, default="unknown")
    detail = models.CharField(max_length=200, default="unknown")
    operation_hours = models.CharField(max_length=200, default="unknown")
    # * occupancy_percent: 0% or 100% for Business, 0% through 100% for Street
    occupancy_percent = models.IntegerField(blank=True, null=True)
