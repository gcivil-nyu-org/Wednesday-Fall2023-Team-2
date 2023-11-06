from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from map.models import ParkingSpace
from .serializers import ParkingSpaceSerializer

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from haversine import haversine, Unit

# Create your views here.


class ParkingSpaceAPIView(generics.ListAPIView):
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
