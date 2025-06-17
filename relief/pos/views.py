from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, FileResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics, ttfonts
from datetime import datetime
from .models import Customer, Product, CustomerProduct, OrderItem, Invoice, Company
from .forms import ImportFileForm, ExportOrderItemForm, ExportInvoiceForm
from .freshbooks import freshbooks_access
from requests_oauthlib import OAuth2Session
from django_pivot.pivot import pivot
from collections import Counter
from decimal import Decimal, ROUND_UP
from django.conf import settings
import csv
import io
import requests
import uuid
import time


# Create your views here.
def redirect_to_freshbooks_auth(request):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(
        'https://auth.freshbooks.com/service/auth/oauth/authorize')
    request.session['oauth_state'] = state
    return HttpResponseRedirect(authorization_url)


def get_token(request):
    callback_url = request.get_full_path()
    client_id = settings.FRESHBOOKS_CLIENT_ID
    client_secret = settings.FRESHBOOKS_CLIENT_SECRET
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI

    freshbooks = OAuth2Session(
        client_id,
        token=request.session['oauth_state'], 
        redirect_uri=redirect_uri
    )

    freshbooks.headers.update({
        'User-Agent': 'FreshBooks API (python) 1.0.0',
        'Content-Type': 'application/json'
    })

    try:
        token = freshbooks.fetch_token(
            "https://api.freshbooks.com/auth/oauth/token",
            authorization_response=callback_url,
            client_secret=client_secret)
    except Exception as e:
        print(f"Error fetching token: {e}")
        return HttpResponseRedirect(reverse('pos:login'))
    
    current_unix_time = int(time.time())

    request.session['client_id'] = client_id
    request.session['oauth_token'] = token.get('access_token')
    request.session['refresh_token'] = token.get('refresh_token')
    request.session['unix_token_expires'] = current_unix_time + token.get('expires_in')

    print(f"get_token:: OAuth Token: {request.session['oauth_token']}")
    print(f"get_token:: Refresh Token: {request.session['refresh_token']}")
    print(f"get_token:: Expires In: {request.session['unix_token_expires']}")

    # Use the access token to authenticate the user with the OAuth service
    # to check for the user's freshbooks account id
    res = freshbooks.get("https://api.freshbooks.com/auth/api/v1/users/me").json()

    account_id = res.get('response')\
                    .get('business_memberships')[0]\
                    .get('business')\
                    .get('account_id')

    company = get_object_or_404(Company, freshbooks_account_id=account_id)

    # If the user has a freshbooks account id, find the user object and log them in
    if company is not None:
        login(request, company.user)
        request.session['freshbooks_account_id'] = account_id
        request.user.freshbooks_access_token = token.get('access_token')
        request.user.freshbooks_refresh_token = token.get('refresh_token')
        request.user.freshbooks_token_expires = current_unix_time + token.get('expires_in')
        request.user.save()
        return HttpResponseRedirect(reverse('pos:overview'))

    # Handle the case where the login failed, where user has logged in by freshbooks,
    # but does not have an account on the system.
    # TODO: (register a new user, company object)
    return HttpResponse(status=404)


@login_required
def overview(request):
    template_name = 'pos/customer/index.html'

    if request.method == 'GET':
        return render(request, template_name)


@login_required
def express_order(request):
    template_name = 'pos/route/express_order.html'
    if request.method == 'GET':
        return render(request, template_name)


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
        self.drawRightString(200*mm, 10*mm,
                             "Page %d of %d" % (self._pageNumber, page_count))


@login_required
def download_invoice(request, pk=None):
    invoice_number = request.GET.get('invoice_number', None)
    print(invoice_number)
    try:
        if pk:
            print('use pk')
            invoice = Invoice.objects.get(pk=pk)
        if invoice_number:
            print('use invoice number')
            invoice = Invoice.objects.filter(invoice_number=invoice_number).get()
    except ObjectDoesNotExist:
        #  invoice is not in the db
        print('not in db')
        return freshbooks_invoice_download(request, invoice_number=invoice_number)

    if invoice:
        #  invoice is in the db
        print('in db')
        invoice_name = invoice.customer.get_download_file_name(invoice.invoice_number)
        if invoice.pivot:
            print('pivot')
            return invoice_pdf_view(request, invoice.pk, file_name=invoice_name)
        else:
            print('freshbooks')
            return freshbooks_invoice_download(request, pk=invoice.pk, file_name=invoice_name)

    return HttpResponseBadRequest()


@login_required
def invoice_pdf_view(request, pk, file_name=''):
    invoice = Invoice.objects.select_related('customer').get(pk=pk)
    if invoice:
        invoice_customer = invoice.customer
        query_oi = OrderItem.objects.filter(
            customerproduct__customer__id=invoice_customer.pk, invoice_id=pk).order_by('route__date')
        unique_orderitem_names = set([oi.customerproduct.product.name for oi in query_oi])
        unique_quote_price_set = set(query_oi.values_list(
            'customerproduct__product__name', 'unit_price'))
        unique_quote_price_dict = {k: v for k, v in unique_quote_price_set}

        pv_table = pivot(
            query_oi,
            ['route__do_number', 'route__date'],
            'customerproduct__product__name', 'driver_quantity',
            default=0
        )

        product_sum = Counter()

        for row in pv_table:
            mapped_row = {name: row.get(name, 0) for name in unique_orderitem_names}
            product_sum.update(mapped_row)

        nett_amt = {name: unique_quote_price_dict[name] *
                    product_sum[name] for name in unique_orderitem_names}

        subtotal = 0
        for k, v in nett_amt.items():
            subtotal += v

        total_nett_amt = subtotal - invoice.minus
        gst_decimal = Decimal(invoice.gst / 100)
        gst = (total_nett_amt * gst_decimal).quantize(Decimal('.0001'), rounding=ROUND_UP)
        total_incl_gst = (total_nett_amt + gst).quantize(Decimal('.0001'), rounding=ROUND_UP)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{0}.pdf"'.format(file_name)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=1*cm,
                                leftMargin=1*cm, topMargin=5*mm, bottomMargin=5*mm)

        # container for the "Flowable" objects
        elements = []

        # Make heading for each column and start data list

        top_table_style = TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
            ]
        )
        taxStyle = getSampleStyleSheet()
        taxHeadingStyle = taxStyle["Normal"]
        taxHeadingStyle.fontName = 'Helvetica-Bold'
        taxHeadingStyle.fontSize = 14

        top_table_data = []
        top_table_data.append(["SUN-UP BEAN FOOD MFG PTE LTD",
                               Paragraph("TAX INVOICE", taxHeadingStyle)])
        top_table_data.append(["TUAS BAY WALK #02-30 SINGAPORE 637780",
                               "INVOICE NUMBER:", invoice.invoice_number])
        if invoice.date_created:
            top_table_data.append(["TEL: 68639035 FAX: 68633738", "DATE: ",
                                   invoice.date_created.strftime('%d/%m/%Y')])
        else:
            top_table_data.append(["TEL: 68639035 FAX: 68633738", "DATE: ", ""])
        top_table_data.append(["REG NO: 200302589N"])
        top_table_data.append(["BILL TO"])
        top_table_data.append([invoice_customer.name])

        if invoice_customer.address:
            top_table_data.append([invoice_customer.address])
        if invoice_customer.postal_code and invoice_customer.country:
            top_table_data.append([invoice_customer.country + ' ' + invoice_customer.postal_code])
        else:
            top_table_data.append([invoice_customer.country])

        top_table = Table(top_table_data, [12*cm, 4*cm, 3*cm])
        top_table.setStyle(top_table_style)

        # Assemble data for each column using simple loop to append it into data list

        styles = getSampleStyleSheet()
        styleBH = styles["Normal"]
        styleBH.alignment = TA_CENTER
        styleBH.fontName = 'Helvetica-Bold'

        product_style = TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
            data_row.append(row.get('route__date').strftime('%d/%m/%Y'))
            for name in unique_orderitem_names:
                if row.get(name) is None:
                    data_row.append('')
                else:
                    qty = row.get(name)
                    if qty == 0:
                        data_row.append('')
                    else:
                        data_row.append(str(row.get(name)))
            data_row.append(row.get('route__do_number', styleBH))
            datalist.append(data_row)
        table_width = (19/len(heading)) * cm
        product_table = Table(datalist, [table_width for i in range(len(heading))], 5.25*mm)
        product_table.hAlign = 'CENTER'
        product_table.setStyle(product_style)

        quantity_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                     ('FONTSIZE', (0, 0), (-1, -1), 9)])
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
        quantity_table = Table(quantity_data, [table_width for i in range(len(heading))], 5*mm)
        quantity_table.hAlign = 'CENTER'
        quantity_table.setStyle(quantity_style)

        # -- subtotal, gst, total amount --
        total_data_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9),
                                       ('SPAN', (0, 0), (0, 0)),
                                       ('SPAN', (0, 0), (0, -1)),
                                       ('GRID', (1, 0), (-1, -1), 0.5, colors.black),
                                       ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')])

        note_styles = getSampleStyleSheet()
        notes_style = note_styles["Normal"]
        notes_style.alignment = TA_LEFT
        notes_style.fontName = 'Helvetica-Bold'

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
        total_data_table = Table(total_data, [12.8*cm, 4*cm, 2*cm])
        total_data_table.hAlign = 'RIGHT'
        total_data_table.setStyle(total_data_style)

        elements.append(top_table)
        elements.append(Spacer(0, 5*mm))
        elements.append(product_table)
        elements.append(Spacer(0, 5*mm))
        elements.append(quantity_table)
        elements.append(Spacer(0, 5*mm))
        elements.append(total_data_table)

        doc.build(elements, canvasmaker=NumberedPageCanvas)

        response.write(buffer.getvalue())
        buffer.close()
        return response
    return HttpResponseBadRequest()


@login_required
@freshbooks_access
def freshbooks_invoice_download(request, freshbooks_svc, pk=None, invoice_number=None, file_name=''):
    if pk:
        invoice = Invoice.objects.get(pk=pk)
        invoice_number = invoice.invoice_number
    if invoice_number:
        #  find the invoice id from freshbooks
        freshbooks_account_id = request.session['freshbooks_account_id']
        freshbooks_invoice_search = freshbooks_svc.search_freshbooks_invoices(invoice_number)

        if len(freshbooks_invoice_search) == 0:
            return HttpResponseBadRequest()

        freshbooks_invoice_id = freshbooks_invoice_search[0].get('invoiceid')

        #  TODO: check if freshbooks customer id is in database for file name
        try:
            freshbooks_invoice_client_id = freshbooks_invoice_search[0].get('customerid')
            invoice_customer = Customer.objects.get(
                freshbooks_client_id=freshbooks_invoice_client_id)
            file_name = invoice_customer.get_download_file_name(invoice_number)
        except ObjectDoesNotExist:
            #  customer not registered in database
            #  different file name format for customers not registered in database
            file_name = str(invoice_number)
            freshbooks_first_name = freshbooks_invoice_search[0].get('fname', '')
            freshbooks_last_name = freshbooks_invoice_search[0].get('lname', '')
            freshbooks_organization = freshbooks_invoice_search[0].get('organization', '')
            if freshbooks_first_name:
                file_name += ('_' + freshbooks_first_name)
            if freshbooks_last_name:
                file_name += ('_' + freshbooks_last_name)
            if freshbooks_organization:
                file_name += ('_' + freshbooks_organization)
        except MultipleObjectsReturned:
            #  more than one customer with the same freshbooks client id
            return HttpResponseBadRequest()

        try:
            pdf = freshbooks_svc.download_freshbooks_invoice(freshbooks_invoice_id)
        except Exception:
            return HttpResponseBadRequest()

        response = FileResponse(pdf.raw, as_attachment=True, filename='{0}.pdf'.format(file_name))
        return response
    return HttpResponseBadRequest()


@login_required
def orderitem_summary(request):
    def get_invoice_number(orderitem):
        if orderitem.invoice:
            print(orderitem.invoice)
            return orderitem.invoice.invoice_number
        return ''

    if request.method == 'GET':
        field_names = [
            'date', 'customer', 'product', 'quantity',
            'driver_quantity', 'do_number', 'unit_price',
            'invoice_number'
        ]
        date_start_string = request.GET.get('start_date')
        date_end_string = request.GET.get('end_date')

        if date_start_string and date_end_string:
            date_start = datetime.strptime(date_start_string, "%Y-%m-%d")
            date_end = datetime.strptime(date_end_string, "%Y-%m-%d")
            orderitems = OrderItem.objects.select_related('route', 'invoice')\
                .filter(route__date__gte=date_start, route__date__lte=date_end)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="summary.csv"'

            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            for oi in orderitems:
                writer.writerow({
                    'date': oi.route.date.strftime('%d/%m/%Y'),
                    'customer': oi.customerproduct.customer.name,
                    'product': oi.customerproduct.product.name,
                    'quantity': oi.quantity,
                    'driver_quantity': oi.driver_quantity,
                    'do_number': oi.route.do_number,
                    'unit_price': oi.unit_price,
                    'invoice_number': get_invoice_number(oi)
                })
            return response
        else:
            return HttpResponseBadRequest()


@login_required
def export_invoice(request):
    if request.method == 'GET':
        field_names = [
            'date_generated', 'remark', 'minus', 'net_total',
            'gst', 'net_gst', 'total_incl_gst',
            'invoice_number', 'customer', 'pivot'
        ]
        date_start_string = request.GET.get('start_date')
        date_end_string = request.GET.get('end_date')

        if date_start_string and date_end_string:
            date_start = datetime.strptime(date_start_string, "%Y-%m-%d")
            date_end = datetime.strptime(date_end_string, "%Y-%m-%d")
            orderitems_with_invoices = OrderItem.objects.select_related(
                'route', 'invoice'
            )\
                .filter(
                route__date__gte=date_start,
                route__date__lte=date_end,
                invoice__invoice_number__isnull=False
            )
            invoice_ids = set(
                [orderitem.invoice.invoice_number for orderitem in orderitems_with_invoices])
            export_invoices = Invoice.objects.filter(invoice_number__in=invoice_ids)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="invoice_summary.csv"'

            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            for invoice in export_invoices:
                writer.writerow({
                    'date_generated': invoice.date_generated,
                    'remark': invoice.remark,
                    'minus': invoice.minus,
                    'net_total': invoice.net_total,
                    'gst': invoice.gst,
                    'net_gst': invoice.net_gst,
                    'total_incl_gst': invoice.total_incl_gst,
                    'invoice_number': invoice.invoice_number,
                    'customer': invoice.customer.name,
                    'pivot': invoice.pivot
                })
            return response
        else:
            return HttpResponseBadRequest()


@login_required
def export_quote(request):
    if request.method == 'GET':
        field_names = ['sku', 'customer', 'product', 'quote_price', 'freshbooks_tax_1']
        quotes = CustomerProduct.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="quotes.csv"'

        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()
        for cp in quotes:
            writer.writerow({
                'sku': cp.pk,
                'customer': cp.customer.name,
                'product': cp.product.name,
                'quote_price': cp.quote_price,
                'freshbooks_tax_1': cp.freshbooks_tax_1
            })
        return response
    else:
        return HttpResponseBadRequest()


@login_required
def import_items(request):
    template_name = 'pos/master/import_items.html'
    if request.method == 'POST':
        form = ImportFileForm(request.POST, request.FILES)
        if form.is_valid():
            import_customer_file = request.FILES.get('import_customer_file', None)
            import_product_file = request.FILES.get('import_product_file', None)
            import_quote_file = request.FILES.get('import_quote_file', None)
            import_orderitem_file = request.FILES.get('import_orderitem_file', None)
            import_detrack_file = request.FILES.get('import_detrack_file', None)
            import_invoice_file = request.FILES.get('import_invoice_file', None)

            if import_customer_file:
                with open('/tmp/customer_import.csv', 'wb+') as destination:
                    for chunk in import_customer_file.chunks():
                        destination.write(chunk)
                with open('/tmp/customer_import.csv') as csv_file:
                    Customer.handle_customer_import(csv_file)
            if import_product_file:
                with open('/tmp/product_import.csv', 'wb+') as destination:
                    for chunk in import_product_file.chunks():
                        destination.write(chunk)
                with open('/tmp/product_import.csv') as csv_file:
                    Product.handle_product_import(csv_file)
            if import_quote_file:
                with open('/tmp/quote_import.csv', 'wb+') as destination:
                    for chunk in import_quote_file.chunks():
                        destination.write(chunk)
                with open('/tmp/quote_import.csv') as csv_file:
                    CustomerProduct.handle_quote_import(csv_file)
            #  import invoice file
            if import_invoice_file:
                with open('/tmp/invoice_import.csv', 'wb+') as destination:
                    for chunk in import_invoice_file.chunks():
                        destination.write(chunk)
                with open('/tmp/invoice_import.csv') as csv_file:
                    Invoice.handle_invoice_import(csv_file)
            if import_orderitem_file:
                with open('/tmp/orderitem_import.csv', 'wb+') as destination:
                    for chunk in import_orderitem_file.chunks():
                        destination.write(chunk)
                with open('/tmp/orderitem_import.csv') as csv_file:
                    OrderItem.handle_orderitem_import(csv_file)
            if import_detrack_file:
                with open('/tmp/detrack_import.csv', 'wb+') as destination:
                    for chunk in import_detrack_file.chunks():
                        destination.write(chunk)
                with open('/tmp/detrack_import.csv') as csv_file:
                    OrderItem.handle_detrack_import(csv_file)
            return HttpResponseRedirect(reverse('pos:import_items'))
    else:
        form = ImportFileForm()
        export_form = ExportOrderItemForm()
        export_invoice = ExportInvoiceForm()
    return render(request, template_name, {'form': form, 'export_form': export_form, 'export_invoice': export_invoice})


def download_receipt(request, submission_id):
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': settings.DETRACK_API_KEY
    }
    read_order_url = f'https://app.detrack.com/api/v2/dn/jobs/show/?do_number={submission_id}'
    response = requests.get(read_order_url, headers=headers).json()
    data = response.get('data')
    delivery_date = datetime.strptime(data.get('date'), '%Y-%m-%d')
    fmt_delivery_date = delivery_date.strftime('%d/%m/%Y')
    do_number = data.get('do_number')
    customer_name = data.get('deliver_to_collect_from')
    orderitems = data.get('items')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(58*mm, 180*mm),
        rightMargin=3*mm,
        leftMargin=3*mm,
        topMargin=3*mm,
        bottomMargin=3*mm
    )

    style = getSampleStyleSheet()
    headingStyle = style["Normal"]
    headingStyle.fontName = 'Helvetica-Bold'
    headingStyle.alignment = TA_CENTER
    headingStyle.fontSize = 7

    detail = getSampleStyleSheet()
    detailStyle = detail["Normal"]
    detailStyle.fontName = 'Helvetica-Bold'
    detailStyle.alignment = TA_LEFT
    detailStyle.fontSize = 7

    detail_right = getSampleStyleSheet()
    detailRightStyle = detail_right["Normal"]
    detailRightStyle.fontName = 'Helvetica-Bold'
    detailRightStyle.alignment = TA_RIGHT
    detailRightStyle.fontSize = 7

    # container for the "Flowable" objects
    heading_data = [
        [Paragraph("Delivery Date:", detailStyle), Paragraph(fmt_delivery_date, detailRightStyle)],
        [Paragraph("Delivery Order No.:", detailStyle), Paragraph(do_number, detailRightStyle)],
        [Paragraph("Messrs: ", detailStyle), ],
        [Paragraph(customer_name, detailStyle), ],
    ]
    heading_table_style = TableStyle([
        #  ('GRID',(0,0),(-1,-1),0.5,colors.gray),
        #  ('LINEABOVE', (0,0), (2,0), 0.25, colors.black),
        #  ('LINEBELOW', (-2,-1), (-1,-1), 0.25, colors.black),
        ('SPAN', (0, 3), (1, 3)),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ])
    heading_table = Table(heading_data)
    heading_table.setStyle(heading_table_style)

    elements = [
        Paragraph("SUN-UP BEAN FOOD MFG PTE LTD", headingStyle),
        Paragraph("No. 10 Tuas Bay Walk #02-30", headingStyle),
        Paragraph("Singapore 637780", headingStyle),
        Paragraph("Tel: 6863 9035 Fax: 6863 3738", headingStyle),
        Paragraph("GST & Co. Reg. No.: 200302589N", headingStyle),
        heading_table,
    ]

    all_product_desc = [
        'Plate Tofu\n板豆腐 (盘)',
        'Press Tofu\n板豆腐 (白)',
        'Japanese Silken Packaging\n日本豆腐',
        'Deep Fried Packaging Tofu\n盒装煎炸 (青)',
        'Silken Tofu With Egg (Square)\n菜香豆腐 (方)',
        'Egg Tofu (Tube)\n蛋豆腐 (条)',
        'Pail Tofu\n豆腐 (桶)',
        'Tofu Without Packaging\n豆腐 (条)',
        'Bean Curd\n豆干',
        'Ready Fried Tofu (20 pcs)\n预备炸豆腐 (20 条)',
        'Ready Fried Tofu (3 pcs)\n预备炸豆腐 (3 条)',
        'Blank Japanese Silken Packaging\n无印日本',
        'Blank Press Tofu Packaging\n无印四方',
    ]

    num_expiry_dates = len([oi for oi in orderitems if oi.get('expiry_date') or oi.get('purchase_order_number')])
    non_empty_products = [oi.get('description') for oi in orderitems]
    empty_product_description = [d for d in all_product_desc if d not in non_empty_products]
    empty_products = [
        {
            'description': description,
            'actual_quantity': '',
            'exp_date': '',
            'purchase_order_number': '',
        }
        for description in empty_product_description
    ]

    product_table = build_product_table(orderitems)
    empty_product_table = build_product_table(empty_products)

    elements += product_table
    elements += empty_product_table
    extra_paper_height = num_expiry_dates * 5
    doc.pagesize = (58*mm, (180 + extra_paper_height) * mm)
    doc.build(elements)
    filename = str(uuid.uuid4())
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{0}.pdf"'.format(filename)
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    return response


def build_product_table(orderitems):
    body = getSampleStyleSheet()
    bodyStyle = body["Normal"]
    bodyStyle.alignment = TA_LEFT
    bodyStyle.fontSize = 7

    po = getSampleStyleSheet()
    poStyle = po["Normal"]
    poStyle.alignment = TA_RIGHT
    poStyle.fontSize = 7

    quantity = getSampleStyleSheet()
    quantityStyle = quantity["Normal"]
    quantityStyle.alignment = TA_RIGHT
    quantityStyle.fontSize = 10

    unit = getSampleStyleSheet()
    unitStyle = unit["Normal"]
    unitStyle.alignment = TA_RIGHT
    unitStyle.fontSize = 7

    pdfmetrics.registerFont(ttfonts.TTFont("ukai", "ukai.ttc"))

    cn = getSampleStyleSheet()
    cnStyle = cn["Normal"]
    cnStyle.alignment = TA_LEFT
    cnStyle.fontSize = 10
    cnStyle.fontName = 'ukai'

    product_table_list = []

    for oi in orderitems:
        name = oi.get('description').split('\n')
        #  quantity = oi.get('actual_quantity') or ""
        actual_quantity = str(oi.get('actual_quantity') or "")
        exp_date = oi.get('expiry_date') or ""
        po_number = oi.get('purchase_order_number') or ""

        eng_product_name = name[0]
        product_data = [
            [Paragraph(eng_product_name, bodyStyle), Paragraph(actual_quantity, quantityStyle)],
        ]

        if len(name) > 1:
            cn_product_name = name[1]
            product_data = [
                [Paragraph(cn_product_name, cnStyle), Paragraph(actual_quantity, quantityStyle)],
                [Paragraph(eng_product_name, bodyStyle), ],
            ]

        if exp_date or po_number:
            product_data.append([
                Paragraph(f"EXP DATE: {exp_date}", bodyStyle), Paragraph(po_number, poStyle)
            ])

        product_table = Table(product_data)
        product_table_style = TableStyle([
            #  ('GRID',(0,0),(-1,-1),0.5,colors.gray),
            ('SPAN', (0, 1), (-1, 1)),
            ('LINEABOVE', (0, 0), (2, 0), 0.25, colors.black),
            ('LINEBELOW', (-2, -1), (-1, -1), 0.25, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]
        )
        product_table.setStyle(product_table_style)
        product_table_list.append(product_table)

    return product_table_list