from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Max
from .models import ParkingSpace

from django.conf import settings
from .forms import CreatePostForm, CreateParkingSpaceForm
from users.models import User

from better_profanity import profanity

profanity.load_censor_words()
# Custom swear words can be added to this array
custom_badwords = ["bullshittery", "bitchy"]


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
            username (str): username of post author

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
            parking_spot_id (str): PK of ParkingSpace object clicked on map
            username (str): username of post author

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        spot = get_object_or_404(ParkingSpace, parking_spot_id=parking_spot_id)
        author = get_object_or_404(User, username=username)
        form = self.form_class(request.POST)
        if form.is_valid():
            profanity.add_censor_words(custom_badwords)
            new_post = form.save(commit=False)
            new_post.parking_space = spot
            new_post.author = author
            new_post.title = profanity.censor(form.cleaned_data["title"])
            new_post.post = profanity.censor(form.cleaned_data["post"])
            new_post.save()
            return redirect("map:parking")
        return render(request, self.template_name, {"form": form})


class ParkingSpaceView(View):
    """Parking Space view"""

    model = ParkingSpace
    form_class = CreateParkingSpaceForm
    template_name = "map/add_spot.html"

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        """return spot view

        Args:
            request (HttpRequest): http request object
            username (str): username of post author

        Returns:
            HttpResponse: rendered post view
        """
        context = {
            "lat": request.GET.get("lat"),
            "lon": request.GET.get("lon"),
            "form": self.form_class(None),
            "username": username,
        }
        # print(request.GET.get("lat"))
        # print(request.GET.get("lon"))
        return render(request, self.template_name, context)

    def __get_next_custom_id(self):
        # Get the maximum existing custom_id in the database
        max_custom_id = ParkingSpace.objects.aggregate(Max("parking_spot_id"))[
            "parking_spot_id__max"
        ]
        max_custom_id = int(max_custom_id)

        # If there are no existing records, start with a default value (e.g., 1)
        if max_custom_id is None:
            return "1"

        # Increment the max_custom_id to get the next custom_id
        return str(max_custom_id + 1)

    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        """handle spot creation post req

        Args:
            request (HttpRequest): http request object
            username (str): username of post author

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        user = get_object_or_404(User, username=username)
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")
        form = self.form_class(request.POST)
        if form.is_valid():
            new_spot = form.save(commit=False)
            new_spot.parking_spot_id = self.__get_next_custom_id()
            new_spot.longitude = lon
            new_spot.latitude = lat
            new_spot.user = user
            new_spot.save()
            return redirect("map:parking")
        return render(request, self.template_name, {"form": form})
