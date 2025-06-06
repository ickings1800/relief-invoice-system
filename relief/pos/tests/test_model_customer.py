from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from ..models import Customer, CustomerProduct, Product, OrderItem, Route, Invoice

# run test with python manage.py test pos.tests


class InvoiceTestCase(APITestCase):
    def setUp(self):
        customer = Customer.objects.create(
            name="Test Customer",
            to_whatsapp=True,
            to_email=True,
            to_fax=True,
            to_print=True,
            download_prefix='',
            download_suffix='',
        )

    def test_download_invoice_file_name(self):
        invoice_number = 20211234
        customer = Customer.objects.get(name="Test Customer")
        file_name = customer.get_download_file_name(invoice_number)
        self.assertEqual(file_name, '20211234_whatsapp_email_fax_print')
