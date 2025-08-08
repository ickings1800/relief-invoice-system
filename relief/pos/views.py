import csv
import io
import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from requests_oauthlib import OAuth2Session
from users.models import User

from .forms import CompanySelectForm, ExportInvoiceForm, ExportOrderItemForm, ImportFileForm
from .freshbooks import freshbooks_access
from .managers import get_company_from_request
from .models import Company, Customer, CustomerProduct, Invoice, OrderItem, Product

client_id = settings.FRESHBOOKS_CLIENT_ID
client_secret = settings.FRESHBOOKS_CLIENT_SECRET
redirect_uri = settings.FRESHBOOKS_REDIRECT_URI


# Create your views here.
def redirect_to_freshbooks_auth(request):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url("https://auth.freshbooks.com/service/auth/oauth/authorize")
    request.session["oauth_state"] = state
    return HttpResponseRedirect(authorization_url)


def get_token(request):
    callback_url = request.get_full_path()

    freshbooks = OAuth2Session(client_id, token=request.session["oauth_state"], redirect_uri=redirect_uri)

    freshbooks.headers.update(
        {
            "User-Agent": "FreshBooks API (python) 1.0.0",
            "Content-Type": "application/json",
        }
    )

    try:
        token = freshbooks.fetch_token(
            "https://api.freshbooks.com/auth/oauth/token",
            authorization_response=callback_url,
            client_secret=client_secret,
        )
    except Exception as e:
        print(f"Error fetching token: {e}")
        return HttpResponseRedirect(reverse("pos:login"))

    current_unix_time = int(time.time())

    request.session["client_id"] = client_id
    request.session["oauth_token"] = token.get("access_token")
    request.session["refresh_token"] = token.get("refresh_token")
    request.session["unix_token_expires"] = current_unix_time + token.get("expires_in")

    print(f"get_token:: OAuth Token: {request.session['oauth_token']}")
    print(f"get_token:: Refresh Token: {request.session['refresh_token']}")
    print(f"get_token:: Expires In: {request.session['unix_token_expires']}")

    return HttpResponseRedirect(reverse("pos:select_company"))


def select_company(request):
    template_name = "pos/login.html"
    refresh_url = "https://api.freshbooks.com/auth/oauth/token"
    current_unix_time = int(time.time())

    def token_updater(token):
        request.session["oauth_token"] = token.get("access_token")
        request.session["refresh_token"] = token.get("refresh_token")
        request.session["unix_token_expires"] = current_unix_time + token.get("expires_in")

    token = {
        "access_token": request.session.get("oauth_token"),
        "refresh_token": request.session.get("refresh_token"),
        "token_type": "Bearer",
        "expires_in": request.session.get("unix_token_expires"),
    }

    freshbooks = OAuth2Session(
        client_id,
        token=token,
        auto_refresh_url=refresh_url,
        token_updater=token_updater,
        redirect_uri=redirect_uri,
    )
    # Use the access token to authenticate the user with the OAuth service
    # to check for the user's freshbooks account id
    res = freshbooks.get("https://api.freshbooks.com/auth/api/v1/users/me").json()

    if request.method == "GET":
        business_memberships = res.get("response").get("business_memberships")
        business_memberships_dict = {
            bm.get("business").get("account_id"): bm.get("business").get("name") for bm in business_memberships
        }
        select_company_form = CompanySelectForm(companies=business_memberships_dict)
        return render(request, template_name, {"select_company_form": select_company_form})

    # We need to allow user to select which business account to use
    if request.method == "POST":
        business_memberships = res.get("response").get("business_memberships")
        business_memberships_dict = {
            bm.get("business").get("account_id"): bm.get("business").get("name") for bm in business_memberships
        }
        print("POST request::", request.POST)
        select_company_form = CompanySelectForm(request.POST, companies=business_memberships_dict)

        if not select_company_form.is_valid():
            return render(request, template_name, {"select_company_form": select_company_form})

        try:
            account_id = select_company_form.cleaned_data.get("company")
            company = Company.objects.get(freshbooks_account_id=account_id)
        except Company.DoesNotExist:
            create_company_name = business_memberships_dict.get(account_id)
            company = Company(name=create_company_name, freshbooks_account_id=account_id)
            company.save()
        except Company.MultipleObjectsReturned:
            return HttpResponseBadRequest("Multiple companies found with the same account ID.")

        try:
            freshbooks_user_email = res.get("response").get("email")
            search_freshbooks_user = User.objects.get(email=freshbooks_user_email, companies=company)
            print("search_freshbooks_user:: ", search_freshbooks_user)
        except User.DoesNotExist:
            # Handle the case where the login failed, where user has logged in by freshbooks,
            # but does not have an account on the system.
            print("User does not exist, creating a new user.")
            new_user = User(email=freshbooks_user_email, username=freshbooks_user_email)
            new_user.set_unusable_password()  # Set an unusable password since we use OAuth
            new_user.save()
            new_user.refresh_from_db()
            new_user.companies.add(company)
            new_user.save()
            search_freshbooks_user = new_user
        except User.MultipleObjectsReturned:
            return HttpResponseBadRequest("Multiple users found with the same email address.")

        login(request, search_freshbooks_user)
        print("token:: ", token)
        request.session["freshbooks_account_id"] = account_id
        request.user.freshbooks_access_token = token.get("access_token")
        request.user.freshbooks_refresh_token = token.get("refresh_token")
        request.user.freshbooks_token_expires = current_unix_time + token.get("expires_in")
        request.user.save()
        return HttpResponseRedirect(reverse("pos:overview"))

    return HttpResponseBadRequest("Invalid request method.")


@login_required
def overview(request):
    template_name = "pos/customer/index.html"

    if request.method == "GET":
        return render(request, template_name)


@login_required
def express_order(request):
    template_name = "pos/route/express_order.html"
    if request.method == "GET":
        return render(request, template_name)


@login_required
@freshbooks_access
def download_invoice(request, freshbooks_svc):
    if request.method == "GET":
        pk = request.GET.get("pk", None)
        if not pk:
            return HttpResponseBadRequest("No invoice id provided.")
        try:
            company = Company.objects.get(freshbooks_account_id=request.session["freshbooks_account_id"])
            invoice = Invoice.objects.filter(company=company, pk=pk).first()
        except Company.DoesNotExist:
            return HttpResponseBadRequest("Company not found.")
        except Invoice.DoesNotExist:
            return HttpResponseBadRequest("Invoice not found.")

        filename = invoice.customer.get_download_file_name(invoice.invoice_number)
        if invoice.pivot:
            invoice_pivot_pdf_io = io.BytesIO()
            Invoice.download_pivot_invoice(invoice.company, invoice.pk, invoice_pivot_pdf_io)
            invoice_pivot_pdf_io.seek(0)
            return FileResponse(invoice_pivot_pdf_io, as_attachment=True, filename=f"{filename}.pdf")
        try:
            invoice_freshbooks_pdf = freshbooks_svc.download_freshbooks_invoice(invoice.freshbooks_invoice_id)
            return FileResponse(
                io.BytesIO(invoice_freshbooks_pdf.content),
                as_attachment=True,
                filename=f"{filename}.pdf",
                content_type="application/pdf",
            )
        except Exception:
            return HttpResponseBadRequest("Failed to download invoice from FreshBooks.")
    return HttpResponseBadRequest("Invalid request method.")


@login_required
def download_invoice_zip(request, huey_task_id):
    if request.method == "GET":
        filename = request.GET.get("filename", "download")
        huey_db = settings.HUEY
        if not huey_db.get(huey_task_id, peek=True):
            return HttpResponseBadRequest("Download task is still in progress.")
        zip_buffer = io.BytesIO(huey_db.get(huey_task_id, peek=False))
        return FileResponse(zip_buffer, as_attachment=True, filename=f"{filename}.zip", content_type="application/zip")
    return HttpResponseBadRequest("Invalid request method.")


@login_required
def orderitem_summary(request):
    def get_invoice_number(orderitem):
        if orderitem.invoice:
            print(orderitem.invoice)
            return orderitem.invoice.invoice_number
        return ""

    if request.method == "GET":
        field_names = [
            "date",
            "customer",
            "product",
            "quantity",
            "driver_quantity",
            "do_number",
            "unit_price",
            "invoice_number",
        ]
        date_start_string = request.GET.get("start_date")
        date_end_string = request.GET.get("end_date")

        if date_start_string and date_end_string:
            company = get_company_from_request(request)
            if not company:
                return HttpResponseBadRequest("Company not found")
            date_start = datetime.strptime(date_start_string, "%Y-%m-%d")
            date_end = datetime.strptime(date_end_string, "%Y-%m-%d")
            orderitems = (
                OrderItem.objects.filter(company=company)
                .select_related("route", "invoice")
                .filter(route__date__gte=date_start, route__date__lte=date_end)
            )

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="summary.csv"'

            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            for oi in orderitems:
                writer.writerow(
                    {
                        "date": oi.route.date.strftime("%d/%m/%Y"),
                        "customer": oi.customerproduct.customer.name,
                        "product": oi.customerproduct.product.name,
                        "quantity": oi.quantity,
                        "driver_quantity": oi.driver_quantity,
                        "do_number": oi.route.do_number,
                        "unit_price": oi.unit_price,
                        "invoice_number": get_invoice_number(oi),
                    }
                )
            return response
        else:
            return HttpResponseBadRequest()


@login_required
def export_invoice(request):
    if request.method == "GET":
        field_names = [
            "date_generated",
            "remark",
            "minus",
            "net_total",
            "gst",
            "net_gst",
            "total_incl_gst",
            "invoice_number",
            "customer",
            "pivot",
        ]
        date_start_string = request.GET.get("start_date")
        date_end_string = request.GET.get("end_date")

        if date_start_string and date_end_string:
            company = get_company_from_request(request)
            if not company:
                return HttpResponseBadRequest("Company not found")
            date_start = datetime.strptime(date_start_string, "%Y-%m-%d")
            date_end = datetime.strptime(date_end_string, "%Y-%m-%d")
            orderitems_with_invoices = (
                OrderItem.objects.filter(company=company)
                .select_related("route", "invoice")
                .filter(
                    route__date__gte=date_start,
                    route__date__lte=date_end,
                    invoice__invoice_number__isnull=False,
                )
            )
            invoice_ids = set([orderitem.invoice.invoice_number for orderitem in orderitems_with_invoices])
            export_invoices = Invoice.objects.filter(company=company, invoice_number__in=invoice_ids)
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="invoice_summary.csv"'

            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            for invoice in export_invoices:
                writer.writerow(
                    {
                        "date_generated": invoice.date_generated,
                        "remark": invoice.remark,
                        "minus": invoice.minus,
                        "net_total": invoice.net_total,
                        "gst": invoice.gst,
                        "net_gst": invoice.net_gst,
                        "total_incl_gst": invoice.total_incl_gst,
                        "invoice_number": invoice.invoice_number,
                        "customer": invoice.customer.name,
                        "pivot": invoice.pivot,
                    }
                )
            return response
        else:
            return HttpResponseBadRequest()


@login_required
def export_quote(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return HttpResponseBadRequest("Company not found")
        field_names = ["sku", "customer", "product", "quote_price", "freshbooks_tax_1"]
        quotes = CustomerProduct.objects.filter(company=company)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="quotes.csv"'

        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()
        for cp in quotes:
            writer.writerow(
                {
                    "sku": cp.pk,
                    "customer": cp.customer.name,
                    "product": cp.product.name,
                    "quote_price": cp.quote_price,
                    "freshbooks_tax_1": cp.freshbooks_tax_1,
                }
            )
        return response
    else:
        return HttpResponseBadRequest()


@login_required
def import_items(request):
    template_name = "pos/master/import_items.html"
    if request.method == "POST":
        form = ImportFileForm(request.POST, request.FILES)
        company = get_company_from_request(request)
        if not company:
            return HttpResponseBadRequest("Company not found")
        if form.is_valid():
            import_customer_file = request.FILES.get("import_customer_file", None)
            import_product_file = request.FILES.get("import_product_file", None)
            import_quote_file = request.FILES.get("import_quote_file", None)
            import_orderitem_file = request.FILES.get("import_orderitem_file", None)
            import_detrack_file = request.FILES.get("import_detrack_file", None)
            import_invoice_file = request.FILES.get("import_invoice_file", None)

            if import_customer_file:
                with open("/tmp/customer_import.csv", "wb+") as destination:
                    for chunk in import_customer_file.chunks():
                        destination.write(chunk)
                with open("/tmp/customer_import.csv") as csv_file:
                    Customer.handle_customer_import(company, csv_file)
            if import_product_file:
                with open("/tmp/product_import.csv", "wb+") as destination:
                    for chunk in import_product_file.chunks():
                        destination.write(chunk)
                with open("/tmp/product_import.csv") as csv_file:
                    Product.handle_product_import(company, csv_file)
            if import_quote_file:
                with open("/tmp/quote_import.csv", "wb+") as destination:
                    for chunk in import_quote_file.chunks():
                        destination.write(chunk)
                with open("/tmp/quote_import.csv") as csv_file:
                    CustomerProduct.handle_quote_import(company, csv_file)
            #  import invoice file
            if import_invoice_file:
                with open("/tmp/invoice_import.csv", "wb+") as destination:
                    for chunk in import_invoice_file.chunks():
                        destination.write(chunk)
                with open("/tmp/invoice_import.csv") as csv_file:
                    Invoice.handle_invoice_import(company, csv_file)
            if import_orderitem_file:
                with open("/tmp/orderitem_import.csv", "wb+") as destination:
                    for chunk in import_orderitem_file.chunks():
                        destination.write(chunk)
                with open("/tmp/orderitem_import.csv") as csv_file:
                    OrderItem.handle_orderitem_import(company, csv_file)
            if import_detrack_file:
                with open("/tmp/detrack_import.csv", "wb+") as destination:
                    for chunk in import_detrack_file.chunks():
                        destination.write(chunk)
                with open("/tmp/detrack_import.csv") as csv_file:
                    OrderItem.handle_detrack_import(company, csv_file)
            return HttpResponseRedirect(reverse("pos:import_items"))
    else:
        form = ImportFileForm()
        export_form = ExportOrderItemForm()
        export_invoice = ExportInvoiceForm()
    return render(
        request,
        template_name,
        {"form": form, "export_form": export_form, "export_invoice": export_invoice},
    )
