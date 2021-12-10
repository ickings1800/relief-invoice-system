from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from ..models import Customer, CustomerProduct, Product, OrderItem, Route, Invoice
from datetime import datetime

# run test with python manage.py test pos.tests


class OrderItemTestCase(APITestCase):
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
        product = Product.objects.create(name="Test Product")
        customerproduct = CustomerProduct.objects.create(
            customer=customer, product=product, quote_price=0.4
        )
        date_early = datetime.strptime('10/12/2021', '%d/%m/%Y')
        date_late = datetime.strptime('11/12/2021', '%d/%m/%Y')
        date_later = datetime.strptime('12/12/2021', '%d/%m/%Y')
        route_early = Route.objects.create(do_number='TEST-INV', date=date_early)
        route_late = Route.objects.create(do_number='TEST-INV2', date=date_late)
        route_later = Route.objects.create(do_number='TEST-INV3', date=date_later)
        orderitem = OrderItem.objects.create(
            customerproduct=customerproduct,
            route=route_early,
            quantity=40,
            driver_quantity=40,
            unit_price=0.4
        )
        orderitem3 = OrderItem.objects.create(
            customerproduct=customerproduct,
            route=route_later,
            quantity=40,
            driver_quantity=40,
            unit_price=0.4
        )
        orderitem2 = OrderItem.objects.create(
            customerproduct=customerproduct,
            route=route_late,
            quantity=40,
            driver_quantity=40,
            unit_price=0.4
        )


    def test_filter_orderitem_based_on_customer_pk_no_empty_string(self):
        url = reverse('pos:orderitems_filter')
        customer = Customer.objects.all().first()
        response = self.client.get(url, {'customer_ids': str(customer.pk) + ';'},HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_orderitem_ascending_by_date(self):
        url = reverse('pos:orderitems_filter')
        invoice_customer = Customer.objects.all().first()
        invoice = Invoice.objects.create(invoice_number="20210000", customer=invoice_customer)
        orderitems = OrderItem.objects.all()
        for oi in orderitems:
            oi.invoice=invoice
            oi.save()
        orderitems = OrderItem.objects.filter(customerproduct__customer__id=invoice_customer.pk, invoice_id=invoice.pk)
        print(orderitems.query)
        for oi in orderitems:
            print(oi.route.__dict__)
        self.assertEqual(orderitems.count(), 3)
        self.assertEqual(orderitems[0].route.date.strftime('%d/%m/%Y'), '10/12/2021')
        self.assertEqual(orderitems[1].route.date.strftime('%d/%m/%Y'), '11/12/2021')
        self.assertEqual(orderitems[2].route.date.strftime('%d/%m/%Y'), '12/12/2021')