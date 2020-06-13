# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.postgres.fields import JSONField
from rest_framework.exceptions import APIException
from datetime import date
import uuid

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

    def create_route(trip_id, note, customer_id=None, do_number=None):
        trip = get_object_or_404(Trip, id=trip_id)
        route_list = Route.objects.filter(trip_id=trip.pk)
        route_indexes = [r.index for r in route_list]
        route = Route.objects.create(index=max(route_indexes, default=0) + 1, trip=trip, note=note, do_number=do_number)

        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            customer_id = customer.pk
            customer_products = CustomerProduct.objects.filter(customer_id=customer_id)

            for cp in customer_products:
                orderitem = OrderItem.objects.create(customerproduct=cp, route=route)
        print("Create route")
        return route

    def duplicate_trip(trip_id):
        trip_copy = get_object_or_404(Trip, id=trip_id)
        if trip_copy:
            new_trip = Trip.objects.create(
                date=trip_copy.date,
                notes=trip_copy.notes,
                packaging_methods=trip_copy.packaging_methods
            )
            new_trip.save()
            for r in trip_copy.route_set.all():
                orderitems = [OrderItem(quantity=oi.quantity,
                                        driver_quantity=0,
                                        note=oi.note,
                                        customerproduct=oi.customerproduct,
                                        packing=oi.packing) for oi in r.orderitem_set.all()]

                # reset routes primary key to none so that can save to db.
                r.pk = None
                # reset do_number from previous trip
                r.do_number = ""
                r.invoice = None
                r.trip = new_trip
                r.save()
                for oi in orderitems:
                    oi.route = r
                    oi.pk = None
                    oi.save()
            return new_trip

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
        if trip.packaging_methods:
            packing_sum = {packing.strip(): 0 for packing in trip.packaging_methods.split(',')}
            route_list = Route.objects.filter(trip_id=trip.pk)
            for route in route_list:
                orderitems = OrderItem.objects.filter(route_id=route.pk)
                for oi in orderitems:
                    packing = oi.packing
                    if packing:
                        for k in packing_sum:
                            if packing.get(k):
                                packing_sum[k] += int(packing.get(k))
            return packing_sum
        else:
            return dict()

    def get_trips_by_date(start_date, end_date):
        trips = Trip.objects.filter(date__lte=end_date, date__gte=start_date).order_by('date')
        return trips


class Group(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name

    def group_create(name):
        group_exists = Group.objects.filter(name=name)
        if len(group_exists) > 0:
            raise Exception("Group with the name of '{}' already exists.".format(name))
        new_group = Group.objects.create(name=name)
        return new_group

    def group_change(pk, group_id):
        if pk and group_id:
            customer_group = CustomerGroup.objects.get(pk=pk)
            group = Group.objects.get(pk=group_id)
            prev_customergroup_group_id = customer_group.group_id
            next_group_index = len(CustomerGroup.objects.filter(group_id=group_id)) + 1
            customer_group.group = group
            customer_group.index = next_group_index
            customer_group.save()
            Group.customergroup_index_rearrange(prev_customergroup_group_id)

    def customergroup_index_rearrange(group_id):
        customergroup_rerrange = CustomerGroup.objects.filter(group_id=group_id).order_by('index')
        for i in range(len(customergroup_rerrange)):
            customergroup = customergroup_rerrange[i]
            ordering = i + 1
            if customergroup.index != ordering:
                customergroup.index = ordering
                customergroup.save()


class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    tel_no = models.CharField(max_length=8, null=True, blank=True)
    fax_no = models.CharField(max_length=8, null=True, blank=True)
    term = models.PositiveSmallIntegerField(null=True, blank=True)
    gst = models.DecimalField(default=7, max_digits=1, decimal_places=0)
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name


class CustomerGroup(models.Model):
    index = models.IntegerField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True)

    def customergroup_swap(customer_groups, customergroup_list_arrangement):
        if customergroup_list_arrangement and len(customergroup_list_arrangement) == len(customer_groups):
            for cg in customer_groups:
                try:
                    customergroup_index = customergroup_list_arrangement.index(cg.pk) + 1
                except ValueError as e:
                    print(e)
                    break
                if cg.index != customergroup_index:
                    cg.index = customergroup_index
                    cg.save()

    def next_customer_group(customer_id):
        cg = CustomerGroup.objects.filter(customer_id=customer_id)[0]
        next_customer_group = CustomerGroup.objects.filter(index__gt=cg.index).order_by('index')
        if len(next_customer_group) > 0:
            return next_customer_group[0]

    def prev_customer_group(customer_id):
        cg = CustomerGroup.objects.filter(customer_id=customer_id)[0]
        prev_customer_group = CustomerGroup.objects.filter(index__lt=cg.index).order_by('index')
        if len(prev_customer_group) > 0:
            return prev_customer_group[0]


class Product(models.Model):
    name = models.CharField(max_length=128)
    specification = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    date_generated = models.DateField(auto_now=True)
    remark = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    minus = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    gst = models.DecimalField(default=0.00, max_digits=2, decimal_places=0)
    original_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    net_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    net_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    total_incl_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    invoice_year = models.IntegerField(null=True, blank=False)
    invoice_number = models.IntegerField(null=True, blank=False)
    customer = models.ForeignKey(Customer, null=False, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('invoice_year', 'invoice_number')

    def get_customer_invoices(customer_id):
        return Invoice.objects.filter(route__orderitem__customerproduct__customer_id=customer_id).distinct('pk')

    def get_customer_latest_invoice(customer_id):
        invoices = Invoice.objects.filter(customer_id=customer_id).order_by('-date_generated')
        if len(invoices) > 0:
            return invoices[0]
        else:
            return None

    def generate_invoice(customer_id, customer_gst, start_date, end_date, invoice_year, invoice_number, route_id_list):
        selected_routes = []
        for r in route_id_list:
            try:
                route = Route.objects.get(pk=r)
            except Route.DoesNotExist:
                raise ValueError("Route ID:{0} does not exist".format(r))
            if route.invoice_id:
                raise ValueError("Route ID:{0} has an Invoice".format(r))
            selected_routes.append(route)

        invoice = Invoice(customer_id=customer_id)
        invoice.save()

        # check whether route already has an invoice, and ensure every route is found.
        original_total = 0
        for r in selected_routes:
            r.invoice = invoice
            orderitems = r.orderitem_set.all()
            for oi in orderitems:
                quote = oi.customerproduct.quote_price
                oi.unit_price = quote
                oi.save()
                original_total += (oi.driver_quantity * oi.unit_price)
            r.save()

        net_total = original_total

        # Invoice implementation not done yet. All values will be zero.
        # GST value is a whole number in model
        if invoice.gst > 0:
            gst = float(original_total) * (int(customer_gst) / 100)
        else:
            gst = 0
        invoice.net_total = net_total
        invoice.original_total = original_total
        invoice.net_gst = gst
        invoice.total_incl_gst = float(net_total) + gst
        invoice.save()
        return invoice


    def get_customer_routes_for_invoice(invoice_id):
        route_list_dict = list()
        route_list = Route.objects.filter(invoice_id=invoice_id).order_by('trip__date')
        for r in route_list:
            row_dict = dict()
            trip_date = r.trip.date
            do_number = r.do_number
            row_dict['trip_date'] = trip_date
            row_dict['do_number'] = do_number
            for oi in r.orderitem_set.all():
                orderitem_name = oi.customerproduct.product.name
                orderitem_driver_quantity = oi.quantity
                row_dict[orderitem_name] = orderitem_driver_quantity
            route_list_dict.append(row_dict)
        return route_list_dict

    def get_invoice_customerproduct_sum(route_list_dict, customerproducts):
        customerproduct_dict = {cp.product.name: 0 for cp in customerproducts}
        print(route_list_dict)
        for row in route_list_dict:
            for cp in customerproduct_dict.keys():
                customerproduct_dict[cp] += row[cp]
        return customerproduct_dict

    def get_invoice_customerproduct_nett_amt(customerproduct_quantity_sum_dict, customerproducts):
        customerproduct_nett_dict = {cp.product.name: 0 for cp in customerproducts}
        for cp in customerproducts:
            customerproduct_nett = customerproduct_quantity_sum_dict[cp.product.name] * cp.quote_price
            customerproduct_nett_dict[cp.product.name] = customerproduct_nett
        return customerproduct_nett_dict



class Route(models.Model):
    index = models.SmallIntegerField()
    do_number = models.CharField(max_length=8, null=True, blank=True)
    note = models.TextField(null=True, blank=True, max_length=255)
    invoice = models.ForeignKey(Invoice, null=True, default=None, on_delete=models.SET_NULL)
    trip = models.ForeignKey(Trip, null=True, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)

    # Route automatically defaults to order by index ascending in database model level
    class Meta:
        ordering = ['index']

    def get_customer_routes_for_invoice(customer_id):
        route_list = Route.objects.filter(orderitem__customerproduct__customer_id=customer_id, checked=True, invoice=None)\
            .order_by('trip__date')\
            .distinct()
        return route_list

    def get_customer_detail_routes(customer_id):
        route_list = Route.objects.filter(orderitem__customerproduct__customer_id=customer_id, invoice=None)\
            .order_by('trip__date')\
            .distinct()
        return route_list

    def get_customer_routes_orderitems_by_date(date_start, date_end, customer_id):
        route_list = Route.objects.filter(trip__date__lte=date_end,
                                          trip__date__gte=date_start,
                                          invoice__exact=None,
                                          orderitem__customerproduct__customer_id=customer_id).order_by('trip__date')\
            .distinct()
        return route_list


class CustomerProduct(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quote_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    index = models.PositiveIntegerField(null=False)

    # Customerproduct automatically defaults to order by index ascending
    class Meta:
        ordering = ['index']

    def get_latest_customerproducts(customer_id):
        customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)
        # for cp in customerproduct_ids:
        #     latest_cp = CustomerProduct.objects.filter(Q(end_date__isnull=True) | Q(end_date__gte=date.today()),
        #                                                customer_id=cp.customer_id,
        #                                                product_id=cp.product_id).latest('start_date').order_by('index')
        return customerproducts

    def get_customerproducts_by_date(customer_id, start_date, end_date):
        customerproducts = CustomerProduct.objects.filter(customer_id=customer_id,
                                                          start_date__gte=start_date,
                                                          end_date__lte=end_date)
        return customerproducts


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField(default=0)
    driver_quantity = models.PositiveSmallIntegerField(default=0)
    note = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    customerproduct = models.ForeignKey(CustomerProduct, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    packing = JSONField(null=True, blank=True)

    # Orderitem automatically defaults to order by index ascending depending on customerproduct
    class Meta:
        unique_together = ('route', 'customerproduct')
        ordering = ['customerproduct__index']

    def get_orderitem_summary_by_date(customer_id, start_date, end_date):
        return OrderItem.objects.filter(route__trip__date__lte=end_date,
                                        route__trip__date__gte=start_date,
                                        customerproduct__customer_id=customer_id)\
            .order_by('route__trip__date')
