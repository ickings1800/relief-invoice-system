# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .validators import date_within_year
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
    date = models.DateTimeField(validators=[date_within_year])
    notes = models.CharField(max_length=255, null=True, blank=True)


class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    tel_no = models.CharField(max_length=8, null=True, blank=True)
    fax_no = models.CharField(max_length=8, null=True, blank=True)
    term = models.PositiveSmallIntegerField()
    gst = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)


class Product(models.Model):
    name = models.CharField(max_length=128)
    specification = models.CharField(max_length=255, null=True, blank=True)


class Invoice(models.Model):
    date_generated = models.DateField(auto_now=True)
    remark = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    minus = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    gst = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    original_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    net_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    net_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    total_incl_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    invoice_year = models.IntegerField(null=True, blank=False)
    invoice_number = models.IntegerField(null=True, blank=False)

    class Meta:
        unique_together = ('invoice_year', 'invoice_number')


class Route(models.Model):
    index = models.SmallIntegerField()
    do_number = models.CharField(max_length=8, blank=True)
    note = models.TextField(null=True, blank=True, max_length=255)
    invoice = models.ForeignKey(Invoice, null=True, default=None, on_delete=models.SET_NULL)
    trip = models.ForeignKey(Trip, null=True, on_delete=models.CASCADE)


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

    class Meta:
        unique_together = ('route', 'customerproduct')


class Packing(models.Model):
    name = models.CharField(max_length=128)


class Method(models.Model):
    packing = models.ForeignKey(Packing, on_delete=models.CASCADE)
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    packing_quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('orderitem', 'packing')
