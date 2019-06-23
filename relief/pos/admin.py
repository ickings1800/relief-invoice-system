from django.contrib import admin
from django.shortcuts import get_object_or_404
from .models import Trip, Customer, Product, Invoice, Route, CustomerProduct, OrderItem
# Register your models here.


class AdminCustomer(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AdminProduct(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AdminTrip(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AdminCustomerProduct(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'customer':
            customer_id = request.GET.get('customer')
            kwargs['queryset'] = Customer.objects.filter(id=customer_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['product', 'customer']
        else:
            return []

    def has_delete_permission(self, request, obj=None):
        return False



admin.site.register(Customer, AdminCustomer)
admin.site.register(Product, AdminProduct)
admin.site.register(Trip, AdminTrip)
admin.site.register(CustomerProduct, AdminCustomerProduct)
