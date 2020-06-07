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
    #  /pos/trip/detail/<int:pk>/
    path('trip/detail/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    #  /pos/trip/detail/<int:pk>/print/
    path('trip/detail/<int:pk>/print/', views.TripDetailPDFView.as_view(), name='trip_detail_print'),
    #  /pos/trip/detail<int:pk>/print/test/
    path('trip/detail/<int:pk>/print/test/', views.TripDetailPrintView.as_view(), name='trip_detail_test'),
    #  /pos/orderitem/summary/
    path('orderitem/<int:pk>/summary/', views.orderitem_summary, name='orderitem_summary'),
    #  /pos/login
    path('login/', auth_views.LoginView.as_view(template_name='pos/login.html'), name='login'),
    #  /pos/logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += urls.urlpatterns
