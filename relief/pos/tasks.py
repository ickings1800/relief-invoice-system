from requests_oauthlib import OAuth2Session
from huey import crontab
from huey.contrib.djhuey import periodic_task, task, db_task
from .services import FreshbooksService
from django.conf import settings
from decimal import Decimal
from pos.models import *
import time
import json


def get_huey_freshbooks_service(user):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    token = user.freshbooks_access_token
    refresh_token = user.freshbooks_refresh_token
    expires_in = user.freshbooks_token_expires
    refresh_url = "https://api.freshbooks.com/auth/oauth/token"
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI
    current_unix_time = int(time.time())

    extra = {
        "grant_type": "refresh_token",
    }

    def token_updater(token):
        user.freshbooks_access_token = token.get('access_token')
        user.freshbooks_refresh_token = token.get('refresh_token')
        user.freshbooks_token_expires = int(time.time()) + token.get('expires_in')
        user.save()

    token = {
        'access_token': token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': expires_in - current_unix_time
    }

    extra = {
        "grant_type": "refresh_token",
    }

    freshbooks = OAuth2Session(
        client_id,
        token=token,
        auto_refresh_url=refresh_url,
        auto_refresh_kwargs=extra,
        token_updater=token_updater,
        redirect_uri=redirect_uri
    )

    res = freshbooks.get("https://api.freshbooks.com/auth/api/v1/users/me").json()

    account_id = res.get('response')\
                    .get('business_memberships')[0]\
                    .get('business')\
                    .get('account_id')

    freshbooks_svc = FreshbooksService(account_id, freshbooks)
    return freshbooks_svc


@task(retries=10, retry_delay=10)
def huey_download_freshbooks_invoice(freshbooks_invoice_id, user):
    freshbooks_svc = get_huey_freshbooks_service(user)
    pdf = freshbooks_svc.download_freshbooks_invoice(freshbooks_invoice_id)
    return pdf.content


@db_task(retries=10, retry_delay=10, context=True)
def huey_create_invoice(user, freshbooks_tax_lookup, invoice_orderitems,
        invoice_customer, parsed_create_date, invoice_number=None, po_number=None, minus_decimal=Decimal(0),
         minus_description=None, task=None):

    freshbooks_svc = get_huey_freshbooks_service(user)

    #. create the ask on huey, get the task id
    freshbooks_client_id = invoice_customer.freshbooks_client_id

    freshbooks_invoice_body = OrderItem.build_freshbooks_invoice_body(
        invoice_orderitems, freshbooks_client_id, 
        invoice_number, po_number, parsed_create_date, freshbooks_tax_lookup
    )

    print(json.dumps(freshbooks_invoice_body))

    invoice = freshbooks_svc.create_freshbooks_invoice(freshbooks_invoice_body)

    invoice_number = invoice.get('invoice_number')
    freshbooks_account_id = invoice.get('accounting_systemid')
    freshbooks_invoice_id = invoice.get('id')

    create_invoice_kwargs = {
        'invoice_number': invoice_number,
        'po_number': po_number,
        'minus_decimal': minus_decimal,
        'minus_description': minus_description,
        'huey_task_id': task.id if task else None
    }

    new_invoice = Invoice.create_local_invoice(
        invoice_orderitems, invoice_customer, parsed_create_date,
        freshbooks_account_id, freshbooks_invoice_id, **create_invoice_kwargs
    )

    return new_invoice


@db_task(retries=10, retry_delay=10, context=True)
def huey_update_freshbooks_invoice(user, existing_invoice, freshbooks_update_invoice_body, task=None):
    freshbooks_svc = get_huey_freshbooks_service(user)
    #  update invoice
    print(json.dumps(freshbooks_update_invoice_body))

    freshbooks_updated_invoice = freshbooks_svc.update_freshbooks_invoice(
        existing_invoice.freshbooks_invoice_id, freshbooks_update_invoice_body
    )

    invoice_number = freshbooks_updated_invoice.get('invoice_number')
    date_created = freshbooks_updated_invoice.get('create_date')
    freshbooks_account_id = freshbooks_updated_invoice.get('accounting_systemid')
    freshbooks_invoice_id = freshbooks_updated_invoice.get('id')

    existing_invoice.freshbooks_invoice_id = freshbooks_invoice_id
    existing_invoice.freshbooks_account_id = freshbooks_account_id
    existing_invoice.invoice_number = invoice_number
    existing_invoice.date_created = date_created
    existing_invoice.huey_task_id = None
    existing_invoice.save(update_fields=[
        'freshbooks_invoice_id',
        'freshbooks_account_id',
        'invoice_number',
        'date_created',
        'huey_task_id'
    ])
    
@periodic_task(crontab(minute='*/5'))
def every_five_mins():
    print('Every five minutes this will be printed by the consumer')