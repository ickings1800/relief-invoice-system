from django.urls import path

from .api import urls
from . import views

app_name = 'pos'
urlpatterns = [
    #  /pos/customers/
    path('customers/', views.CustomerIndexView.as_view(), name='customer_index'),
    #  /pos/customers/detail/<pk>/
    path('customers/detail/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    #  /pos/products/
    path('products/', views.ProductIndexView.as_view(), name='product_index'),
    #  /pos/trips/
    path('trips/', views.TripIndexView.as_view(), name='trip_index'),
    #  /pos/trips/copy/<int:pk>/
    path('trip/copy/<int:pk>/', views.TripCopyView.as_view(), name='trip_copy'),
    #  /pos/trips/detail/<int:pk>/
    path('trip/detail/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    #  /pos/trips/detail/<int:pk>/print
    path('trip/detail/<int:pk>/print/', views.print_trip_detail, name='print_trip_detail'),
    #  /pos/trips/delete/<pk>/
    path('trip/delete/<int:pk>/', views.TripDeleteView.as_view(), name='trip_delete'),
    #  /pos/trips/arrange/<pk>/
    path('trips/arrange/<int:pk>/', views.TripArrangementView, name='trip_arrange'),
    #  /pos/route/customer/<int:pk>/
    path('route/customer/<int:pk>/', views.CustomerRouteView.as_view(), name='route_customer'),
    #  /pos/route/edit/<pk>/
    path('route/edit/<int:pk>/', views.RouteEditView.as_view(), name='route_edit'),
    #  /pos/route/delete<pk>/
    path('route/delete/<int:trip_pk>/<int:route_pk>/', views.RouteDeleteView.as_view(), name='route_delete'),
    #  /pos/customerproducts/<cust_pk>/
    path('customerproducts/<int:pk>/', views.CustomerProductListView.as_view(), name='customerproduct_index'),
    #  /pos/invoice/customer_select/<cust_pk>/
    path('invoice/date_range/<int:pk>/', views.InvoiceDateRangeView, name='invoice_daterange'),
    #  /pos/invoice/invoice_history/
    path('invoice/invoice_history', views.InvoiceHistoryView.as_view(), name='invoice_history'),
    #  /pos/invoice/<invoice_pk>/
    path('invoice/<int:cust_pk>/<int:invoice_pk>/', views.InvoiceSingleView, name='invoice_view'),
    #  /pos/invoice/delete/<invoice_pk>/
    path('invoice/delete/<int:pk>', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    #  /pos/invoice/customer/<customer_pk>/
    path('invoice/customer/<int:pk>', views.InvoiceCustomerView.as_view(), name='invoice_customer'),
]

urlpatterns += urls.urlpatterns
