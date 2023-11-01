from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .models import ParkingSpace

from django.conf import settings


class MapView(View):
    """main map view"""

    template_name = "map/parking.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return map view page

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: rendered map view response
        """
        parking_space = ParkingSpace.objects.filter(address_zip="11201") 
        context = {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
                   "parking_space": parking_space}
        return render(request, self.template_name, context)
