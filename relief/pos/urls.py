from django.urls import path

from . import views

app_name = 'pos'
urlpatterns=[
    #  /pos/customers/
    path('customers/', views.CustomerIndexView.as_view(), name='customer_index'),
    #  /pos/customers/create
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer_create'),
    # /pos/customers/edit/<pk>/
    path('customers/edit/<int:pk>/', views.CustomerEditView.as_view(), name='customer_edit'),
    #  /pos/customers/detail/<pk>/
    path('customers/detail/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    #  /pos/products/
    path('products/', views.ProductIndexView.as_view(), name='product_index'),
    #  /pos/products/create
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    #  /pos/products/edit/<pk>/
    path('products/edit/<int:pk>/', views.ProductEditView.as_view(), name='product_edit'),
    #  /pos/trips/
    path('trips/', views.TripIndexView.as_view(), name='trip_index'),
    #  /pos/trips/create
    path('trips/create/', views.TripCreateView.as_view(), name='trip_create'),
    #  /pos/trips/detail/<int:pk>/
    path('trips/detail/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    #  /pos/trips/edit/<pk>/
    path('trips/edit/<int:pk>/', views.TripEditView.as_view(), name='trip_edit'),
    #  /pos/trips/delete/<pk>/
    path('trips/delete/<int:pk>/', views.TripDeleteView.as_view(), name='trip_delete'),
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
    #  /pos/customerproducts/create/<cust_pk>/
    path('customerproducts/create/<int:pk>/', views.CustomerProductCreateView.as_view(), name='customerproduct_create'),
    #  /pos/customerproducts/edit/<cust_pk>/
    path('customerproducts/edit/<int:pk>/', views.CustomerProductUpdateView.as_view(), name='customerproduct_edit'),
    #  /pos/invoice/customer_select/<cust_pk>/
    path('invoice/date_range/<int:pk>/', views.InvoiceDateRangeView, name='invoice_daterange'),
    #  /pos/invoice/order_assign/
    path('invoice/order_assign/<int:pk>/', views.InvoiceOrderAssignView, name='invoice_orderassign'),
    #  /pos/invoice/invoice_history/
    path('invoice/invoice_history', views.InvoiceHistoryView.as_view(), name='invoice_history'),
    #  /pos/invoice/<invoice_pk>/
    path('invoice/<int:pk>', views.InvoiceSingleView, name='invoice_view'),
    #  /pos/invoice/delete/<invoice_pk>/
    path('invoice/delete/<int:pk>', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    #  /pos/invoice/customer/<customer_pk>/
    path('invoice/customer/<int:pk>', views.InvoiceCustomerView.as_view(), name='invoice_customer'),
]
