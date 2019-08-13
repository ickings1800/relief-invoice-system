from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import api

urlpatterns = [
    # path('api/customers/', api.CustomerList.as_view(), name='customer_list'),
    path('api/customers/<int:pk>/', api.CustomerDetail.as_view(), name='customer_detail'),
    # path('api/customer/create', api.CustomerCreate.as_view(), name='customer_create'),
    # path('api/customer/update/<int:pk>/', api.CustomerUpdate.as_view(), name='customer_update'),
    # path('api/products/', api.ProductList.as_view(), name='product_list'),
    # path('api/products/<int:pk>/', api.ProductDetail.as_view(), name='product_detail'),
    # path('api/product/create', api.ProductCreate.as_view(), name='product_create'),
    # path('api/product/update/<int:pk>/', api.ProductUpdate.as_view(), name='product_update'),
    path('api/customers/<int:pk>/products/', api.CustomerProductList.as_view(), name='customerproduct_list'),
    # path('api/customers/<int:pk>/products/create/', api.CustomerProductCreate.as_view(), name='customerproduct_create'),
    # path('api/customerproduct/<int:pk>/', api.CustomerProductDetail.as_view(), name='customerproduct_detail'),
    # path('api/customerproduct/<int:pk>/update/', api.CustomerProductUpdate.as_view(), name='customerproduct_update'),
    # path('api/customers/<int:pk>/routes/', api.CustomerRouteList.as_view(), name='customerroute_list'),
    # path('api/customers/<int:pk>/invoices/', api.CustomerInvoiceList.as_view(), name='customerinvoice_list'),
    path('api/trips/', api.TripList.as_view(), name='trip_list'),
    # path('api/trips/<int:pk>/', api.TripDetail.as_view(), name='trip_detail'),
    # path('api/trip/create/', api.TripCreate.as_view(), name='trip_create'),
    # path('api/trip/update/<int:pk>/', api.TripUpdate.as_view(), name='trip_update'),
    # path('api/trip/<int:pk>/delete/', api.TripDelete.as_view(), name='trip_delete'),
    path('api/trip/<int:pk>/packingsum/', api.trip_packing_sum, name='trip_packing_sum'),
    # path('api/invoices/', api.InvoiceList.as_view(), name='invoice_list'),
    path('api/invoice/date_range/<int:pk>/', api.InvoiceDateRange.as_view(), name='customer_invoice_route_daterange'),
    # path('api/invoices/<int:pk>/', api.InvoiceDetail.as_view(), name='invoice_detail'),
    path('api/invoice/create/', api.InvoiceCreate.as_view(), name='invoice_create'),
    # path('api/invoices/<int:pk>/delete/', api.InvoiceDelete.as_view(), name='invoice_delete'),
    path('api/trips/<int:pk>/detail/routes/', api.TripRouteList.as_view(), name='trip_route_list'),
    path('api/trips/<int:pk>/detail/routes/add/', api.TripRouteCreate.as_view(), name='trip_route_create'),
    path('api/routes/<int:pk>/delete/', api.RouteDelete.as_view(), name='route_delete'),
    path('api/routes/<int:pk>/update/', api.RouteUpdate.as_view(), name='route_update'),
    path('api/routes/<int:pk>/', api.RouteDetail.as_view(), name='route_detail'),
    path('api/orderitem/<int:pk>/', api.OrderItemDetail.as_view(), name='orderitem_detail'),
    path('api/orderitem/<int:pk>/update/', api.OrderItemUpdate.as_view(), name='orderitem_update'),
    path('api/trips/<int:pk>/routes/arrange/', api.route_arrange, name='route_arrange'),
    path('api/invoice/getnewinvoicenumber/', api.get_invoice_number, name='get_new_invoice_number')
]

urlpatterns = format_suffix_patterns(urlpatterns)
