# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException

from .validators import date_within_year
from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=6)
    tel_no = models.CharField(max_length=8)
    business_no = models.CharField(max_length=10)
    fax_no = models.CharField(max_length=8)


class Trip(models.Model):
    date = models.DateTimeField()
    notes = models.CharField(max_length=255, null=True, blank=True)
    packaging_methods = models.CharField(max_length=255, null=True, blank=True)

    def create_route(trip_id, note, customer_id=None):
        trip = get_object_or_404(Trip, id=trip_id)
        route_list = Route.objects.filter(trip_id=trip.pk)
        route_indexes = [r.index for r in route_list]
        route = Route.objects.create(index=max(route_indexes, default=0) + 1, trip=trip, note=note)

        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            customer_id = customer.pk
            customer_products = CustomerProduct.objects.filter(customer_id=customer_id)

            for cp in customer_products:
                orderitem = OrderItem.objects.create(customerproduct=cp, route=route)
        print("Create route")
        return route

    def rearrange_trip_routes_after_delete(trip_id):
        route_list = Route.objects.filter(trip_id=trip_id).order_by('index')
        for i in range(len(route_list)):
            route_list[i].index = i+1
            route_list[i].save()

    def arrange_route_index(trip_id, arrangement):
        trip = get_object_or_404(Trip, id=trip_id)
        route_list = Route.objects.filter(trip_id=trip.pk)
        route_id_list = [r.pk for r in route_list]
        contains = all(elem in arrangement for elem in route_id_list)
        if contains:
            for r in route_list:
                r.index = arrangement.index(r.pk) + 1
                r.save()
        else:
            raise APIException('Unable to parse route_id_list')

    def get_packing_sum(trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        packing_sum = {packing: 0 for packing in trip.packaging_methods.split(',')}
        route_list = Route.objects.filter(trip_id=trip.pk)
        for route in route_list:
            orderitems = OrderItem.objects.filter(route_id=route.pk)
            for oi in orderitems:
                packing = oi.packing
                if packing:
                    for k in packing_sum:
                        if packing.get(k):
                            packing_sum[k] += packing.get(k)
        return packing_sum


class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    tel_no = models.CharField(max_length=8, null=True, blank=True)
    fax_no = models.CharField(max_length=8, null=True, blank=True)
    term = models.PositiveSmallIntegerField()
    gst = models.DecimalField(default=0.00, max_digits=2, decimal_places=0)


class Product(models.Model):
    name = models.CharField(max_length=128)
    specification = models.CharField(max_length=255, null=True, blank=True)


class Invoice(models.Model):
    date_generated = models.DateField(auto_now=True)
    remark = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    minus = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    gst = models.DecimalField(default=0.00, max_digits=2, decimal_places=0)
    original_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    net_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    net_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    total_incl_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    invoice_year = models.IntegerField(null=True, blank=False)
    invoice_number = models.IntegerField(null=True, blank=False)

    class Meta:
        unique_together = ('invoice_year', 'invoice_number')

    def get_customer_invoices(customer_id):
        return Invoice.objects.filter(route__orderitem__customerproduct__customer_id=customer_id).distinct('pk')


class Route(models.Model):
    index = models.SmallIntegerField()
    do_number = models.CharField(max_length=8, blank=True)
    note = models.TextField(null=True, blank=True, max_length=255)
    invoice = models.ForeignKey(Invoice, null=True, default=None, on_delete=models.SET_NULL)
    trip = models.ForeignKey(Trip, null=True, on_delete=models.CASCADE)

    def get_customer_routes(customer_id):
        route_list = Route.objects.filter(orderitem__customerproduct__customer_id=customer_id) \
            .filter((Q(orderitem__quantity__gt=0) | Q(orderitem__driver_quantity__gt=0))) \
            .distinct()
        return route_list


class CustomerProduct(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quote_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)

    class Meta:
        unique_together = ('customer', 'product')


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField(default=0)
    driver_quantity = models.PositiveSmallIntegerField(default=0)
    note = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    customerproduct = models.ForeignKey(CustomerProduct, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    packing = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('route', 'customerproduct')
