from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from ..models import Customer, CustomerProduct, Product, OrderItem, Route, Invoice

# run test with python manage.py test pos.tests


class InvoiceTestCase(APITestCase):
    def setUp(self):
        customer = Customer.objects.create(name="Test Customer")
        product = Product.objects.create(name="Test Product")
        customerproduct = CustomerProduct.objects.create(
            customer=customer, product=product, quote_price=0.4
        )
        route = Route.objects.create(do_number='TEST-INV')
        orderitem = OrderItem.objects.create(
            customerproduct=customerproduct,
            route=route,
            quantity=40,
            driver_quantity=40,
            unit_price=0.4
        )
        orderitem2 = OrderItem.objects.create(
            customerproduct=customerproduct,
            route=route,
            quantity=40,
            driver_quantity=40,
            unit_price=0.41
        )

    def test_create_invoice_error_400_when_inconsistent_orderitem_unit_price(self):
        url = reverse('pos:invoice_create')
        customer = Customer.objects.get(name="Test Customer")
        orderitem_list = [oi.pk for oi in OrderItem.objects.all()]
        data = {
            'customer_id': customer.pk,
            'create_date': "2021-03-31",
            'orderitems_id': orderitem_list,
            'discount': 0
        }
        response = self.client.post(url, data, format='json')
        invoices_count = Invoice.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), 'Orderitems unit pricing is inconsistent')
        self.assertEqual(invoices_count, 0)

    def test_update_invoice_error_400_when_inconsistent_orderitem_unit_price(self):
        #  set up order items to invoice before updating with inconsistent unit price
        customer = Customer.objects.get(name="Test Customer")
        orderitem = OrderItem.objects.first()
        invoice = Invoice.objects.create(invoice_number="20210000", customer=customer)
        orderitem.invoice=invoice
        orderitem.save()
        orderitem_list = [oi.pk for oi in OrderItem.objects.all()]

        url = reverse('pos:invoice_update', args=[1])
        data = {
            'orderitems_id':orderitem_list,
            'discount': 0
        }
        response = self.client.put(url, data, format='json')
        invoice_orderitem_count = invoice.orderitem_set.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), 'Orderitems unit pricing is inconsistent')
        self.assertEqual(invoice_orderitem_count, 1)