from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from django.conf import settings
from .models import Locations

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
        locations = Locations.objects.all()
        context = {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY, "locations":locations}
        return render(request, self.template_name, context)
