from django.urls import path
from django.contrib.auth import views as auth_views
from .api import urls
from . import views

app_name = 'pos'
urlpatterns = [
    #  /pos/customers/detail/<pk>/
    path('quotes/', views.overview, name='overview'),
    #  /pos/invoice/<int:pk>/
    path('invoice/<int:pk>/', views.InvoiceSingleView, name='invoice_detail'),
    #  /pos/invoice/pdf/
    path('invoice/pdf/', views.download_invoice, name='invoice_download_range'),
    #  /pos/invoice/<int:pk>/pdf/
    path('invoice/<int:pk>/pdf/', views.download_invoice, name='invoice_download'),
    #  /pos/orderitem/summary/
    path('orderitem/summary/', views.orderitem_summary, name='orderitem_summary'),
    #  /pos/invoice/export/
    path('invoice/export/', views.export_invoice, name='invoice_export'),
    #  /pos/quotes/export/
    path('quotes/export/', views.export_quote, name='export_quote'),
    #  /pos/express/
    path('express/', views.express_order, name='express_order'),
    #  /pos/import/
    path('import/', views.import_items, name='import_items'),
    #  /pos/login
    path('login/', auth_views.LoginView.as_view(template_name='pos/login.html'), name='login'),
    #  /pos/logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #  /pos/token/
    path('token/', views.get_token, name='get_freshbooks_token'),
    #  /pos/token/redirect
    path('token/redirect/', views.redirect_to_freshbooks_auth, name='freshbooks_redirect')
]

urlpatterns += urls.urlpatterns
