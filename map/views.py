from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import ParkingSpace

from django.conf import settings
from .forms import CreatePostForm, CreateParkingSpaceForm
from users.models import User


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
            "GOOGLE_MAP_ID": settings.GOOGLE_MAP_ID,
        }
        return render(request, self.template_name, context)


class PostView(View):
    """post view"""

    model = ParkingSpace
    form_class = CreatePostForm
    template_name = "map/post.html"

    def get(
        self, request: HttpRequest, parking_spot_id: str, username: str
    ) -> HttpResponse:
        """return post view

        Args:
            request (HttpRequest): http request object
            parking_spot_id (str): PK of ParkingSpace object clicked on map

        Returns:
            HttpResponse: rendered post view
        """
        spot = get_object_or_404(ParkingSpace, parking_spot_id=parking_spot_id)
        context = {"spot": spot, "form": self.form_class(None), "username": username}
        return render(request, self.template_name, context)

    def post(
        self, request: HttpRequest, parking_spot_id: str, username: str
    ) -> HttpResponse:
        """handle Post creation post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        spot = get_object_or_404(ParkingSpace, parking_spot_id=parking_spot_id)
        author = get_object_or_404(User, username=username)
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.parking_space = spot
            new_post.author = author
            new_post.save()
            # Safe text filter here for title and post
            return redirect("map:parking")
        return render(request, self.template_name, {"form": form})

class ParkingSpaceView(View):
    """post view"""

    model = ParkingSpace
    form_class = CreateParkingSpaceForm
    template_name = "map/add_spot.html"

    def get(
        self, request: HttpRequest, username: str
    ) -> HttpResponse:
        print(request.GET.get("lat"))
        print(request.GET.get("lon"))
        return render(request, self.template_name)

    
