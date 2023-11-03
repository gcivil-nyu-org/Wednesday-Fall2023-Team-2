from django.shortcuts import render

from map.models import ParkingSpace
from .serializers import ParkingSpaceSerializer

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from haversine import haversine, Unit

# Create your views here.

class ParkingSpaceAPIView(generics.ListAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer

    def get(self, request):
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')

        if not (lat and lon):
            response_data = {'message': 'Bad Request: Missing lat and lon parameters'}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        center_point = (float(lat), float(lon))
        filtered_spots = [
            spot for spot in self.queryset.all() 
            if self.__is_within_dist(center_point, (float(spot.latitude), float(spot.longitude)))
        ]
        serializer = self.serializer_class(filtered_spots, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def __is_within_dist(self, p1, p2):
        max_dist = 0.25
        return haversine(p1, p2, unit=Unit.MILES) < max_dist