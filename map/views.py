from typing import Optional
from django.views import View
from django.conf import settings
from django.db.models import Max
from better_profanity import profanity
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect


from users.models import User, UserVerification
from .models import ParkingSpace
from .forms import CreatePostForm, CreateParkingSpaceForm


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
        user_verification = None
        if request.user.is_authenticated:
            user_verification = UserVerification.objects.filter(
                username=request.user
            ).first()
        context = {
            "GOOGLE_MAP_ID": settings.GOOGLE_MAP_ID,
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "user_verification": user_verification,
        }
        return render(request, self.template_name, context)


class PostView(View, LoginRequiredMixin):
    """create post view"""

    form_class = CreatePostForm
    template_name = "map/post.html"

    def get(self, request: HttpRequest, parking_spot_id: str) -> HttpResponse:
        """return post view

        Args:
            request (HttpRequest): http request object
            parking_spot_id (str): PK of ParkingSpace object clicked on map

        Returns:
            HttpResponse: rendered post view
        """
        spot = get_object_or_404(ParkingSpace, parking_spot_id=parking_spot_id)
        context = {
            "spot": spot,
            "form": self.form_class(None),
            "username": request.user.username,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, parking_spot_id: str) -> HttpResponse:
        """handle Post creation post req

        Args:
            request (HttpRequest): http request object
            parking_spot_id (str): PK of ParkingSpace object clicked on map
            username (str): username of post author

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        map_template_name = "map/parking.html"
        author = get_object_or_404(User, username=request.user.username)
        spot = get_object_or_404(ParkingSpace, parking_spot_id=parking_spot_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            profanity.add_censor_words(custom_badwords)
            new_post = form.save(commit=False)
            new_post.author = author
            new_post.parking_space = spot
            new_post.title = profanity.censor(form.cleaned_data["title"])
            new_post.post = profanity.censor(form.cleaned_data["post"])
            new_post.save()

            user_verification = None
            if request.user.is_authenticated:
                user_verification = UserVerification.objects.filter(
                    username=request.user
                ).first()

            map_context = {
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
                "GOOGLE_MAP_ID": settings.GOOGLE_MAP_ID,
                "spot": spot,
                "recenter_after_post": True,
                "user_verification": user_verification,
            }

            return render(request, map_template_name, map_context)

        return render(request, self.template_name, {"form": form})


class ParkingSpaceView(View, LoginRequiredMixin):
    """Parking Space view"""

    model = ParkingSpace
    form_class = CreateParkingSpaceForm
    template_name = "map/add_spot.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """return create spot view

        Args:
            request (HttpRequest): http request object
            username (str): username of post author

        Returns:
            HttpResponse: rendered create spot view
        """
        error = None
        if not (request.GET.get("lat") and request.GET.get("lon")):
            error = "Unable to collect longitude and latitude from URL. Please check if the URL is correct."
        return self.__render_page_with_optional_error(request, error)

    def __render_page_with_optional_error(
        self, request: HttpRequest, error: Optional[str] = None
    ) -> HttpResponse:
        user_verification = UserVerification.objects.filter(
            username=request.user
        ).first()
        context = {
            "error": error,
            "form": self.form_class(None),
            "username": request.user.username,
            "user_verification": user_verification,
        }
        return render(request, self.template_name, context)

    def __get_next_parkingspace_id(self):
        """helper method to get next spot ID

        Returns:
            _type_: _description_
        """
        max_parkingspace_id = self.model.objects.aggregate(Max("parking_spot_id"))[
            "parking_spot_id__max"
        ]
        if max_parkingspace_id is None:
            return "1"
        max_parkingspace_id = int(max_parkingspace_id)

        # Increment the max_parkingspace_id to get the next parkingspace_id
        return str(max_parkingspace_id + 1)

    def post(self, request: HttpRequest) -> HttpResponse:
        """handle spot creation post req

        Args:
            request (HttpRequest): http request object

        Returns:
            HttpResponse: redirect or register view with error hints
        """
        user = get_object_or_404(User, username=request.user.username)
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        try:
            float(lat)
            float(lon)
        except ValueError or TypeError:
            return self.__render_page_with_optional_error(
                request,
                "We failed to obtain the longitude and latitude of the new spot you want to create. Please double check your URL to include valid longitude and latitude",
            )

        form = self.form_class(request.POST)
        map_template_name = "map/parking.html"
        if form.is_valid():
            new_spot = form.save(commit=False)
            new_spot.parking_spot_id = self.__get_next_parkingspace_id()
            new_spot.longitude = lon
            new_spot.latitude = lat
            new_spot.user = user
            new_spot.save()

            user_verification = None
            if request.user.is_authenticated:
                user_verification = UserVerification.objects.filter(
                    username=request.user
                ).first()
            map_context = {
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
                "GOOGLE_MAP_ID": settings.GOOGLE_MAP_ID,
                "spot": new_spot,
                "recenter_after_post": True,
                "user_verification": user_verification,
            }

            return render(request, map_template_name, map_context)
        return render(request, self.template_name, {"form": form})


class ProfileSpotRedirectView(View):
    """Spot Redirect view"""

    def get(self, request: HttpRequest, parking_spot_id: str) -> HttpResponse:
        """Args:
            request (HttpRequest): http request object
            parking_spot_id (str): id of a given spot

        Returns:
            HttpResponse: redirects user to the selected spot on the map
        """
        map_template_name = "map/parking.html"
        redirect_spot = ParkingSpace.objects.get(parking_spot_id=parking_spot_id)
        map_context = {
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "GOOGLE_MAP_ID": settings.GOOGLE_MAP_ID,
            "spot": redirect_spot,
            "recenter_after_post": True,
        }
        return render(request, map_template_name, map_context)
