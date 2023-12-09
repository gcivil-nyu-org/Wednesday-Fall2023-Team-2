from rest_framework import status
from django.utils import timezone
from django.template import loader
from django.http import HttpRequest
from rest_framework import generics
from haversine import haversine, Unit
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from rest_framework.permissions import IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.authentication import SessionAuthentication

from map.models import ParkingSpace, OccupancyHistory
from users.models import Post, Comment, UserWatchedParkingSpace
from .serializers import (
    ParkingSpaceSerializer,
    PostSerializer,
    UserWatchedParkingSpaceSerializer,
)

from better_profanity import profanity

profanity.load_censor_words()
# Custom swear words can be added to this array
custom_badwords = ["bullshittery", "bitchy"]
User = get_user_model()


class ParkingSpaceNearCenterAPIView(generics.ListAPIView):
    """API endpoint
    /api/spots/?lat=LATITUDE&lon=LONGITUDE
    """

    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer

    def get(self, request: HttpRequest) -> Response:
        """handles get requests to API endpoint above

        Args:
            request (HttpRequest): http request object

        Returns:
            Response: JSON Object with either message requesting
            lat and lon as query parameters OR on success
            the parking spots within distance
            (specified in __is_within_dist method)
        """
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        if not (lat and lon):
            response_data = {"message": "Bad Request: Missing lat and lon parameters"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        center_point = (float(lat), float(lon))
        filtered_spots = [
            spot
            for spot in self.queryset.all()
            if self.__is_within_dist(
                center_point, (float(spot.latitude), float(spot.longitude))
            )
        ]

        for spot in filtered_spots:
            if spot.occupancy_percent:
                spot.occupancy_percent = round(spot.occupancy_percent / 10) * 10

        serializer = self.serializer_class(filtered_spots, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def __is_within_dist(self, p1, p2):
        """method to create a normal user

        Returns:
            Boolean: p1 is within max_dist of p2
        """
        max_dist = 1
        return haversine(p1, p2, unit=Unit.MILES) < max_dist


class ParkingSpaceChangeOccupancyAPIView(APIView):
    """API endpoint
    /api/spot/occupancy/?percent=PERCENT&id=PARKING_SPACE_ID

    Changes the Occupancy Percent of Parking Space (ID)
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    extra_email_context = {"site_name": "Parkrowd"}
    email_template_name = "api/parkingspace_status_update_email_template.html"
    subject_template_name = "api/parkingspace_status_update_email_subject_template.txt"

    def post(self, request: HttpRequest) -> Response:
        """handles post requests to API endpoint above

        Args:
            request (HttpRequest): http request object

        Returns:
            Response: JSON Object with either parking_spot_id
            sent on success OR
            fail message to update front end
        """
        occupancy_percent = request.data.get("percent")
        parking_spot_id = request.data.get("id")
        available_vehicle_spaces = request.data.get("available_vehicle_spaces")

        if not ((occupancy_percent is not None) and parking_spot_id):
            response_data = {"message": "Bad Request: Missing percent or id parameters"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(occupancy_percent, str) and not occupancy_percent.isdigit():
            response_data = {"message": "Bad Request: Percent can only have digits"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        occupancy_percent = int(occupancy_percent)
        if occupancy_percent > 100:
            response_data = {"message": "Bad Request: Percent is >100"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        if occupancy_percent % 10 != 0:
            response_data = {"message": "Bad Request: Percent is not a multiple of 10"}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            # * Retrieve the ParkingSpace instance
            parking_space = ParkingSpace.objects.get(parking_spot_id=parking_spot_id)

            # Update the occupancy_percent field
            parking_space.occupancy_percent = occupancy_percent

            # Update the available_vehicle_spaces
            parking_space.available_vehicle_spaces = available_vehicle_spaces

            # Create New Occupancy History
            history = OccupancyHistory()
            history.user = request.user
            history.parking_space = get_object_or_404(
                ParkingSpace, parking_spot_id=parking_spot_id
            )
            history.updated_at = timezone.now()
            history.occupancy_percent = occupancy_percent

            parking_space.save()
            history.save()

            # send emails to users that put a watch on this spot
            current_site = get_current_site(request)
            email_field_name = User.get_email_field_name()
            user_watches = UserWatchedParkingSpace.objects.filter(
                parking_space=parking_space, threshold__gte=occupancy_percent
            )
            domain = current_site.domain

            for record in user_watches:
                user_email = getattr(record.user, email_field_name)
                context = {
                    "user": record.user,
                    "email": user_email,
                    "domain": domain,
                    "protocol": "https" if self.request.is_secure() else "http",
                    **(self.extra_email_context or {}),
                }
                self.send_mail(
                    self.subject_template_name,
                    self.email_template_name,
                    context,
                    None,
                    user_email,
                )
                record.delete()

            return Response(
                {"message": "Occupancy percent updated successfully."},
                status=status.HTTP_200_OK,
            )

        except ParkingSpace.DoesNotExist:
            return Response(
                {"message": "ParkingSpace with the specified id does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()


class ParkingSpacePostsAPIView(generics.ListAPIView):
    """GET API endpoint
    /api/spot/posts/<str:spotId>

    get a list of all the posts associated with a spot
    """

    serializer_class = PostSerializer

    def get_queryset(self):
        parking_space_id = self.kwargs["spotId"]
        return Post.objects.filter(parking_space__parking_spot_id=parking_space_id)


class ParkingSpaceAddCommentAPIView(APIView):
    """POST API endpoint
    /api/spot/posts/add-comment/<int:postId>

    get a list of all the posts associated with a spot
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request: HttpRequest, postId: int) -> Response:
        profanity.add_censor_words(custom_badwords)
        comment_content = profanity.censor(request.data["commentContent"])
        if not comment_content:
            return Response("Error: empty comment content", 400)
        try:
            post = Post.objects.get(id=postId)
        except Post.DoesNotExist:
            return Response(f"No post with post id {postId}", 400)

        new_comment = Comment(
            content=comment_content,
            author=request.user,
            post=post,
            created_at=timezone.now(),
        )
        new_comment.save()

        return Response("Comment created!", 200)


class AddWatchOnParkingSpaceAPIView(APIView):
    model = UserWatchedParkingSpace
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request: HttpRequest) -> Response:
        user = request.user
        try:
            parking_space = ParkingSpace.objects.get(
                parking_spot_id=request.data["parking_spot_id"]
            )
        except ParkingSpace.DoesNotExist:
            return Response("Invalid parking spot id", 400)

        threshold = request.data.get("threshold", 80)
        newUserWatchedParkingSpace = UserWatchedParkingSpace(
            user=user, parking_space=parking_space, threshold=threshold
        )
        newUserWatchedParkingSpace.save()

        return Response(f"Watch on spot {parking_space.parking_spot_id} added", 200)


class RemoveWatchOnParkingSpaceAPIView(APIView):
    model = UserWatchedParkingSpace
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request: HttpRequest) -> Response:
        try:
            parkingSpace = ParkingSpace.objects.get(
                parking_spot_id=request.data["parking_spot_id"]
            )
        except ParkingSpace.DoesNotExist:
            return Response("Invalid parking spot id", 400)
        try:
            watchRecord = self.model.objects.get(
                user=request.user, parking_space=parkingSpace
            )
        except self.model.DoesNotExist:
            return Response("No watch found on this parking space", 400)
        watchRecord.delete()

        return Response(f"Watch on spot {parkingSpace.parking_spot_id} removed", 200)


class WatchOnParkingSpaceAPIView(APIView):
    model = UserWatchedParkingSpace
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    serializer_class = UserWatchedParkingSpaceSerializer

    def get(self, request: HttpRequest) -> Response:
        return Response(
            self.serializer_class(
                self.model.objects.filter(user=request.user), many=True
            ).data,
            status.HTTP_200_OK,
        )
