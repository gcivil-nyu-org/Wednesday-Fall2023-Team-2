from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
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
        parking_space = ParkingSpace.objects.all()
        context = {
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "parking_space": parking_space,
        }
        return render(request, self.template_name, context)


class PostView(View):
    """post view"""

    model = ParkingSpace
    template_name = "map/post.html"

    def get(self, request: HttpRequest, dca_license_number: str) -> HttpResponse:
        """return post view

        Args:
            request (HttpRequest): http request object
            dca number (str): dca string

        Returns:
            HttpResponse: rendered post view
        """
        spot = get_object_or_404(ParkingSpace, dca_license_number=dca_license_number)

        # * conditionally render the delete button
        # * only if the user is logged-in and viewing his/her own profile

        context = {
            "spot": spot,
        }

        return render(request, self.template_name, context)
