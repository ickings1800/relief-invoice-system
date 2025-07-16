# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
from collections import Counter
from datetime import date, datetime
from decimal import ROUND_UP, Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField
from django_pivot.pivot import pivot
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .managers import CompanyAwareManager
from .tasks import huey_create_invoice

# Create your models here.


class CompanyAwareModel(models.Model):
    #  Separate manager allowing bypassing company check
    objects_all_companies = models.Manager()
    #  override the default manager to always require a specific company filter
    objects = CompanyAwareManager()

    class Meta:
        abstract = True


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    tel_no = models.CharField(max_length=8, null=True, blank=True)
    business_no = models.CharField(max_length=10, null=True, blank=True)
    fax_no = models.CharField(max_length=8, null=True, blank=True)
    freshbooks_account_id = models.CharField(max_length=255, null=False, blank=False)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)


class Group(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name

    def group_create(name):
        group_exists = Group.objects.filter(name=name)
        if len(group_exists) > 0:
            raise Exception("Group with the name of '{}' already exists.".format(name))
        new_group = Group.objects.create(name=name)
        return new_group


class Customer(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=False)
    postal_code = models.CharField(max_length=255, null=True, blank=False)
    country = models.CharField(max_length=128, null=True, blank=False)
    gst = models.DecimalField(default=9, max_digits=1, decimal_places=0)
    currency = models.CharField(max_length=3, null=True, blank=False)
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
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_download_file_name(self, invoice_number):
        invoice_name = ""

        if self.download_prefix:
            invoice_name += self.download_prefix + "_"

        invoice_name += str(invoice_number)

        if self.download_suffix:
            invoice_name += "_" + self.download_suffix
        if self.to_whatsapp:
            invoice_name += "_whatsapp"
        if self.to_email:
            invoice_name += "_email"
        if self.to_fax:
            invoice_name += "_fax"
        if self.to_print:
            invoice_name += "_print"

        return invoice_name

    def handle_customer_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        default_group = Group.objects.filter(name="Default").first()
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

    def import_freshbooks_clients(import_clients):
        default_group = Group.objects.filter(name="Default").first()
        if not default_group:
            new_group = Group(name="Default")
            new_group.save()
            default_group = new_group

        for client in import_clients:
            if client.get("organization", ""):
                client_name = client.get("organization", "")
            else:
                client_name = client.get("fname", "") + client.get("lname", "")
            client_address = client.get("p_street")
            client_postal_code = client.get("p_code")
            client_country = client.get("p_country")
            client_id = client.get("id")
            client_accounting_systemid = client.get("accounting_systemid")
            client_currency = client.get("currency_code", "USD")
            new_client = Customer(
                name=client_name,
                address=client_address,
                postal_code=client_postal_code,
                country=client_country,
                currency=client_currency,
                freshbooks_client_id=client_id,
                freshbooks_account_id=client_accounting_systemid,
            )
            new_client.save()
            customer_group = CustomerGroup(group=default_group, customer=new_client)
            customer_group.save()


class CustomerGroup(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
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
                print("empty the group")
                CustomerGroup.objects.filter(group=group).delete()
        updated_grouping = Customer.objects.filter(id__in=client_id_list)
        return updated_grouping


class Product(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=128)
    unit_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    freshbooks_item_id = models.CharField(max_length=12, null=True, blank=False)
    freshbooks_account_id = models.CharField(max_length=12, null=True, blank=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def handle_product_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row_product = Product(name=row["name"])
            row_product.save()

    def freshbooks_import_products(item_arr):
        for item in item_arr:
            item_name = item.get("name")
            item_id = item.get("itemid")
            item_accounting_systemid = item.get("accounting_systemid")
            new_item = Product(
                name=item_name,
                freshbooks_item_id=item_id,
                freshbooks_account_id=item_accounting_systemid,
            )
            new_item.save()


class Invoice(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
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
    invoice_number = models.TextField(null=True, blank=False, unique=False)
    customer = models.ForeignKey(Customer, null=False, on_delete=models.DO_NOTHING)
    pivot = models.BooleanField(default=False)
    freshbooks_account_id = models.TextField(null=True, blank=False)
    freshbooks_invoice_id = models.TextField(null=True, blank=False)
    huey_task_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ("invoice_number", "customer")
        ordering = ["invoice_number"]

    def create_local_invoice(
        invoice_orderitems,
        invoice_customer,
        parsed_create_date,
        freshbooks_account_id,
        freshbooks_invoice_id,
        invoice_number=None,
        po_number=None,
        minus_decimal=Decimal(0),
        minus_description=None,
        huey_task_id=None,
    ):
        net_total = 0
        for orderitem in invoice_orderitems:
            net_total += orderitem.driver_quantity * orderitem.unit_price

        gst_decimal = Decimal(invoice_customer.gst / 100)
        net_total -= minus_decimal
        net_gst = (net_total * gst_decimal).quantize(Decimal(".0001"), rounding=ROUND_UP)
        total_incl_gst = (net_total + net_gst).quantize(Decimal(".0001"), rounding=ROUND_UP)

        new_invoice = Invoice(
            date_created=parsed_create_date,
            po_number=po_number,
            net_total=net_total,
            gst=invoice_customer.gst,
            net_gst=net_gst,
            minus=minus_decimal,
            discount_description=minus_description,
            total_incl_gst=total_incl_gst,
            invoice_number=invoice_number,
            customer=invoice_customer,
            pivot=invoice_customer.pivot_invoice,
            freshbooks_account_id=freshbooks_account_id,
            freshbooks_invoice_id=freshbooks_invoice_id,
            huey_task_id=huey_task_id,
        )
        new_invoice.save()

        for orderitem in invoice_orderitems:
            orderitem.invoice = new_invoice
            orderitem.save()

        return new_invoice

    def create_invoice(
        user,
        freshbooks_tax_lookup,
        invoice_orderitems,
        invoice_customer,
        parsed_create_date,
        invoice_number=None,
        po_number=None,
        minus_decimal=Decimal(0),
        minus_description=None,
    ):
        create_invoice_kwargs = {
            "invoice_number": invoice_number,
            "po_number": po_number,
            "minus_decimal": minus_decimal,
            "minus_description": minus_description,
        }
        create_invoice_task = huey_create_invoice(
            user,
            freshbooks_tax_lookup,
            invoice_orderitems,
            invoice_customer,
            parsed_create_date,
            **create_invoice_kwargs,
        )
        return create_invoice_task

    def handle_invoice_import(csv_file):
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            date_generated = row["date_generated"]
            remark = row["remark"]
            minus = row["minus"]
            net_total = row["net_total"]
            gst = row["gst"]
            net_gst = row["net_gst"]
            total_incl_gst = row["total_incl_gst"]
            invoice_number = row["invoice_number"]
            customer = row["customer"]
            pivot = row["pivot"]

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
                    pivot=pivot,
                )
                new_invoice.save()
                new_invoice.date_generated = date_generated
                new_invoice.save()

    def download_pivot_invoice(invoice_pk, buffer):
        class NumberedPageCanvas(canvas.Canvas):
            """
            http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
            http://code.activestate.com/recipes/576832/
            http://www.blog.pythonlibrary.org/2013/08/12/reportlab-how-to-add-page-numbers/
            """

            def __init__(self, *args, **kwargs):
                """Constructor"""
                super().__init__(*args, **kwargs)
                self.pages = []

            def showPage(self):
                """
                On a page break, add information to the list
                """
                self.pages.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                """
                Add the page number to each page (page x of y)
                """
                page_count = len(self.pages)

                for page in self.pages:
                    self.__dict__.update(page)
                    self.draw_page_number(page_count)
                    super().showPage()
                canvas.Canvas.save(self)

            def draw_page_number(self, page_count):
                self.setFont("Helvetica-Bold", 8)
                self.drawRightString(200 * mm, 10 * mm, "Page %d of %d" % (self._pageNumber, page_count))

        try:
            invoice = Invoice.objects.select_related("customer").get(pk=invoice_pk)
        except Invoice.DoesNotExist:
            return None

        invoice_customer = invoice.customer
        query_oi = OrderItem.objects.filter(
            customerproduct__customer__id=invoice_customer.pk, invoice_id=invoice_pk
        ).order_by("route__date")
        unique_orderitem_names = set([oi.customerproduct.product.name for oi in query_oi])
        unique_quote_price_set = set(query_oi.values_list("customerproduct__product__name", "unit_price"))
        unique_quote_price_dict = {k: v for k, v in unique_quote_price_set}

        pv_table = pivot(
            query_oi,
            ["route__do_number", "route__date"],
            "customerproduct__product__name",
            "driver_quantity",
            default=0,
        )

        product_sum = Counter()

        for row in pv_table:
            mapped_row = {name: row.get(name, 0) for name in unique_orderitem_names}
            product_sum.update(mapped_row)

        nett_amt = {name: unique_quote_price_dict[name] * product_sum[name] for name in unique_orderitem_names}

        subtotal = 0
        for k, v in nett_amt.items():
            subtotal += v

        total_nett_amt = subtotal - invoice.minus
        gst_decimal = Decimal(invoice.gst / 100)
        gst = (total_nett_amt * gst_decimal).quantize(Decimal(".0001"), rounding=ROUND_UP)
        total_incl_gst = (total_nett_amt + gst).quantize(Decimal(".0001"), rounding=ROUND_UP)

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=5 * mm,
            bottomMargin=5 * mm,
        )

        # container for the "Flowable" objects
        elements = []

        # Make heading for each column and start data list

        top_table_style = TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ]
        )
        taxStyle = getSampleStyleSheet()
        taxHeadingStyle = taxStyle["Normal"]
        taxHeadingStyle.fontName = "Helvetica-Bold"
        taxHeadingStyle.fontSize = 14

        top_table_data = []
        top_table_data.append(["SUN-UP BEAN FOOD MFG PTE LTD", Paragraph("TAX INVOICE", taxHeadingStyle)])
        top_table_data.append(
            [
                "TUAS BAY WALK #02-30 SINGAPORE 637780",
                "INVOICE NUMBER:",
                invoice.invoice_number,
            ]
        )
        if invoice.date_created:
            top_table_data.append(
                [
                    "TEL: 68639035 FAX: 68633738",
                    "DATE: ",
                    invoice.date_created.strftime("%d/%m/%Y"),
                ]
            )
        else:
            top_table_data.append(["TEL: 68639035 FAX: 68633738", "DATE: ", ""])
        top_table_data.append(["REG NO: 200302589N"])
        top_table_data.append(["BILL TO"])
        top_table_data.append([invoice_customer.name])

        if invoice_customer.address:
            top_table_data.append([invoice_customer.address])
        if invoice_customer.postal_code and invoice_customer.country:
            top_table_data.append([invoice_customer.country + " " + invoice_customer.postal_code])
        else:
            top_table_data.append([invoice_customer.country])

        top_table = Table(top_table_data, [12 * cm, 4 * cm, 3 * cm])
        top_table.setStyle(top_table_style)

        # Assemble data for each column using simple loop to append it into data list

        styles = getSampleStyleSheet()
        styleBH = styles["Normal"]
        styleBH.alignment = TA_CENTER
        styleBH.fontName = "Helvetica-Bold"

        product_style = TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
        heading = []
        heading.append(Paragraph("DATE", styleBH))
        for name in unique_orderitem_names:
            heading.append(Paragraph(name, styleBH))
        heading.append(Paragraph("D/O", styleBH))
        datalist = [heading]

        for row in pv_table:
            data_row = []
            data_row.append(row.get("route__date").strftime("%d/%m/%Y"))
            for name in unique_orderitem_names:
                if row.get(name) is None:
                    data_row.append("")
                else:
                    qty = row.get(name)
                    if qty == 0:
                        data_row.append("")
                    else:
                        data_row.append(str(row.get(name)))
            data_row.append(row.get("route__do_number", styleBH))
            datalist.append(data_row)
        table_width = (19 / len(heading)) * cm
        product_table = Table(datalist, [table_width for i in range(len(heading))], 5.25 * mm)
        product_table.hAlign = "CENTER"
        product_table.setStyle(product_style)

        quantity_style = TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTSIZE", (0, 0), (-1, -1), 9)])
        quantity_data = []
        #   -- quantity row --
        quantity_row = []
        quantity_row.append(Paragraph("QUANTITY", styleBH))
        for name in unique_orderitem_names:
            quantity_row.append(Paragraph(str(product_sum.get(name, 0)), styleBH))
        quantity_row.append("")
        quantity_data.append(quantity_row)
        #  -- unit price row --
        unit_price_row = []
        unit_price_row.append(Paragraph("UNIT PRICE", styleBH))
        for name in unique_orderitem_names:
            unit_price_row.append(Paragraph(str(unique_quote_price_dict.get(name)), styleBH))
        unit_price_row.append("")
        quantity_data.append(unit_price_row)
        #  -- nett amount row --
        nett_amt_row = []
        nett_amt_row.append(Paragraph("NETT AMOUNT", styleBH))
        for name in unique_orderitem_names:
            nett_amt_row.append(Paragraph(str(nett_amt.get(name)), styleBH))
        nett_amt_row.append("")
        quantity_data.append(nett_amt_row)
        quantity_table = Table(quantity_data, [table_width for i in range(len(heading))], 5 * mm)
        quantity_table.hAlign = "CENTER"
        quantity_table.setStyle(quantity_style)

        # -- subtotal, gst, total amount --
        total_data_style = TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("SPAN", (0, 0), (0, 0)),
                ("SPAN", (0, 0), (0, -1)),
                ("GRID", (1, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ]
        )

        note_styles = getSampleStyleSheet()
        notes_style = note_styles["Normal"]
        notes_style.alignment = TA_LEFT
        notes_style.fontName = "Helvetica-Bold"

        total_data = []
        if invoice.remark:
            notes_paragraph = Paragraph(invoice.remark, notes_style)
        else:
            notes_paragraph = Paragraph("", notes_style)

        total_data.append([notes_paragraph, "SUB-TOTAL ($)", str(subtotal)])

        if invoice.minus > 0:
            if invoice.discount_description:
                total_data.append(["", invoice.discount_description, str(invoice.minus)])
            else:
                total_data.append(["", "MINUS ($)", str(invoice.minus)])
            total_data.append(["", "TOTAL NETT AMT ($)", str(total_nett_amt)])

        total_data.append(["", "GST ({0}%)".format(invoice.gst), str(gst)])
        total_data.append(["", "TOTAL (inc. GST) ($)", str(total_incl_gst)])
        total_data_table = Table(total_data, [12.8 * cm, 4 * cm, 2 * cm])
        total_data_table.hAlign = "RIGHT"
        total_data_table.setStyle(total_data_style)

        elements.append(top_table)
        elements.append(Spacer(0, 5 * mm))
        elements.append(product_table)
        elements.append(Spacer(0, 5 * mm))
        elements.append(quantity_table)
        elements.append(Spacer(0, 5 * mm))
        elements.append(total_data_table)

        doc.build(elements, canvasmaker=NumberedPageCanvas)
        return buffer


class Route(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    index = models.SmallIntegerField(null=True)
    do_number = models.CharField(max_length=128, null=False, blank=False)
    po_number = models.TextField(null=True, blank=False, max_length=255)
    note = models.TextField(null=True, blank=True, max_length=255)
    checked = models.BooleanField(default=False)
    date = models.DateField(default=date.today)

    # Route automatically defaults to order by index ascending in database model level
    class Meta:
        ordering = ["index"]


class CustomerProduct(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    quote_price = models.DecimalField(
        default=0.00,
        max_digits=6,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    freshbooks_tax_1 = models.CharField(max_length=8, null=True)
    archived = models.BooleanField(default=False, null=False)
    sort_order = models.IntegerField(null=True)

    class Meta:
        unique_together = ("customer", "product", "quote_price")
        ordering = ["sort_order"]

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
                    freshbooks_tax_1=freshbooks_tax_1,
                )
                new_quote.save()


class OrderItem(CompanyAwareModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    quantity = models.PositiveSmallIntegerField(default=0)
    driver_quantity = models.PositiveSmallIntegerField(default=0)
    note = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.DecimalField(default=0.00, max_digits=6, decimal_places=4)
    customerproduct = models.ForeignKey(CustomerProduct, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    packing = JSONField(null=True, blank=True)
    invoice = models.ForeignKey(Invoice, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["route__date"]

    def get_available_orderitems_for_customer(customer):
        """
        Returns all order items for a customer that are not yet invoiced.
        """
        return OrderItem.objects.filter(customerproduct__customer=customer, invoice=None)

    def check_orderitem_consistent_pricing(invoice_orderitems):
        price_map = {}
        for oi in invoice_orderitems:
            product_name = oi.customerproduct.product.name
            if not price_map.get(product_name):
                price_map[product_name] = oi.unit_price
            if price_map[product_name] != oi.unit_price:
                return False
        return True

    def build_freshbooks_invoice_body(
        invoice_orderitems,
        freshbooks_client_id,
        invoice_number,
        po_number,
        parsed_create_date,
        freshbooks_tax_lookup_dict,
    ):
        invoice_lines = []
        for orderitem in invoice_orderitems:
            orderitem_date_str = datetime.strftime(orderitem.route.date, "%d-%m-%Y")
            description = f"DATE: {orderitem_date_str} D/O: {orderitem.route.do_number}"

            if orderitem.note:
                description += " P/O: {0}".format(orderitem.note)

            invoice_line = {
                "type": 0,
                "description": description,
                "name": orderitem.customerproduct.product.name,
                "qty": orderitem.driver_quantity,
                "unit_cost": {"amount": str(orderitem.unit_price), "code": orderitem.customerproduct.customer.currency},
            }

            try:
                tax_id = int(orderitem.customerproduct.freshbooks_tax_1)
                orderitem_tax = freshbooks_tax_lookup_dict.get(tax_id, None) if tax_id else None
                if orderitem_tax:
                    invoice_line["taxName1"] = orderitem_tax.get("name", None)
                    invoice_line["taxAmount1"] = orderitem_tax.get("amount", None)
            except (ValueError, TypeError):
                pass

            print("invoice_lines", invoice_lines)
            invoice_lines.append(invoice_line)

        body = {
            "invoice": {
                "customerid": freshbooks_client_id,
                "invoice_number": invoice_number,
                "po_number": po_number,
                "create_date": datetime.strftime(parsed_create_date, "%Y-%m-%d"),
                "lines": [line for line in invoice_lines],
            }
        }

        return body

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

            parsed_date = datetime.strptime(date, "%d/%m/%Y")
            formatted_date = parsed_date.strftime("%Y-%m-%d")
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
                    invoice=invoice_obj,
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
                    invoice=invoice_obj,
                )
                new_orderitem.save()

    def handle_detrack_import(csv_file):
        csv_reader = csv.DictReader(csv_file, delimiter=",")

        #  save csv into memory
        for row in csv_reader:
            date = row["Date"]
            sku = row["SKU"]
            orderitem_qty = row["Actual Quantity"]
            do_number = row["D.O. No."]
            name = row["Deliver to"]
            po_number_start = name.index("(") if "(" in name else None
            po_number_end = name.index(")") if ")" in name else None
            po_number = ""

            if not sku:
                continue

            if int(orderitem_qty) <= 0:
                continue

            if po_number_start and po_number_end:
                po_number = name[po_number_start : po_number_end + 1]

            parsed_date = datetime.strptime(date, "%d/%m/%Y")
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            quote_obj = CustomerProduct.objects.filter(pk=sku).first()
            route_obj = Route.objects.filter(date=formatted_date, do_number=do_number).first()

            if quote_obj and route_obj:
                new_orderitem = OrderItem(
                    note=po_number,
                    quantity=orderitem_qty,
                    driver_quantity=orderitem_qty,
                    unit_price=quote_obj.quote_price,
                    customerproduct=quote_obj,
                    route=route_obj,
                )
                new_orderitem.save()

            if quote_obj and route_obj is None:
                new_route = Route(do_number=do_number, date=formatted_date)
                new_route.save()
                new_orderitem = OrderItem(
                    note=po_number,
                    quantity=orderitem_qty,
                    driver_quantity=orderitem_qty,
                    unit_price=quote_obj.quote_price,
                    customerproduct=quote_obj,
                    route=new_route,
                )
                new_orderitem.save()
