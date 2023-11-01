from django.db import models


# Create your models here.
class ParkingSpace(models.Model):
    dca_license_number = models.CharField(max_length=200)
    address_zip = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    latitude = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200)
