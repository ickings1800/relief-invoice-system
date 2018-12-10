from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .serializers import TripAddRouteSerializer
from ..models import Trip, Route, Customer, CustomerProduct, OrderItem


class TripRouteCreate(CreateAPIView):
    def post(self, request, *args, **kwargs):
        try:
            trip = Trip.objects.get(pk=self.kwargs['pk'])
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        route_serializer = TripAddRouteSerializer(data=request.data)
        if route_serializer.is_valid():
            validated_note = route_serializer.validated_data.get('note')
            validated_customer = route_serializer.validated_data.get('customer')
            trip.create_route(validated_note, validated_customer)
            return Response(status=status.HTTP_201_CREATED, data=route_serializer.data)

        return Response(route_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
