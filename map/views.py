from django.views import View
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import ParkingSpace

from django.conf import settings
from .forms import CreatePostForm
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
            profanity.add_censor_words(custom_badwords)
            new_post = form.save(commit=False)
            new_post.parking_space = spot
            new_post.author = author
            new_post.title = profanity.censor(form.cleaned_data["title"])
            new_post.post = profanity.censor(form.cleaned_data["post"])
            new_post.save()
            return redirect("map:parking")
        return render(request, self.template_name, {"form": form})
