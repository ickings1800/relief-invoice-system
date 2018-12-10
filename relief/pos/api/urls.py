from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api

urlpatterns = [
    path('api/trip/<int:pk>/route/add/', api.TripRouteCreate.as_view(), name='trip_route_create'),
]

urlpatterns = format_suffix_patterns(urlpatterns)