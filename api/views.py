from rest_framework import status
from django.http import HttpRequest
from rest_framework import generics
from haversine import haversine, Unit
from rest_framework.response import Response

from map.models import ParkingSpace
from users.models import Post, Comment
from .serializers import ParkingSpaceSerializer, PostSerializer, CommentSerializer


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
        serializer = self.serializer_class(filtered_spots, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def __is_within_dist(self, p1, p2):
        """method to create a normal user

        Returns:
            Boolean: p1 is within max_dist of p2
        """
        max_dist = 1
        return haversine(p1, p2, unit=Unit.MILES) < max_dist


class ParkingSpaceChangeOccupancyAPIView(generics.ListAPIView):
    """API endpoint
    /api/spot/occupancy/?percent=PERCENT&id=PARKING_SPACE_ID

    Changes the Occupancy Percent of Parking Space (ID)
    """

    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer

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

        if not (occupancy_percent and parking_spot_id):
            response_data = {
                "message": "Bad Request: Missing percent and id parameters"
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            # * Retrieve the ParkingSpace instance
            parking_space = ParkingSpace.objects.get(parking_spot_id=parking_spot_id)

            # Update the occupancy_percent field
            parking_space.occupancy_percent = occupancy_percent
            parking_space.save()

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


class ParkingSpacePostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        parking_space_id = self.kwargs["spotId"]
        return Post.objects.filter(parking_space__parking_spot_id=parking_space_id)
