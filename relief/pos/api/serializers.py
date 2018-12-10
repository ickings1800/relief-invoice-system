from rest_framework import serializers
from ..models import Customer, Product, Trip, Route, OrderItem, Invoice, CustomerProduct


class TripAddRouteSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=255, required=False)
    customer = serializers.CharField(required=False)

    def create(self, validated_data):
        note = validated_data.get('note')
        customer = validated_data.get('customer').upper()
        return Route(note=note)