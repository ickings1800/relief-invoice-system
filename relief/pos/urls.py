from django.urls import path
from django.contrib.auth import views as auth_views
from .api import urls
from . import views

app_name = 'pos'
urlpatterns = [
    #  /pos/customers/
    path('customers/', views.CustomerIndexView, name='customer_index'),
    #  /pos/customers/detail/<pk>/
    path('customers/detail/<int:id>/', views.CustomerDetailView, name='customer_detail_view'),
    #  /pos/products/
    path('products/', views.ProductIndexView.as_view(), name='product_index'),
    #  /pos/trips/
    path('trips/', views.TripIndexView.as_view(), name='trip_index'),
    #  /pos/trips/copy/<int:pk>/
    path('trip/copy/<int:pk>/', views.TripCopyView.as_view(), name='trip_copy'),
    #  /pos/trips/detail/<int:pk>/
    path('trip/detail/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    #  /pos/trips/detail/<int:pk>/
    path('trip/detail/<int:pk>/print/', views.TripDetailPDFView.as_view(), name='trip_print'),
    #  /pos/trips/delete/<pk>/
    path('trip/delete/<int:pk>/', views.TripDeleteView.as_view(), name='trip_delete'),
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
    path('invoice/<int:invoice_pk>/', views.InvoiceSingleView.as_view(), name='invoice_view'),
    #  /pos/invoice/<invoice_pk>/pdf/
    path('invoice/<int:invoice_pk>/pdf/', views.InvoiceSinglePDFView.as_view(), name='invoice_pdf_view'),
    #  /pos/invoice/delete/<invoice_pk>/
    path('invoice/delete/<int:pk>', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    #  /pos/invoice/customer/<customer_pk>/
    path('invoice/customer/<int:pk>', views.InvoiceCustomerView.as_view(), name='invoice_customer'),
    #  /pos/login
    path('login/', auth_views.LoginView.as_view(template_name='pos/login.html'), name='login'),
    #  /pos/logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += urls.urlpatterns
