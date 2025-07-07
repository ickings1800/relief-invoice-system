import datetime
import io
import json
import time
import zipfile
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from huey.contrib.djhuey import db_task, task
from huey.exceptions import CancelExecution, TaskException
from pypdf import PdfReader
from pypdf.errors import PdfStreamError
from requests_oauthlib import OAuth2Session

from .services import FreshbooksService


def get_huey_freshbooks_service(user):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    token = user.freshbooks_access_token
    refresh_token = user.freshbooks_refresh_token
    expires_in = user.freshbooks_token_expires
    refresh_url = "https://api.freshbooks.com/auth/oauth/token"
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI
    current_unix_time = int(time.time())

    def token_updater(token):
        user.freshbooks_access_token = token.get("access_token")
        user.freshbooks_refresh_token = token.get("refresh_token")
        user.freshbooks_token_expires = int(time.time()) + token.get("expires_in")
        user.save()

    token = {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": expires_in - current_unix_time,
    }

    freshbooks = OAuth2Session(
        client_id,
        token=token,
        auto_refresh_url=refresh_url,
        token_updater=token_updater,
        redirect_uri=redirect_uri,
    )

    res = freshbooks.get("https://api.freshbooks.com/auth/api/v1/users/me").json()

    account_id = res.get("response").get("business_memberships")[0].get("business").get("account_id")

    freshbooks_svc = FreshbooksService(account_id, freshbooks)
    return freshbooks_svc


@db_task(context=True)
def huey_download_invoice_main_task(invoice_number_from, invoice_number_to, user, task=None):
    from .models import Invoice

    print("huey_download_invoice_main_task:: ", invoice_number_from, invoice_number_to)
    try:
        invoice_number_from = int(invoice_number_from)
        invoice_number_to = int(invoice_number_to)
    except ValueError:
        raise CancelExecution(retry=False)

    def valid_invoice_number(invoice_number_from, invoice_number_to):
        if invoice_number_from and invoice_number_to:
            if invoice_number_to > invoice_number_from:
                return True
        return False

    if not valid_invoice_number(invoice_number_from, invoice_number_to):
        raise CancelExecution(retry=False)

    freshbooks_svc = get_huey_freshbooks_service(user)

    #  key is huey task id, value is the filename
    huey_download_tasks = dict()
    huey_q = []

    invoice_in_database = None

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for invoice_number in range(invoice_number_from, invoice_number_to + 1):
            try:
                invoice_in_database = Invoice.objects.get(invoice_number=invoice_number)
            except Invoice.MultipleObjectsReturned:
                #  multiple invoices found (shouldn't happen), but let's just use the first one
                invoice_in_database = Invoice.objects.filter(invoice_number=invoice_number).first()
            except Invoice.DoesNotExist:
                invoice_in_database = None

            if not invoice_in_database:
                # if invoice is not in database, we need to download it from Freshbooks
                freshbooks_invoice_search = freshbooks_svc.search_freshbooks_invoices(invoice_number)

                if len(freshbooks_invoice_search) == 0:
                    continue

                freshbooks_invoice = freshbooks_invoice_search[0]
                freshbooks_invoice_id = freshbooks_invoice.get("id")
                huey_pdf_task = huey_download_freshbooks_invoice(freshbooks_invoice_id, user)
                huey_download_tasks[huey_pdf_task.id] = freshbooks_invoice.get("invoice_number", "download") + ".pdf"
                huey_q.append(huey_pdf_task)
                continue

            # if invoice is in database, we need to see if it is a pivot invoice or have to download from Freshbooks
            filename = invoice_in_database.customer.get_download_file_name(invoice_in_database.invoice_number) + ".pdf"

            if invoice_in_database.pivot:
                pivot_invoice_pdf_buffer = Invoice.download_pivot_invoice(invoice_in_database.pk, io.BytesIO())
                zip_file.writestr(filename, pivot_invoice_pdf_buffer.getvalue())
                pivot_invoice_pdf_buffer.close()
                continue
            else:
                freshbooks_invoice_search = freshbooks_svc.search_freshbooks_invoices(invoice_number)
                if len(freshbooks_invoice_search) == 0:
                    continue
                huey_pdf_task = huey_download_freshbooks_invoice(invoice_in_database.freshbooks_invoice_id, user)
                huey_download_tasks[huey_pdf_task.id] = filename
                huey_q.append(huey_pdf_task)

        #  after all huey tasks are created, we need to wait for them to finish
        #  TODO: Make this non-blocking
        for task_result in huey_q:
            try:
                pdf_content = task_result.get(blocking=True)
                zip_file.writestr(huey_download_tasks.get(task_result.id), pdf_content)
            except TaskException:
                continue
    return zip_buffer.getvalue()


@task(retries=10, retry_delay=10)
def huey_download_freshbooks_invoice(freshbooks_invoice_id, user):
    # Read the PDF content into a PdfReader object, will throw error if not valid PDF.
    # when error is thrown, huey will retry the task
    freshbooks_svc = get_huey_freshbooks_service(user)
    pdf = freshbooks_svc.download_freshbooks_invoice(freshbooks_invoice_id)
    try:
        PdfReader(io.BytesIO(pdf.content))
        return pdf.content
    except PdfStreamError as e:
        print(f"Failed to read PDF content for invoice {freshbooks_invoice_id}: {str(e)}")
        raise TaskException()


@db_task(context=True)
def huey_create_invoice(
    user,
    freshbooks_tax_lookup,
    invoice_orderitems,
    invoice_customer,
    parsed_create_date,
    invoice_number=None,
    po_number=None,
    minus_decimal=Decimal(0),
    minus_description=None,
    task=None,
):
    from .models import Invoice, OrderItem

    freshbooks_svc = get_huey_freshbooks_service(user)

    # . create the ask on huey, get the task id
    freshbooks_client_id = invoice_customer.freshbooks_client_id

    freshbooks_invoice_body = OrderItem.build_freshbooks_invoice_body(
        invoice_orderitems,
        freshbooks_client_id,
        invoice_number,
        po_number,
        parsed_create_date,
        freshbooks_tax_lookup,
    )

    print("huey_create_invoice:: ", json.dumps(freshbooks_invoice_body))

    invoice = freshbooks_svc.create_freshbooks_invoice(freshbooks_invoice_body)

    invoice_number = invoice.get("invoice_number")
    freshbooks_account_id = invoice.get("accounting_systemid")
    freshbooks_invoice_id = invoice.get("id")

    create_invoice_kwargs = {
        "invoice_number": invoice_number,
        "po_number": po_number,
        "minus_decimal": minus_decimal,
        "minus_description": minus_description,
        "huey_task_id": task.id if task else None,
    }

    new_invoice = Invoice.create_local_invoice(
        invoice_orderitems,
        invoice_customer,
        parsed_create_date,
        freshbooks_account_id,
        freshbooks_invoice_id,
        **create_invoice_kwargs,
    )

    return new_invoice


# docker time is in UTC time
# @db_periodic_task(crontab(hour="17"))
@task()
def huey_create_invoice_automation(group_name):
    from .models import CustomerGroup, OrderItem

    User = get_user_model()
    user = User.objects.get(pk=1)  #  Temporarily hardcode with user id 1
    freshbooks_svc = get_huey_freshbooks_service(user)
    freshbooks_tax_lookup = freshbooks_svc.get_freshbooks_taxes()
    customergroup_arr = CustomerGroup.objects.filter(group__name=group_name).order_by("index")
    parsed_create_date = datetime.datetime.now().date()

    for cg in customergroup_arr:
        #  get all customers in the default group
        #  and create invoices for them
        customer = cg.customer
        customer_orderitems = OrderItem.get_available_orderitems_for_customer(customer)

        if len(customer_orderitems) == 0:
            print(f"No order items found for customer {customer.name} in group {group_name}.")
            continue

        print("")
        print("User:: ", user)
        print("Freshbooks Tax Lookup:: ", freshbooks_tax_lookup)
        print("Customer Order Items:: ", customer_orderitems)
        print("Creating invoice for customer:", customer.name)
        print("Parsed Create Date:: ", parsed_create_date)
        print("")

        if settings.DEBUG:
            print("Debug mode: Skipping invoice creation.")
            continue

        # huey_create_invoice(
        #     user=user,
        #     freshbooks_tax_lookup=freshbooks_tax_lookup,
        #     invoice_orderitems=customer_orderitems,
        #     invoice_customer=customer,
        #     parsed_create_date=parsed_create_date,
        # )


@db_task(retries=5, retry_delay=10, context=True)
def huey_update_freshbooks_invoice(user, existing_invoice, freshbooks_update_invoice_body, task=None):
    freshbooks_svc = get_huey_freshbooks_service(user)
    #  update invoice
    print(json.dumps(freshbooks_update_invoice_body))

    freshbooks_updated_invoice = freshbooks_svc.update_freshbooks_invoice(
        existing_invoice.freshbooks_invoice_id, freshbooks_update_invoice_body
    )

    invoice_number = freshbooks_updated_invoice.get("invoice_number")
    date_created = freshbooks_updated_invoice.get("create_date")
    freshbooks_account_id = freshbooks_updated_invoice.get("accounting_systemid")
    freshbooks_invoice_id = freshbooks_updated_invoice.get("id")

    existing_invoice.freshbooks_invoice_id = freshbooks_invoice_id
    existing_invoice.freshbooks_account_id = freshbooks_account_id
    existing_invoice.invoice_number = invoice_number
    existing_invoice.date_created = date_created
    existing_invoice.huey_task_id = None
    existing_invoice.save(
        update_fields=[
            "freshbooks_invoice_id",
            "freshbooks_account_id",
            "invoice_number",
            "date_created",
            "huey_task_id",
        ]
    )
