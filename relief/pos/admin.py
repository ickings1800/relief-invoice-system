from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Customer, Product, Invoice, Route, CustomerProduct, OrderItem, CustomerGroup, Group
# Register your models here.


class AdminCustomer(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AdminProduct(admin.ModelAdmin):
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

    def response_add(self, request, obj, post_url_continue=None):
        customer_id = request.GET.get('customer')
        return redirect(reverse('admin:pos_customerproduct_add') + '?customer={0}'.format(customer_id))


class AdminGroup(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


# admin.site.register(Group, AdminGroup)
# admin.site.register(Customer, AdminCustomer)
# admin.site.register(Product, AdminProduct)
# admin.site.register(CustomerProduct, AdminCustomerProduct)
