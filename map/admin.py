from django.contrib import admin
from .models import ParkingSpace, OccupancyHistory


# Register your models here.
class ParkingSpaceAdmin(admin.ModelAdmin):
    """Parking Space Admin Page"""

    # * Allows users to search by parking_spot_id
    # * For Admin <-> Business Owner communication
    # * To claim an existing spot, a Business Owner
    # * must contact the Admin to connect a Parking Space
    # * with the owner's username
    search_fields = ["parking_spot_id"]


class OccupancyHistoryAdmin(admin.ModelAdmin):
    """Occupancy History Admin Page Manager"""

    autocomplete_fields = ["parking_space", "user"]


admin.site.register(ParkingSpace, ParkingSpaceAdmin)
admin.site.register(OccupancyHistory, OccupancyHistoryAdmin)
