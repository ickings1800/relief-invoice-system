# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Q, Max, IntegerField, JSONField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from rest_framework.exceptions import APIException
from datetime import date, datetime
from requests_oauthlib import OAuth2Session
import csv

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=6)
    tel_no = models.CharField(max_length=8)
    business_no = models.CharField(max_length=10)
    fax_no = models.CharField(max_length=8)


class Trip(models.Model):
    notes = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['pk']


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
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=False)
    postal_code = models.CharField(max_length=255, null=True, blank=False)
    country = models.CharField(max_length=128, null=True, blank=False)
    gst = models.DecimalField(default=7, max_digits=1, decimal_places=0)
    freshbooks_account_id = models.CharField(max_length=8, null=True, blank=False)
    freshbooks_client_id = models.CharField(max_length=8, null=True, blank=False)
    pivot_invoice = models.BooleanField(default=False)
    download_prefix = models.CharField(max_length=128, null=True, blank=False)
    download_suffix = models.CharField(max_length=128, null=True, blank=False)
    to_print = models.BooleanField(default=False)
    to_fax = models.BooleanField(default=False)
    to_email = models.BooleanField(default=False)
    to_whatsapp = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']


    def __str__(self):
        return self.name

    def get_download_file_name(self, invoice_number):
        invoice_name = ''

        if self.download_prefix:
            invoice_name += self.download_prefix + '_'

        invoice_name += str(invoice_number)

        if self.download_suffix:
            invoice_name += '_' + self.download_suffix
        if self.to_whatsapp:
            invoice_name += '_whatsapp'
        if self.to_email:
            invoice_name += '_email'
        if self.to_fax:
            invoice_name += '_fax'
        if self.to_print:
            invoice_name += '_print'

        return invoice_name

    def handle_customer_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        default_group = Group.objects.filter(name='Default').first()
        for row in csv_reader:
            row_client = Customer(name=row["name"], gst=row["gst"])
            row_client.save()
            assign_group = row["group"]
            if assign_group and len(assign_group) > 0:
                group = Group.objects.filter(name=assign_group).first()
                if not group:
                    group = Group(name=assign_group)
                    group.save()
                customer_group = CustomerGroup(group=group, customer=row_client)
                customer_group.save()
            else:
                customer_group = CustomerGroup(group=default_group, customer=row_client)
                customer_group.save()

    def import_freshbooks_clients(import_clients, freshbooks_account_id, token):
        default_group = Group.objects.filter(name='Default').first()
        if not default_group:
            new_group = Group(name='Default')
            new_group.save()
            default_group = new_group

        for client in import_clients:
            if client.get('organization', ''):
                client_name = client.get('organization', '')
            else:
                client_name = client.get('fname', '') + client.get('lname', '')
            client_address = client.get('p_street')
            client_postal_code = client.get('p_code')
            client_country = client.get('p_country')
            client_id = client.get('id')
            client_accounting_systemid = client.get('accounting_systemid')
            new_client = Customer(
                name=client_name, address=client_address, postal_code=client_postal_code,
                country=client_country, freshbooks_client_id=client_id,
                freshbooks_account_id=client_accounting_systemid
            )
            new_client.save()
            customer_group = CustomerGroup(group=default_group, customer=new_client)
            customer_group.save()


    def get_freshbooks_client(freshbooks_account_id, freshbooks_client_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/users/clients/{1}".format(freshbooks_account_id, freshbooks_client_id)).json()
        #  print(res)
        return res

    def get_freshbooks_clients(freshbooks_account_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        page = 1
        client_arr = []
        while(True):
            res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/users/clients?page={1}".format(freshbooks_account_id, page)).json()
            #  print(res)
            max_pages = res.get('response')\
                            .get('result')\
                            .get('pages')

            curr_page = res.get('response')\
                            .get('result')\
                            .get('page')

            clients = res.get('response')\
                            .get('result')\
                            .get('clients')

            for client in clients:
                client_arr.append(client)
            if curr_page == max_pages:
                break
            else:
                page += 1
        return client_arr


    def update_freshbooks_clients(freshbooks_account_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        page = 1
        client_arr = []
        while(True):
            res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/users/clients?page={1}".format(freshbooks_account_id, page)).json()
            max_pages = res.get('response')\
                            .get('result')\
                            .get('pages')

            curr_page = res.get('response')\
                            .get('result')\
                            .get('page')

            clients = res.get('response')\
                            .get('result')\
                            .get('clients')

            for client in clients:
                client_arr.append(client)
            if curr_page == max_pages:
                break
            else:
                page += 1

        for client in client_arr:
            client_id = str(client.get('id'))
            if client.get('organization', ''):
                client_name = client.get('organization', '')
            else:
                client_name = client.get('fname', '') + client.get('lname', '')
            client_address = client.get('p_street')
            client_postal_code = client.get('p_code')
            client_country = client.get('p_country')
            client_accounting_systemid = client.get('accounting_systemid')

            client_queryset = Customer.objects.filter(
                freshbooks_client_id=client_id, freshbooks_account_id=client_accounting_systemid
            )
            if client_queryset.count() > 0:
                update_client = client_queryset.get()
                if update_client.freshbooks_client_id == client_id:
                    print(client_name, client_address, client_postal_code, client_country)
                    update_client.name = client_name
                    update_client.address = client_address
                    update_client.postal_code = client_postal_code
                    update_client.country = client_country
                    update_client.save()



class CustomerGroup(models.Model):
    index = models.IntegerField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True)

    def update_grouping(group_id, client_id_list):
        group = Group.objects.filter(id=group_id).first()
        if group:
            if len(client_id_list) > 0:
                client_list = Customer.objects.filter(id__in=client_id_list)
                if len(client_list) == len(client_id_list):
                    #  all customers are valid
                    CustomerGroup.objects.filter(group=group).delete()
                    for index in range(len(client_list)):
                        new_grouping = CustomerGroup(customer=client_list[index], group=group, index=index)
                        new_grouping.save()
            else:
                #  empty the group
                print('empty the group')
                CustomerGroup.objects.filter(group=group).delete()
        updated_grouping = Customer.objects.filter(id__in=client_id_list)
        return updated_grouping


class Product(models.Model):
    name = models.CharField(max_length=128)
    unit_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    freshbooks_item_id = models.CharField(max_length=12, null=True, blank=False)
    freshbooks_account_id = models.CharField(max_length=12, null=True, blank=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def handle_product_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row_product = Product(name=row["name"])
            row_product.save()

    def get_freshbooks_products(freshbooks_account_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        page = 1
        item_arr = []
        while(True):
            print(page)
            res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/items/items?page={1}".format(freshbooks_account_id, page)).json()
            print(res)
            max_pages = res.get('response')\
                            .get('result')\
                            .get('pages')

            curr_page = res.get('response')\
                            .get('result')\
                            .get('page')

            items = res.get('response')\
                            .get('result')\
                            .get('items')

            for item in items:
                item_arr.append(item)
            if curr_page == max_pages:
                break
            else:
                page += 1
        return item_arr


    def freshbooks_product_detail(freshbooks_item_id, freshbooks_account_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/items/items/{1}".format(freshbooks_account_id, freshbooks_item_id)).json()
        print(res)
        return res

    def freshbooks_import_products(item_arr, freshbooks_account_id, token):
        for item in item_arr:
             item_name = item.get('name')
             item_id = item.get('itemid')
             item_accounting_systemid = item.get('accounting_systemid')
             new_item = Product(name=item_name, freshbooks_item_id=item_id, freshbooks_account_id=item_accounting_systemid)
             new_item.save()

    def update_freshbooks_products(freshbooks_account_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        page = 1
        item_arr = []
        while(True):
            res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/items/items?page={1}".format(freshbooks_account_id, page)).json()
            max_pages = res.get('response')\
                            .get('result')\
                            .get('pages')

            curr_page = res.get('response')\
                            .get('result')\
                            .get('page')

            items = res.get('response')\
                            .get('result')\
                            .get('items')

            for item in items:
                item_arr.append(item)
            if curr_page == max_pages:
                break
            else:
                page += 1

        for item in item_arr:
            item_name = item.get('name')
            item_unit_price = item.get('unit_cost').get('amount')
            item_id = item.get('id')
            item_accounting_systemid = item.get('accounting_systemid')

            item_queryset = Product.objects.filter(freshbooks_item_id=item_id, freshbooks_account_id=item_accounting_systemid)
            if len(item_queryset) > 0:
                save_item = False
                update_item = item_queryset.get()
                if update_item.name != item_name:
                    update_item.name = item_name
                    save_item = True
                if update_item.unit_price != item_unit_price:
                    update_item.unit_price = item_unit_price
                    save_item = True
                if save_item:
                    update_item.save()
            else:
                new_item = Product(
                    name=item_name,
                    unit_price=item_unit_price,
                    freshbooks_item_id=item_id,
                    freshbooks_account_id=item_accounting_systemid
                )
                new_item.save()



class Invoice(models.Model):
    date_generated = models.DateField(auto_now=True)
    date_created = models.DateField(null=True)
    remark = models.CharField(max_length=255, null=True, blank=True)
    po_number = models.CharField(max_length=255, null=True, blank=True)
    discount_description = models.CharField(max_length=255, null=True, blank=True)
    discount_percentage = models.DecimalField(default=0.00, max_digits=7, decimal_places=4)
    minus = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    net_total = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    gst = models.DecimalField(default=0.00, max_digits=2, decimal_places=0)
    net_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    total_incl_gst = models.DecimalField(default=0.00, max_digits=9, decimal_places=4)
    invoice_number = models.TextField(null=False, blank=False, unique=True)
    customer = models.ForeignKey(Customer, null=False, on_delete=models.DO_NOTHING)
    pivot = models.BooleanField(default=False)
    freshbooks_account_id = models.TextField(null=True, blank=False)
    freshbooks_invoice_id = models.TextField(null=True, blank=False)

    class Meta:
        unique_together = ('invoice_number', 'customer')
        ordering = ['invoice_number']

    def freshbooks_invoice_detail(freshbooks_invoice_id, freshbooks_account_id, token):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks = OAuth2Session(client_id, token=token)
        res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/invoices/invoices/{1}?include[]=lines".format(freshbooks_account_id, freshbooks_invoice_id)).json()
        lines = res.get('response')\
                    .get('result')\
                    .get('invoice')\
                    .get('lines')
        return lines

    def handle_invoice_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            date_generated = row['date_generated']
            remark = row['remark']
            minus = row['minus']
            net_total = row['net_total']
            gst = row['gst']
            net_gst = row['net_gst']
            total_incl_gst = row['total_incl_gst']
            invoice_number = row['invoice_number']
            customer = row['customer']
            pivot = row['pivot']

            customer_obj = Customer.objects.filter(name=customer).first()
            if customer_obj:
                new_invoice = Invoice(
                    remark=remark,
                    minus=minus,
                    net_total=net_total,
                    gst=gst,
                    net_gst=net_gst,
                    total_incl_gst=total_incl_gst,
                    invoice_number=invoice_number,
                    customer=customer_obj,
                    pivot=pivot
                )
                new_invoice.save()
                new_invoice.date_generated=date_generated
                new_invoice.save()



class Route(models.Model):
    index = models.SmallIntegerField(null=True)
    do_number = models.CharField(max_length=128, null=False, blank=False)
    po_number = models.TextField(null=True, blank=False, max_length=255)
    note = models.TextField(null=True, blank=True, max_length=255)
    checked = models.BooleanField(default=False)
    date = models.DateField(default=date.today)
    do_image = models.FileField(null=True)

    # Route automatically defaults to order by index ascending in database model level
    class Meta:
        ordering = ['index']

    def handle_s3_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            do_number = row['do_number'].strip()
            key = row['key']

            #  to handle s3 import
            route_obj = Route.objects.filter(do_number=do_number).first()
            if route_obj:
                route_obj.do_image = key
                route_obj.save()


class CustomerProduct(models.Model):
    quote_price = models.DecimalField(
        default=0.00,
        max_digits=6,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    freshbooks_tax_1 = models.CharField(max_length=8, null=True)
    archived = models.BooleanField(default=False, null=False)
    sort_order = models.IntegerField(null=True)

    class Meta:
        unique_together = ('customer', 'product', 'quote_price')
        ordering = ['sort_order']


    def handle_quote_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            customer_name = row["customer"]
            product_name = row["product"]
            quote_price = row["quote_price"]
            freshbooks_tax_1 = row["freshbooks_tax_1"]
            customer_obj = Customer.objects.filter(name=customer_name).first()
            product_obj = Product.objects.filter(name=product_name).first()
            if customer_obj and product_obj:
                new_quote = CustomerProduct(
                    customer_id=customer_obj.pk,
                    product_id=product_obj.pk,
                    quote_price=quote_price,
                    freshbooks_tax_1=freshbooks_tax_1
                )
                new_quote.save()

class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField(default=0)
    driver_quantity = models.PositiveSmallIntegerField(default=0)
    note = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    customerproduct = models.ForeignKey(CustomerProduct, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    packing = JSONField(null=True, blank=True)
    invoice = models.ForeignKey(Invoice, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['route__date']


    def handle_orderitem_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            date = row["date"]
            customer_name = row["customer"]
            product_name = row["product"]
            quantity = row["quantity"]
            driver_quantity = row["driver_quantity"]
            unit_price = row["unit_price"]
            do_number = row["do_number"]
            invoice_number = row["invoice_number"]

            parsed_date = datetime.strptime(date, '%d/%m/%Y')
            formatted_date = parsed_date.strftime('%Y-%m-%d')
            customer_obj = Customer.objects.filter(name=customer_name).first()
            product_obj = Product.objects.filter(name=product_name).first()
            quote_obj = CustomerProduct.objects.filter(customer=customer_obj.pk, product=product_obj.pk).first()
            route_obj = Route.objects.filter(date=formatted_date, do_number=do_number).first()
            invoice_obj = Invoice.objects.filter(invoice_number=invoice_number).first()

            if quote_obj and route_obj:
                new_orderitem = OrderItem(
                    quantity=quantity,
                    driver_quantity=driver_quantity,
                    unit_price=unit_price,
                    customerproduct=quote_obj,
                    route=route_obj,
                    invoice=invoice_obj
                )
                new_orderitem.save()

            if quote_obj and route_obj is None:
                new_route = Route(do_number=do_number, date=formatted_date)
                new_route.save()
                new_orderitem = OrderItem(
                    quantity=quantity,
                    driver_quantity=driver_quantity,
                    unit_price=unit_price,
                    customerproduct=quote_obj,
                    route=new_route,
                    invoice=invoice_obj
                )
                new_orderitem.save()