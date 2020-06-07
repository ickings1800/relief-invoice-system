from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api

urlpatterns = [
    path('api/customers/', api.CustomerList.as_view(), name='customer_list'),
    path('api/customers/<int:pk>/', api.CustomerDetail.as_view(), name='customer_detail'),
    path('api/customer/create/', api.CustomerCreate.as_view(), name='customer_create'),
    path('api/customer/<int:pk>/delete/', api.customer_delete, name='customer_delete'),
    path('api/customer/update/<int:pk>/', api.CustomerUpdate.as_view(), name='customer_update'),
    path('api/products/', api.ProductList.as_view(), name='product_list'),
    path('api/products/<int:pk>/', api.ProductDetail.as_view(), name='product_detail'),
    path('api/product/create/', api.ProductCreate.as_view(), name='product_create'),
    path('api/product/update/<int:pk>/', api.ProductUpdate.as_view(), name='product_update'),
    path('api/customergroup/swap/', api.customergroup_arrange, name='customergroup_swap'),
    path('api/customergroup/<int:pk>/update/', api.group_change, name='group_change'),
    path('api/group/create/', api.group_create, name='group_create'),
    path('api/groups/', api.CustomerGroupList.as_view(), name='group_list'),
    path('api/groups/all/', api.GroupList.as_view(), name='list_all_groups'),
    path('api/customers/<int:pk>/products/', api.CustomerProductList.as_view(), name='customerproduct_list'),
    path('api/customers/<int:pk>/products/create/', api.CustomerProductCreate.as_view(), name='customerproduct_create'),
    path('api/customerproduct/<int:pk>/', api.CustomerProductDetail.as_view(), name='customerproduct_detail'),
    path('api/customerproduct/<int:pk>/update/', api.CustomerProductUpdate.as_view(), name='customerproduct_update'),
    path('api/customerproduct/<int:pk>/delete/', api.customerproduct_delete, name='customerproduct_delete'),
    path('api/customers/<int:pk>/customerproduct/arrangement/', api.customerproduct_arrangement, name='customerproduct_arrangement'),
    path('api/customers/<int:pk>/routes/', api.CustomerRouteList.as_view(), name='customerroute_list'),
    path('api/trips/', api.TripList.as_view(), name='trip_list'),
    path('api/trips/<int:pk>/', api.TripDetail.as_view(), name='api_trip_detail'),
    path('api/trip/create/', api.TripCreate.as_view(), name='trip_create'),
    path('api/trip/update/<int:pk>/', api.TripUpdate.as_view(), name='trip_update'),
    path('api/trip/<int:pk>/delete/', api.TripDelete.as_view(), name='trip_delete'),
    path('api/trip/<int:pk>/duplicate/', api.TripDuplicate.as_view(), name='trip_duplicate'),
    path('api/trip/<int:pk>/packingsum/', api.trip_packing_sum, name='trip_packing_sum'),
    path('api/trips/<int:pk>/detail/routes/', api.TripRouteList.as_view(), name='trip_route_list'),
    path('api/trips/<int:pk>/detail/routes/add/', api.TripRouteCreate.as_view(), name='trip_route_create'),
    path('api/routes/<int:pk>/delete/', api.RouteDelete.as_view(), name='route_delete'),
    path('api/routes/<int:pk>/update/', api.RouteUpdate.as_view(), name='route_update'),
    path('api/routes/<int:pk>/', api.RouteDetail.as_view(), name='route_detail'),
    path('api/orderitem/<int:pk>/', api.OrderItemDetail.as_view(), name='orderitem_detail'),
    path('api/orderitem/<int:pk>/update/', api.OrderItemUpdate.as_view(), name='orderitem_update'),
    path('api/trips/<int:pk>/routes/arrange/', api.route_arrange, name='route_arrange'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
