# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from rest_framework.exceptions import APIException
from datetime import datetime

from .validators import date_within_year
from django.contrib.postgres.fields import JSONField
from django.db import models
from io import BytesIO

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

    def export_trip_to_pdf(trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        trip_date = datetime.strftime(trip.date, '%Y-%m-%d %H:%M:%S')
        trip_notes = trip.notes if trip.notes is not None else ''
        trip_packaging_methods = str(trip.packaging_methods).split(',')
        print(trip_packaging_methods)
        routes = Route.objects.filter(trip_id=trip.pk)
        trip_routes = sorted(routes, key=lambda route: route.index)

        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5 * cm, leftMargin=0.5 * cm,
                                topMargin=1 * cm,
                                bottomMargin=2 * cm)
        stylesheet = getSampleStyleSheet()
        styleNote = stylesheet["Normal"]
        packStyleSheet = getSampleStyleSheet()
        packNote = packStyleSheet["Normal"]
        packNote.fontSize = 7
        packNote.alignment = TA_CENTER
        packNote.leading = 10

        # container for the "Flowable" objects
        elements = []
        packaging = [Paragraph(heading, packNote) for heading in trip_packaging_methods]

        # Make heading for each column and start data list

        note_paragraph = Paragraph(trip_notes, styleNote)

        top_table_style = TableStyle([('SPAN', (0, -1), (-1, -1))])
        top_table_data = [["Date:", trip_date], [note_paragraph]]
        top_table = Table(top_table_data, [3 * cm, 10 * cm])
        top_table.hAlign = 'LEFT'
        top_table.setStyle(top_table_style)
        elements.append(top_table)
        elements.append(Spacer(1, 12))

        if trip_packaging_methods != ['None']:
            customer_table_style = TableStyle([('SPAN', (1, 0), (3, 0)),
                                               ('SPAN', (0, -1), (-1, -1)),
                                               ('GRID', (0 - len(packaging), 0), (-1, -2), 0.5, colors.black),
                                               ('LEFTPADDING', (0, 0), (-1, -1), 1),
                                               ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                                               ('TOPPADDING', (0, 0), (-1, -1), 1),
                                               ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                                               ('ALIGN', (0 - len(packaging), 0), (-1, -1), 'CENTER')])
        else:
            customer_table_style = TableStyle([('SPAN', (1, 0), (3, 0)),
                                               ('SPAN', (0, -1), (-1, -1)),
                                               ('LEFTPADDING', (0, 0), (-1, -1), 1),
                                               ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                                               ('TOPPADDING', (0, 0), (-1, -1), 1),
                                               ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                                               ('ALIGN', (0 - len(packaging), 0), (-1, -1), 'CENTER')])

        total_table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')])

        packing_column_sum = Trip.get_packing_sum(trip_id)
        total_table_data = [packaging, [str(packing_column_sum.get(p)) for p in trip_packaging_methods]]
        total_table = Table(total_table_data, [(10.5 / (len(packaging))) * cm for p in packaging])
        total_table.hAlign = 'RIGHT'
        total_table.setStyle(total_table_style)

        noteStyleSheet = getSampleStyleSheet()
        noteStyle = noteStyleSheet["Normal"]
        noteStyle.fontSize = 14
        for tr in trip_routes:
            index = str(tr.index)
            customer_name = ''
            trip_note = tr.note if tr.note is not None else ''
            orderitems = OrderItem.objects.filter(route_id=tr.pk)

            if len(orderitems) > 0:
                customer_name = orderitems[0].customerproduct.customer.name

                # First Row
                if trip_packaging_methods != ['None']:
                    route_table_data = [[index + ".", customer_name, "", ""] + packaging]
                else:
                    route_table_data = [[index + ".", customer_name, "", ""] + [""]]

                for oi in orderitems:
                    row = ["", oi.quantity, Paragraph(oi.customerproduct.product.name, styleNote), ""]
                    # Second Row
                    oi_packing = oi.packing
                    if oi_packing:
                        for packing in trip_packaging_methods:
                            quantity = oi_packing.get(packing)
                            if quantity:
                                row.append(quantity)
                            else:
                                row.append('')
                    route_table_data.append(row)
                # Last Row
                route_table_data.append([trip_note])
                customer_table = Table(route_table_data,
                                       [0.5 * cm, 1 * cm, 4 * cm, 4 * cm] + [(10.5 / (len(packaging))) * cm for p in
                                                                             packaging])
                customer_table.hAlign = 'CENTER'
                customer_table.setStyle(customer_table_style)
                elements.append(customer_table)
                elements.append(Spacer(1, 12))
            else:
                note = Paragraph(index + ". " + trip_note, noteStyle)
                elements.append(note)
                elements.append(Spacer(1, 12))

        if trip_packaging_methods != ['None']:
            elements.append(total_table)
        elements.append(Spacer(1, 12))

        doc.build(elements)
        return buffer


class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    tel_no = models.CharField(max_length=8, null=True, blank=True)
    fax_no = models.CharField(max_length=8, null=True, blank=True)
    term = models.PositiveSmallIntegerField(null=True, blank=True)
    gst = models.DecimalField(default=7, max_digits=1, decimal_places=0)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128)
    specification = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


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
    customer = models.ForeignKey(Customer, null=False, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('invoice_year', 'invoice_number')

    def get_customer_invoices(customer_id):
        return Invoice.objects.filter(route__orderitem__customerproduct__customer_id=customer_id).distinct('pk')

    def get_next_invoice_number():
        invoice_num_max = Invoice.objects.all().aggregate(models.Max('invoice_number'))
        # this condition only occurs on the first invoice (with gst) created.
        if invoice_num_max.get('invoice_number__max') is None:
            return 0
        else:
            return invoice_num_max.get('invoice_number__max') + 1

    def generate_invoice(customer_id, customer_gst, start_date, end_date, invoice_year, invoice_number, route_id_list):
        invoice = Invoice(gst=int(customer_gst), start_date=start_date, end_date=end_date)
        invoice.customer_id = customer_id
        invoice.save()
        original_total = 0
        for r in route_id_list:
            route = get_object_or_404(Route, id=r)
            route.invoice = invoice
            orderitems = route.orderitem_set.all()
            for oi in orderitems:
                quote = oi.customerproduct.quote_price
                oi.unit_price = quote
                oi.save()
                original_total += (oi.driver_quantity * oi.unit_price)
            route.save()

        net_total = original_total
        # GST value is a whole number in model
        gst = float(original_total) * (int(customer_gst) / 100)
        invoice.net_total = net_total
        invoice.original_total = original_total
        invoice.net_gst = gst
        invoice.total_incl_gst = float(net_total) + gst
        if int(customer_gst) > 0:
            invoice.invoice_year = invoice_year
            invoice.invoice_number = invoice_number
        invoice.save()
        return invoice.pk

    def export_invoice_to_pdf(invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        customer_name = invoice.customer.name
        customer_term = invoice.customer.term
        customer_gst = invoice.gst
        customer_id = invoice.customer.pk
        invoice_number = invoice.invoice_number
        invoice_year = invoice.invoice_year
        start_date = invoice.start_date
        end_date = invoice.end_date
        minus = invoice.minus
        gst = invoice.gst
        original_total = invoice.original_total
        net_total = invoice.net_total
        net_gst = invoice.net_gst
        total_incl_gst = invoice.total_incl_gst
        remark = invoice.remark
        date_generated = invoice.date_generated
        routes = Route.objects.filter(invoice_id=invoice_id)

        customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)
        customerproduct_headings = [cp.product.name for cp in customerproducts]
        quantity_row = {cp: 0 for cp in customerproduct_headings}
        unit_price_row = {cp.product.name: cp.quote_price for cp in customerproducts}
        nett_amt_row = {cp: 0 for cp in customerproduct_headings}

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm,
                                bottomMargin=2 * cm)

        # container for the "Flowable" objects
        elements = list()

        # Make heading for each column and start data list

        top_table_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9)])

        top_table_data = list()
        top_table_data.append(["SUN-UP BEAN FOOD MFG PTE LTD", "TAX INVOICE"])
        address_invoice_number_row = ["TUAS BAY WALK #02-30 SINGAPORE 637780"]
        if invoice_number is not None:
            address_invoice_number_row.append("INVOICE NUMBER:")
            address_invoice_number_row.append(invoice_year + " " + invoice_number)
        top_table_data.append(address_invoice_number_row)
        top_table_data.append(["TEL: 68639035 FAX: 68633738", "DATE: ", "{0}".format(end_date)])
        top_table_data.append(["REG NO: 200302589N", "TERMS: ", str(customer_term) + " DAYS"])
        top_table_data.append(["BILL TO"])
        top_table_data.append([customer_name])

        top_table = Table(top_table_data, [12 * cm, 4 * cm, 3 * cm])
        top_table.setStyle(top_table_style)

        # Assemble data for each column using simple loop to append it into data list

        product_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                                    ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
                                    ('FONTSIZE', (0, 0), (-1, -1), 9)])

        product_data = [["DATE"] + customerproduct_headings + ["D/O"]]
        table_width = (19 / len(product_data[0])) * cm

        for r in routes:
            # Remove time part of trip date
            row_date = datetime.strftime(r.trip.date, "%Y-%m-%d")
            row = [row_date]
            orderitems = OrderItem.objects.filter(route_id=r.pk)
            orderitems_qty = {oi.customerproduct.product.name: oi.quantity for oi in orderitems}
            print(r)
            for cp_heading in customerproduct_headings:
                orderitem_qty = orderitems_qty.get(cp_heading)
                if orderitem_qty:
                    print(cp_heading, orderitem_qty)
                    quantity_row[cp_heading] += orderitem_qty
                    row.append(str(orderitem_qty))
                else:
                    row.append("")

            row_do_number = r.do_number
            row.append(row_do_number)
            product_data.append(row)
        print(product_data)
        product_table = Table(product_data, [table_width for i in range(len(product_data))], repeatRows=1,
                              rowHeights=16)
        product_table.hAlign = 'CENTER'
        product_table.setStyle(product_style)

        quantity_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                     ('FONTSIZE', (0, 0), (-1, -1), 9)])

        for cp in customerproduct_headings:
            quantity = quantity_row.get(cp)
            unit_price = float(unit_price_row.get(cp))
            nett_amt = quantity * unit_price
            nett_amt_row[cp] = round(nett_amt, 4)

        quantity_data = list()

        quantity_data.append(["QUANTITY"] + [quantity_row.get(cp) for cp in customerproduct_headings] + [""])
        quantity_data.append(["UNIT PRICE ($)"] + [unit_price_row.get(cp) for cp in customerproduct_headings] + [""])
        quantity_data.append(
            ["NETT AMOUNT ($)"] + ['%.4f' % nett_amt_row.get(cp) for cp in customerproduct_headings] + [""])
        quantity_table = Table(quantity_data, [table_width for i in range(len(product_data))])
        quantity_table.hAlign = 'CENTER'
        quantity_table.setStyle(quantity_style)

        total_data_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9),
                                       ('GRID', (1, 0), (-1, -1), 0.5, colors.black)])
        total_data = list()
        total_data.append(["SUB-TOTAL ($)", "{0}".format(original_total)])
        total_data.append(["MINUS ($)", "{0}".format(minus)])
        total_data.append(["GST ({0}%)".format(gst), "{0}".format(net_gst)])
        total_data.append(["TOTAL (inc. GST) ($)", "{0}".format(total_incl_gst)])
        total_data_table = Table(total_data)
        total_data_table.hAlign = 'RIGHT'
        total_data_table.setStyle(total_data_style)

        elements.append(top_table)
        elements.append(product_table)
        elements.append(quantity_table)
        elements.append(total_data_table)

        doc.build(elements)
        return buffer


class Route(models.Model):
    index = models.SmallIntegerField()
    do_number = models.CharField(max_length=8, null=True, blank=True)
    note = models.TextField(null=True, blank=True, max_length=255)
    invoice = models.ForeignKey(Invoice, null=True, default=None, on_delete=models.SET_NULL)
    trip = models.ForeignKey(Trip, null=True, on_delete=models.CASCADE)

    def get_customer_routes(customer_id):
        route_list = Route.objects.filter(orderitem__customerproduct__customer_id=customer_id) \
            .filter((Q(orderitem__quantity__gt=0) | Q(orderitem__driver_quantity__gt=0))) \
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
