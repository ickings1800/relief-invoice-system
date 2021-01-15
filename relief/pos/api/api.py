from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .serializers import TripAddRouteSerializer, \
    TripListDetailUpdateSerializer, CustomerListDetailUpdateSerializer, ProductListDetailUpdateSerializer, \
    CustomerCreateSerializer, ProductCreateSerializer, TripCreateSerializer, CustomerProductListDetailSerializer,\
    CustomerProductCreateSerializer, CustomerProductUpdateSerializer, RouteListSerializer, InvoiceListSerializer,\
    TripDetailSerializer, OrderItemUpdateSerializer, RouteUpdateSerializer, RouteDetailSerializer, RouteSerializer,\
    InvoiceDetailSerializer, GroupListSerializer, GroupCreateSerializer, OrderItemSerializer

from ..models import Trip, Route, Customer, CustomerProduct, OrderItem, Product, Invoice, CustomerGroup, Group
from datetime import datetime, timedelta, date
from django.db.models import Prefetch
from django.conf import settings
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from decimal import Decimal, ROUND_UP
import requests
import json

refresh_url = "https://api.freshbooks.com/auth/oauth/token"
client_id = settings.FRESHBOOKS_CLIENT_ID
client_secret = settings.FRESHBOOKS_CLIENT_SECRET

extra = {
    'client_id': client_id,
    'client_secret': client_secret,
}

def token_updater(request, token):
    request.session['oauth_token'] = token

class GroupList(ListAPIView):
    serializer_class = GroupListSerializer
    queryset = Group.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CustomerList(ListAPIView):
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.prefetch_related('customergroup_set', 'customergroup_set__group')
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)


class ProductList(ListAPIView):
    def get(self, request, *args, **kwargs):
        customer_id = request.GET.get('customer_id')
        if customer_id:
            products_existing = CustomerProduct.objects.filter(customer_id=customer_id).distinct('product_id')
            products_existing_ids = [cp.product_id for cp in products_existing]
            products = Product.objects.exclude(id__in=products_existing_ids)
        else:
            products = Product.objects.all()
        product_serializer = ProductListDetailUpdateSerializer(products, many=True)
        return Response(status=status.HTTP_200_OK, data=product_serializer.data)

@api_view(['GET'])
def product_detail(request, pk):
    if (request.method == 'GET'):
        product = Product.objects.get(pk=pk)
        if (product):
            token = request.session['oauth_token']
            try:
                product_detail = Product.freshbooks_product_detail(product.freshbooks_item_id, product.freshbooks_account_id, token)
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)

            return Response(status=status.HTTP_200_OK, data=product_detail)
    return Response(status=status.HTTP_400_BAD_REQUEST)

class TripList(ListAPIView):
    def get(self, request, *args, **kwargs):
        date_start_string = self.request.query_params.get('date_start')
        date_end_string = self.request.query_params.get('date_end')
        if date_start_string and date_end_string:
            date_start = datetime.strptime(date_start_string, '%Y-%m-%d')
            date_end = datetime.strptime(date_end_string, '%Y-%m-%d')
            date_end += timedelta(hours=23, minutes=59, seconds=59)
            date_end_formatted = datetime.strftime(date_end, '%Y-%m-%d %H:%M:%S')
            date_start_formatted = datetime.strftime(date_start, '%Y-%m-%d %H:%M:%S')
            trips = Trip.get_trips_by_date(date_start_formatted, date_end_formatted)
        else:
            trips = Trip.objects.all().order_by('-date')
        trip_serializer = TripListDetailUpdateSerializer(trips, many=True, context={'request': request})
        return Response(status=status.HTTP_200_OK, data=trip_serializer.data)


class TripDetail(RetrieveAPIView):
    serializer_class = TripDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return Trip.objects.prefetch_related(Prefetch('route_set', queryset=Route.objects.all().order_by('index')))


class TripCreate(CreateAPIView):
    serializer_class = TripCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TripDuplicate(CreateAPIView):
    serializer_class = TripCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            trip_id = self.kwargs['pk']
            print(trip_id)
            duplicated_trip = Trip.duplicate_trip(trip_id)
            tcs = TripCreateSerializer(duplicated_trip)
            return Response(status=status.HTTP_201_CREATED, data=tcs.data)
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TripUpdate(UpdateAPIView):
    serializer_class = TripListDetailUpdateSerializer
    queryset = Trip.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TripRouteCreate(CreateAPIView):
    serializer_class = TripAddRouteSerializer

    def post(self, request, *args, **kwargs):
        try:
            trip = Trip.objects.get(pk=self.kwargs['pk'])
            print("Try")
        except Trip.DoesNotExist:
            print("Does Not Exist")
            return Response(status=status.HTTP_404_NOT_FOUND)
        validated_note = request.data.get('note')
        validated_customer = request.data.get('customer')
        validated_do_number = request.data.get('do_number')
        print(validated_note, validated_customer)
        route = Trip.create_route(trip.pk, validated_note, customer_id=validated_customer, do_number=validated_do_number)
        rs = RouteSerializer(route)
        return Response(status=status.HTTP_201_CREATED, data=rs.data)


class TripRouteList(ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            routes = Route.objects.filter(trip_id=self.kwargs['pk'])
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        route_serializer = RouteSerializer(instance=routes, many=True)
        return Response(status=status.HTTP_200_OK, data=route_serializer.data)


class OrderItemDetail(RetrieveAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OrderItemUpdate(UpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemUpdateSerializer

    def put(self, request, *args, **kwargs):
        print(request.data)
        return self.update(request, *args, **kwargs)


class TripDelete(DestroyAPIView):
    queryset = Trip.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RouteDetail(RetrieveAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class RouteUpdate(UpdateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteUpdateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


@api_view(['POST'])
def route_arrange(request, pk):
    if request.method == 'POST':
        trip_id = pk
        arrangement = request.data.get('id_arrangement')
        try:
            Trip.arrange_route_index(trip_id, arrangement)
        except APIException as e:
            print(e.detail)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK, data=request.data)


@api_view(['PUT'])
def update_grouping(request):
    if request.method == 'PUT':
        group_id = request.data.get('group_id', None)
        arrangement = request.data.get('arrangement', None)
        if group_id and isinstance(arrangement, list):
            customers = CustomerGroup.update_grouping(group_id, arrangement)
            customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
            return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)


@api_view(['POST'])
def group_create(request):
    if request.method == 'POST':
        try:
            group_create_serializer = GroupCreateSerializer(data=request.data)
            if group_create_serializer.is_valid():
                new_group = group_create_serializer.save()
                print(type(new_group))
                group_list_serializer = GroupListSerializer(new_group)
                return Response(status=status.HTTP_201_CREATED, data=group_list_serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)
        except Exception as group_name_exists:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(group_name_exists)})



class RouteDelete(DestroyAPIView):
    queryset = Route.objects.all()

    def delete(self, request, *args, **kwargs):
        route_instance = self.get_object()
        trip_id = route_instance.trip.pk
        response = self.destroy(request, *args, **kwargs)
        Trip.rearrange_trip_routes_after_delete(trip_id)
        return response


class CustomerProductList(ListAPIView):
    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs['pk']
        customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)
        customerproduct_serializer = CustomerProductListDetailSerializer(customerproducts, many=True)
        return Response(status=status.HTTP_200_OK, data=customerproduct_serializer.data)


class CustomerProductDetail(RetrieveAPIView):
    queryset = CustomerProduct.objects.all()
    serializer_class = CustomerProductListDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CustomerProductCreate(CreateAPIView):
    serializer_class = CustomerProductCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomerProductUpdate(UpdateAPIView):
    queryset = CustomerProduct.objects.all()
    serializer_class = CustomerProductUpdateSerializer

    def put(self, request, *args, **kwargs):
        def get_freshbooks_tax(freshbooks_tax_id):
            token = request.session['oauth_token']
            freshbooks_account_id = request.session['freshbooks_account_id']
            try:
                freshbooks = OAuth2Session(client_id, token=token)
                res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes/{1}"
                    .format(freshbooks_account_id, freshbooks_tax_id)).json()
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)

            tax = res.get('response').get('result').get('tax')
            return tax

        freshbooks_tax_id = request.data.get('freshbooks_tax_1', None)
        quote_price = request.data.get('quote_price', None)
        if freshbooks_tax_id:
            get_valid_tax = get_freshbooks_tax(freshbooks_tax_id)
            if not get_valid_tax.get('taxid'):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.update(request, *args, **kwargs)


class CustomerRouteList(ListAPIView):
    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs['pk']
        # date_start_string = self.request.query_params.get('start_date')
        # date_end_string = self.request.query_params.get('end_date')
        # if date_start_string is not None and date_end_string is not None:
        #     date_start = datetime.strptime(date_start_string, '%Y-%m-%d %H:%M:%S')
        #     date_end = datetime.strptime(date_end_string, '%Y-%m-%d %H:%M:%S')
            #  date_start will start from exactly midnight by default
            #  date_end will have to add timedelta because it will also end at exactly at midnight,
            #  causing the last route order to not be included.
        #     date_end += timedelta(hours=23, minutes=59, seconds=59)
        #     date_end_formatted = datetime.strftime(date_end, '%Y-%m-%d %H:%M:%S')
        #     date_start_formatted = datetime.strftime(date_start, '%Y-%m-%d %H:%M:%S')
        #     routes = Route.get_customer_routes_orderitems_by_date(date_start_formatted, date_end_formatted, customer_id)
        #     route_serializer = RouteSerializer(routes, many=True)
        # else:
        get_checked_routes = request.GET.get("checked")
        # only accept "true" from querystring
        if get_checked_routes == "true":
            routes = Route.get_customer_routes_for_invoice(customer_id)
        else:
            routes = Route.get_customer_detail_routes(customer_id)
        route_serializer = RouteListSerializer(routes, many=True, context={'request': request})
        return Response(status=status.HTTP_200_OK, data=route_serializer.data)


class CustomerInvoiceList(ListAPIView):
    def get(self, request, *args, **kwargs):
        invoices = Invoice.get_customer_invoices(self.kwargs['pk'])
        invoice_serializer = InvoiceListSerializer(invoices, many=True)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)


class InvoiceDetail(RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class InvoiceList(ListAPIView):
    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.select_related('customer').all()
        invoice_serializer = InvoiceListSerializer(
            invoices, many=True, context={'request': request}
        )
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)


class InvoiceDateRange(ListAPIView):
    def get(self, request, *args, **kwargs):
        print(self.request.__str__)
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        date_start_string = request.GET.get('date_start', '')
        date_end_string = request.GET.get('date_end', '')

        try:
            if date_start_string and date_end_string:
                date_start = datetime.strptime(date_start_string, "%Y-%m-%d")
                date_end = datetime.strptime(date_end_string, "%Y-%m-%d")
                #  date_start will start from exactly midnight by default
                #  date_end will have to add timedelta because it will also end at exactly at midnight,
                #  causing the last route order to not be included.
                date_end += timedelta(hours=23, minutes=59, seconds=59)
                date_end_formatted = datetime.strftime(date_end, '%Y-%m-%d %H:%M:%S')
                date_start_formatted = datetime.strftime(date_start, '%Y-%m-%d %H:%M:%S')

                route_list = Route.get_customer_routes_orderitems_by_date(date_start_formatted,
                                                                          date_end_formatted,
                                                                          customer.id)
                print(route_list)
                rs = RouteListSerializer(route_list, many=True, context={'request': request})
                return Response(status=status.HTTP_200_OK, data=rs.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def unlink_invoice(request, pk):
    if request.method == 'PUT':
        unlink_invoice = Invoice.objects.prefetch_related(
            'orderitem_set'
        ).get(pk=pk)
        if unlink_invoice:
            unlink_orderitems = unlink_invoice.orderitem_set.all()
            for oi in unlink_orderitems:
                oi.invoice = None
                oi.save()
            unlink_invoice.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        else:
            return Response(status.HTTP_404_NOT_FOUND)
    return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def hard_delete_invoice(request, pk):
    if request.method == 'DELETE':
        delete_invoice = Invoice.objects.prefetch_related(
            'orderitem_set', 'orderitem_set__route'
        ).get(pk=pk)
        delete_route_ids = []
        delete_orderitems = []
        if delete_invoice:
            delete_orderitems = delete_invoice.orderitem_set.all()
            for oi in delete_orderitems:
                delete_route_ids.append(oi.route.pk)
                oi.delete()
            for route_id in set(delete_route_ids):
                delete_route = Route.objects.get(pk=route_id)
                if delete_route.orderitem_set.count() == 0:
                    delete_route.delete()
            delete_invoice.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        else:
            return Response(status.HTTP_404_NOT_FOUND)
    return Response(status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def create_invoice(request):
    if request.method == 'POST':
        customer_id = request.data.get('customer_id')
        create_date = request.data.get('create_date')
        orderitems_id = request.data.get('orderitems_id')
        invoice_number = request.data.get('invoice_number')
        po_number = request.data.get('po_number')
        discount = request.data.get('discount', 0) #  in percentage
        discount_description = request.data.get('discount_description', None)

        print(customer_id, create_date, orderitems_id, invoice_number, po_number, discount, discount_description)

        try:
            invoice_customer = Customer.objects.get(pk=customer_id)
            invoice_orderitems = OrderItem.objects.filter(pk__in=orderitems_id)
            parsed_create_date = datetime.strptime(create_date, "%Y-%m-%d")
            invoice_discount_percentage = Decimal(discount)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)

        client_id = settings.FRESHBOOKS_CLIENT_ID
        token = request.session['oauth_token']
        freshbooks_account_id = request.session['freshbooks_account_id']
        freshbooks = OAuth2Session(client_id, token=token)
        invoice_create_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices'.format(freshbooks_account_id)
        headers = {'Api-Version': 'alpha', 'Content-Type': 'application/json'}

        print(invoice_customer, invoice_orderitems, parsed_create_date)

        freshbooks_client_id = invoice_customer.freshbooks_client_id

        if len(invoice_orderitems) > 0:
            invoice_lines = []
            routes_id_list = [orderitem.route.pk for orderitem in invoice_orderitems]

            for orderitem in invoice_orderitems:
                tax_id = orderitem.customerproduct.freshbooks_tax_1
                if tax_id:
                    try:
                        res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes/{1}".format(freshbooks_account_id, tax_id)).json()
                    except TokenExpiredError as e:
                        token = freshbooks.refresh_token(refresh_url, **extra)
                        token_updater(request, token)

                    tax = res.get('response').get('result').get('tax')
                    #  get freshbooks tax
                    invoice_line =  {
                      "type": 0,
                      "description": "DATE: {0} D/O: {1}".format(
                          datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                          orderitem.route.do_number
                      ),
                      "taxName1": tax.get('name'),
                      "taxAmount1": tax.get('amount'),
                      "name": orderitem.customerproduct.product.name,
                      "qty": orderitem.driver_quantity,
                      "unit_cost": { "amount": str(orderitem.unit_price) }
                    }

                    invoice_lines.append(invoice_line)
                else:
                    invoice_line =  {
                      "type": 0,
                      "description": "DATE: {0} D/O: {1}".format(
                          datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                          orderitem.route.do_number
                      ),
                      "name": orderitem.customerproduct.product.name,
                      "qty": orderitem.driver_quantity,
                      "unit_cost": { "amount": str(orderitem.unit_price) }
                    }
                    invoice_lines.append(invoice_line)

            net_total = 0
            for orderitem in invoice_orderitems:
                net_total += (orderitem.driver_quantity * orderitem.unit_price)

            body = {
                "invoice": {
                  "customerid": freshbooks_client_id,
                  "invoice_number": invoice_number,
                  "po_number": po_number,
                  "create_date": datetime.strftime(parsed_create_date, '%Y-%m-%d'),
                  "discount_value": discount,
                  "discount_description": discount_description,
                  "lines": [line for line in invoice_lines]
                }
            }
            #  create invoice
            print(json.dumps(body))
            response = freshbooks.post(invoice_create_url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                print(response)
                invoice_number = response.json()\
                                        .get('response')\
                                        .get('result')\
                                        .get('invoice')\
                                        .get('invoice_number')

                freshbooks_account_id = response.json()\
                                        .get('response')\
                                        .get('result')\
                                        .get('invoice')\
                                        .get('accounting_systemid')

                freshbooks_invoice_id = response.json()\
                                        .get('response')\
                                        .get('result')\
                                        .get('invoice')\
                                        .get('id')                


                gst_decimal = Decimal(invoice_customer.gst / 100)
                net_gst = (net_total * gst_decimal).quantize(Decimal('.0001'), rounding=ROUND_UP)
                minus = ((net_total + net_gst) * (invoice_discount_percentage / 100)).quantize(Decimal('.0001'))
                total_incl_gst = (net_total + net_gst - minus).quantize(Decimal('.0001'), rounding=ROUND_UP)

                new_invoice = Invoice(
                    minus=minus,
                    discount_description=discount_description,
                    discount_percentage=discount,
                    po_number=po_number,
                    net_total=net_total,
                    gst=invoice_customer.gst,
                    net_gst=net_gst,
                    total_incl_gst=total_incl_gst,
                    invoice_number=invoice_number,
                    customer=invoice_customer,
                    pivot=invoice_customer.pivot_invoice,
                    freshbooks_account_id=freshbooks_account_id,
                    freshbooks_invoice_id=freshbooks_invoice_id,
                )
                new_invoice.save()

                for orderitem in invoice_orderitems:
                    orderitem.invoice = new_invoice
                    orderitem.save()

                return Response(data=response.json(), status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)


@api_view(['GET'])
def trip_packing_sum(request, pk):
    if request.method == 'GET':
        trip_id = pk
        packing_sum = Trip.get_packing_sum(trip_id)
        return Response(status=status.HTTP_200_OK, data=packing_sum)


@api_view(['GET'])
def get_customer_latest_invoice(request, pk):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, id=pk)
        invoice = Invoice.get_customer_latest_invoice(customer.pk)
        if invoice:
            invoice_serializer = InvoiceDetailSerializer(instance=invoice)
            return Response(status=status.HTTP_200_OK, data={'invoice': invoice_serializer.data})
        return Response(status=status.HTTP_200_OK, data={'invoice': None})


@api_view(['POST'])
def customerproduct_arrangement(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=pk)
        customerproducts = CustomerProduct.objects.filter(customer_id=customer.pk)
        all_customerproducts_ids = [cp.id for cp in customerproducts]
        arrangement = request.data.get('arrangement')
        print(arrangement)
        print(all_customerproducts_ids)
        if len(list(set(all_customerproducts_ids) - set(arrangement))) == 0:
            for cp in customerproducts:
                change_index = arrangement.index(cp.pk)
                cp.index = change_index
                cp.save()
            refresh_customerproducts = CustomerProduct.objects.filter(customer_id=customer.pk)
            customerproduct_serializer = CustomerProductListDetailSerializer(instance=refresh_customerproducts, many=True)
            return Response(data=customerproduct_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Not all customerproducts is in the list"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def customerproduct_delete(request, pk):
    if request.method == 'DELETE':
        customerproduct = get_object_or_404(CustomerProduct, id=pk)
        orderitems = OrderItem.objects.filter(customerproduct_id=customerproduct.pk)
        print("orderitems: ", orderitems)
        if len(orderitems) == 0:
            customerproduct.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Customerproduct has references to it"}, status=status.HTTP_400_BAD_REQUEST)
            # Dont implement soft delete for now
            # customerproduct.end_date = date.today()
            # customerproduct.save()
            # customerproduct_serializer = CustomerProductListDetailSerializer(instance=customerproduct)
            # return Response(customerproduct_serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def customer_delete(request, pk):
    if request.method == 'DELETE':
        customer = get_object_or_404(Customer, id=pk)
        customerproducts = CustomerProduct.objects.filter(customer_id=customer.pk)
        customerroutes = Route.get_customer_detail_routes(customer.pk)
        if len(customerproducts) == 0 and len(customerroutes) == 0:
            customergroup = CustomerGroup.objects.filter(customer_id=customer.pk)
            customergroup.delete()
            customer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Dont implement soft delete for now
            return Response({"error": "Customer has references to it"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_quotes(request):
    if (request.method == 'GET'):
        customer_id = request.GET.get('customer_id', None)
        customerproducts = CustomerProduct.objects.select_related('customer', 'product')
        if customer_id:
            customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)
        customerproduct_serializer = CustomerProductListDetailSerializer(customerproducts, many=True)
        return Response(status=status.HTTP_200_OK, data=customerproduct_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_taxes(request):
    if (request.method == 'GET'):
        client_id = settings.FRESHBOOKS_CLIENT_ID
        token = request.session['oauth_token']
        freshbooks_account_id = request.session['freshbooks_account_id']
        freshbooks = OAuth2Session(client_id, token=token)
        page = 1
        taxes_arr = []
        while(True):
            print(page)
            print(freshbooks_account_id, page)
            try:
                res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes?page={1}".format(freshbooks_account_id, page)).json()
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)
                res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes?page={1}".format(freshbooks_account_id, page)).json()
            except Exception:
                print('Invalid Grant Error')
            print(res)
            max_pages = res.get('response')\
                            .get('result')\
                            .get('pages')

            curr_page = res.get('response')\
                            .get('result')\
                            .get('page')

            taxes = res.get('response')\
                            .get('result')\
                            .get('taxes')

            for tax in taxes:
                taxes_arr.append(tax)
            if curr_page == max_pages:
                break
            else:
                page += 1

        return Response(status=status.HTTP_200_OK, data=taxes_arr)
    return Response(status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def bulk_import_orders(request):
    if (request.method == 'POST'):
        dataArr = request.data
        #  TODO: use a serializer to save model object instead
        error_rows = []
        for row in dataArr:
            customer_id = row.get('selectedCustomer').get('id')
            customerproduct_id = row.get('selectedProduct').get('id')
            quantity = row.get('quantity')
            date = row.get('date')
            do_number = row.get('do_number')

            customer_exists = Customer.objects.get(id=customer_id)
            customerproduct_exists = CustomerProduct.objects.get(id=customerproduct_id)
            route_exists = Route.objects.filter(do_number=do_number, date=date)
            parsedDateTime = datetime.strptime(date, '%Y-%m-%d')

            if (customer_exists and customerproduct_exists):
                if (len(route_exists) > 0):
                    route = route_exists[0]
                    new_orderitem = OrderItem(
                        quantity=quantity, 
                        driver_quantity=quantity,
                        unit_price=customerproduct_exists.quote_price,
                        customerproduct=customerproduct_exists,
                        route=route)
                    new_orderitem.save()
                else:
                    route = Route(do_number=do_number, date=date)
                    route.save()
                    new_orderitem = OrderItem(
                        quantity=quantity, 
                        driver_quantity=quantity,
                        unit_price=customerproduct_exists.quote_price,
                        customerproduct=customerproduct_exists,
                        route=route)
                    new_orderitem.save()
            else:
                error_rows.append(row)

        if (len(error_rows) > 0):
            return Response(status=status.HTTP_200_OK, data=error_rows)
        return Response(status=status.HTTP_201_CREATED, data=request.data)

@api_view(['GET'])
def get_filter_orderitem_rows(request):
    if (request.method == 'GET'):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        do_number = request.GET.get('do_number')
        customer_ids = request.GET.get('customer_ids')

        parsed_start_date = None
        parsed_end_date = None
        parsed_customer_ids = None
        
        try:
            if start_date:
                parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d')

            if end_date:
                parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d')

            if customer_ids:
                parsed_customer_ids = customer_ids.split(';')

        except ValueError:
            return Response(status=HTTP_400_BAD_REQUEST)

        orderitem_qset = OrderItem.objects.select_related(
            'route',
            'customerproduct',
            'customerproduct__customer',
            'customerproduct__product'
        )

        if parsed_start_date:
            orderitem_qset = orderitem_qset.filter(route__date__gte=parsed_start_date)
        if parsed_end_date:
            orderitem_qset = orderitem_qset.filter(route__date__lte=parsed_end_date)
        if parsed_customer_ids:
            orderitem_qset = orderitem_qset.filter(customerproduct__customer_id__in=parsed_customer_ids)

        orderitem_qset = orderitem_qset.filter(invoice__isnull=True)
        print(orderitem_qset.query)

        rows = list(orderitem_qset)
        print(rows)
        orderitem_serializer = OrderItemSerializer(rows, many=True)
        return Response(status=status.HTTP_200_OK, data=orderitem_serializer.data)


@api_view(['GET'])
def get_freshbooks_products(request):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    freshbooks_account_id = request.session['freshbooks_account_id']
    token = request.session['oauth_token']
    freshbooks = OAuth2Session(client_id, token=token)
    page = 1
    item_arr = []
    while(True):
        print(page)
        try:
            res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/items/items?page={1}".format(freshbooks_account_id, page)).json()
        except TokenExpiredError as e:
            token = freshbooks.refresh_token(refresh_url, **extra)
            token_updater(request, token)

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
    return Response(status=status.HTTP_200_OK, data=item_arr)


@api_view(['GET'])
def get_freshbooks_import_clients(request):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    freshbooks_account_id = request.session['freshbooks_account_id']
    token = request.session['oauth_token']
    existing_freshbooks_clients = Customer.objects.filter(freshbooks_account_id__isnull=False, freshbooks_client_id__isnull=False)
    existing_client_ids = [client.freshbooks_client_id for client in existing_freshbooks_clients]
    try:
        freshbooks_clients = Customer.get_freshbooks_clients(freshbooks_account_id, token)
    except TokenExpiredError as e:
        token = freshbooks.refresh_token(refresh_url, **extra)
        token_updater(request, token)

    not_exists_freshbooks_client = []
    for client in freshbooks_clients:
        if str(client.get('id')) not in existing_client_ids:
            not_exists_freshbooks_client.append(client)
    return Response(status=status.HTTP_200_OK, data=not_exists_freshbooks_client)


@api_view(['POST'])
def import_freshbooks_clients(request):
    if request.method == 'POST':
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks_account_id = request.session['freshbooks_account_id']
        token = request.session['oauth_token']
        import_client_ids = request.data.get('freshbooks_id_list')
        valid_import_client_ids = []
        for import_client_id in import_client_ids:
            valid_client = Customer.get_freshbooks_client(freshbooks_account_id, import_client_id, token)
            print(valid_client)
            res = valid_client.get('response').get('result').get('client')
            if res.get('id'):
                valid_import_client_ids.append(res)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, data=import_client_ids)
        try:
            Customer.import_freshbooks_clients(valid_import_client_ids, freshbooks_account_id, token)
        except TokenExpiredError as e:
            token = freshbooks.refresh_token(refresh_url, **extra)
            token_updater(request, token)

        return Response(status=status.HTTP_201_CREATED, data=import_client_ids)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_freshbooks_import_products(request):
    if request.method == 'GET':
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks_account_id = request.session['freshbooks_account_id']
        token = request.session['oauth_token']
        existing_freshbooks_products = Product.objects.filter(freshbooks_account_id__isnull=False, freshbooks_item_id__isnull=False)
        existing_product_ids = [product.freshbooks_item_id for product in existing_freshbooks_products]
        try:
            freshbooks_products = Product.get_freshbooks_products(freshbooks_account_id, token)
        except TokenExpiredError as e:
            token = freshbooks.refresh_token(refresh_url, **extra)
            token_updater(request, token)
            freshbooks_products = Product.get_freshbooks_products(freshbooks_account_id, token)

        not_exists_freshbooks_products = []
        for product in freshbooks_products:
            if str(product.get('id')) not in existing_product_ids:
                not_exists_freshbooks_products.append(product)
        return Response(status=status.HTTP_200_OK, data=not_exists_freshbooks_products)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def import_freshbooks_products(request):
    if request.method == 'POST':
        client_id = settings.FRESHBOOKS_CLIENT_ID
        freshbooks_account_id = request.session['freshbooks_account_id']
        token = request.session['oauth_token']
        import_product_ids = request.data.get('freshbooks_id_list')
        valid_import_product_list = []
        for import_product_id in import_product_ids:
            try:
                valid_product = Product.freshbooks_product_detail(import_product_id, freshbooks_account_id, token)
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)
                valid_product = Product.freshbooks_product_detail(import_product_id, freshbooks_account_id, token)
            print(valid_product)
            res = valid_product.get('response').get('result').get('item')
            if res.get('id'):
                valid_import_product_list.append(res)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, data=import_product_ids)
        print(valid_import_product_list)
        Product.freshbooks_import_products(valid_import_product_list, freshbooks_account_id, token)
        return Response(status=status.HTTP_201_CREATED, data=valid_import_product_list)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_freshbooks_clients(request):
    client_id = settings.FRESHBOOKS_CLIENT_ID
    freshbooks_account_id = request.session['freshbooks_account_id']
    token = request.session['oauth_token']
    try:
        freshbooks_clients = Customer.get_freshbooks_clients(freshbooks_account_id, token)
    except TokenExpiredError as e:
        token = freshbooks.refresh_token(refresh_url, **extra)
        token_updater(request, token)

    return Response(status=status.HTTP_200_OK, data=freshbooks_clients)


@api_view(['PUT'])
def link_customer(request):
    if request.method == 'PUT':
        freshbooks_account_id = request.session['freshbooks_account_id']
        token = request.session['oauth_token']
        customer_id = request.data.get('customer_id')
        freshbooks_client_id = request.data.get('freshbooks_client_id', None)
        pivot_invoice = request.data.get('pivot_invoice', False)
        gst = request.data.get('gst', 0)
        freshbooks_client = None
        if not customer_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        customer_obj = Customer.objects.get(pk=customer_id)
        if not customer_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        customer_obj.pivot_invoice = pivot_invoice
        customer_obj.gst = gst
        if freshbooks_client_id:
            try:
                response = Customer.get_freshbooks_client(freshbooks_account_id, freshbooks_client_id, token)
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)

            freshbooks_client = response.get('response').get('result').get('client')
        if freshbooks_client_id and freshbooks_client:
            customer_obj.freshbooks_client_id = str(freshbooks_client.get('id'));
            customer_obj.save()
            customer_serializer = CustomerListDetailUpdateSerializer(customer_obj)
            return Response(data=customer_serializer.data, status=status.HTTP_200_OK)
        if not freshbooks_client_id:
            customer_obj.freshbooks_client_id = None;
            customer_obj.freshbooks_account_id = None;
            customer_obj.save()
            customer_serializer = CustomerListDetailUpdateSerializer(customer_obj)
            return Response(data=customer_serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def link_product(request):
    if request.method == 'PUT':
        freshbooks_account_id = request.session['freshbooks_account_id']
        token = request.session['oauth_token']
        product_id = request.data.get('product_id')
        freshbooks_item_id = request.data.get('freshbooks_item_id', None)
        freshbooks_product = None
        if not product_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        product_obj = Product.objects.get(pk=product_id)
        if not product_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if freshbooks_item_id:
            try:
                response = Product.freshbooks_product_detail(freshbooks_item_id, freshbooks_account_id, token)
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)
                response = Product.freshbooks_product_detail(freshbooks_item_id, freshbooks_account_id, token)

            freshbooks_product = response.get('response').get('result').get('item')
        if freshbooks_item_id and freshbooks_product:
            product_obj.freshbooks_item_id = str(freshbooks_product.get('id'));
            product_obj.save()
            product_serializer = ProductListDetailUpdateSerializer(product_obj)
            return Response(data=product_serializer.data, status=status.HTTP_200_OK)
        if not freshbooks_item_id:
            product_obj.freshbooks_item_id = None;
            product_obj.freshbooks_account_id = None;
            product_obj.save()
            product_serializer = ProductListDetailUpdateSerializer(product_obj)
            return Response(data=product_serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
def orderitem_delete(request, pk):
    if request.method == 'DELETE':
        orderitem = OrderItem.objects.select_related('route').get(id=pk)
        route = orderitem.route
        if orderitem:
            orderitem.delete()
            if route.orderitem_set.count() == 0:
                route.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def customer_sync(request):
    if request.method == 'POST':
        token = request.session['oauth_token']
        freshbooks_account_id = request.session['freshbooks_account_id']
        try:
            Customer.update_freshbooks_clients(freshbooks_account_id, token)
        except TokenExpiredError as e:
            token = freshbooks.refresh_token(refresh_url, **extra)
            token_updater(request, token)
        except Exception as err:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        customers = Customer.objects.prefetch_related('customergroup_set', 'customergroup_set__group')
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def invoice_sync(request):
    if request.method == 'POST':
        token = request.session['oauth_token']
        freshbooks_account_id = request.session['freshbooks_account_id']
        sync_invoices = Invoice.objects.all()
        for invoice in sync_invoices:
            search_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices?search[invoice_number]={1}'.format(
                freshbooks_account_id, invoice.invoice_number
            )
            try:
                freshbooks = OAuth2Session(client_id, token=token)
                freshbooks_invoice = freshbooks.get(search_url).json()
            except TokenExpiredError as e:
                token = freshbooks.refresh_token(refresh_url, **extra)
                token_updater(request, token)
                freshbooks_invoice = freshbooks.get(search_url).json()

            print(freshbooks_invoice)
            freshbooks_invoice_search = freshbooks_invoice.get('response')\
                                                        .get('result')\
                                                        .get('invoices')

            if len(freshbooks_invoice_search) > 0:
                freshbooks_invoice = freshbooks_invoice_search[0]
                invoice.po_number = freshbooks_invoice.get('po_number')
                invoice.freshbooks_account_id = freshbooks_invoice.get('accounting_systemid')
                invoice.freshbooks_invoice_id = freshbooks_invoice.get('invoiceid')
                invoice.save()


        if not freshbooks_account_id or not token:
            return HttpResponseBadRequest()
        invoice_serializer = InvoiceListSerializer(sync_invoices, context={'request': request}, many=True)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def invoice_update(request, pk):
    if request.method == 'PUT':
        #  list of ints
        orderitems_id = request.data.get('orderitems_id')
        invoice_number = request.data.get('invoice_number')
        po_number = request.data.get('po_number')
        discount = request.data.get('discount', 0) #  in percentage
        discount_description = request.data.get('discount_description', None)

        print(orderitems_id, invoice_number, po_number, discount, discount_description)

        try:
            existing_invoice = Invoice.objects.prefetch_related('orderitem_set').get(pk=pk)
            invoice_discount_percentage = Decimal(discount)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)

        token = request.session['oauth_token']
        freshbooks_account_id = request.session['freshbooks_account_id']
        freshbooks = OAuth2Session(client_id, token=token)
        #  change invoice_create_url
        headers = {'Api-Version': 'alpha', 'Content-Type': 'application/json'}

        invoice_lines = []

        #  list of ints

        print("Selected ID: ", orderitems_id)

        for oi in existing_invoice.orderitem_set.all():
            print("set orderitem null -> ", oi.pk)
            print(oi.quantity, oi.driver_quantity, oi.unit_price)
            oi.invoice = None
            oi.save()

        orderitem_set_existing_invoice = OrderItem.objects.filter(pk__in=orderitems_id)
        for oi in orderitem_set_existing_invoice:
            oi.invoice = existing_invoice
            oi.save()

        existing_invoice.refresh_from_db()
        for orderitem in existing_invoice.orderitem_set.all():
            tax_id = orderitem.customerproduct.freshbooks_tax_1
            if tax_id:
                try:
                    res = freshbooks.get("https://api.freshbooks.com/accounting/account/{0}/taxes/taxes/{1}".format(freshbooks_account_id, tax_id)).json()
                except TokenExpiredError as e:
                    token = freshbooks.refresh_token(refresh_url, **extra)
                    token_updater(request, token)

                tax = res.get('response').get('result').get('tax')
                #  get freshbooks tax
                invoice_line =  {
                  "type": 0,
                  "description": "DATE: {0} D/O: {1}".format(
                      datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                      orderitem.route.do_number
                  ),
                  "taxName1": tax.get('name'),
                  "taxAmount1": tax.get('amount'),
                  "name": orderitem.customerproduct.product.name,
                  "qty": orderitem.driver_quantity,
                  "unit_cost": { "amount": str(orderitem.unit_price) }
                }

                invoice_lines.append(invoice_line)
            else:
                invoice_line =  {
                  "type": 0,
                  "description": "DATE: {0} D/O: {1}".format(
                      datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                      orderitem.route.do_number
                  ),
                  "name": orderitem.customerproduct.product.name,
                  "qty": orderitem.driver_quantity,
                  "unit_cost": { "amount": str(orderitem.unit_price) }
                }
                invoice_lines.append(invoice_line)

        net_total = 0
        for orderitem in existing_invoice.orderitem_set.all():
            net_total += (orderitem.driver_quantity * orderitem.unit_price)

        body = {
            "invoice": {
              "invoice_number": invoice_number,
              "po_number": po_number,
              "discount_value": discount,
              "discount_description": discount_description,
              "lines": [line for line in invoice_lines]
            }
        }
        invoice_update_url = 'https://api.freshbooks.com/accounting/account/{0}/invoices/invoices/{1}'.format(
            freshbooks_account_id, existing_invoice.freshbooks_invoice_id
        )
        #  update invoice
        print(json.dumps(body))
        response = freshbooks.put(invoice_update_url, data=json.dumps(body), headers=headers)
        if response.status_code == 200:
            invoice_number = response.json()\
                                    .get('response')\
                                    .get('result')\
                                    .get('invoice')\
                                    .get('invoice_number')

            gst_decimal = Decimal(existing_invoice.customer.gst / 100)
            net_gst = (net_total * gst_decimal).quantize(Decimal('.0001'), rounding=ROUND_UP)
            minus = ((net_total + net_gst) * (invoice_discount_percentage / 100)).quantize(Decimal('.0001'))
            total_incl_gst = (net_total + net_gst - minus).quantize(Decimal('.0001'), rounding=ROUND_UP)

            existing_invoice.minus = minus
            existing_invoice.discount_description = discount_description
            existing_invoice.discount_percentage = discount
            existing_invoice.po_number = po_number
            existing_invoice.net_total = net_total
            existing_invoice.gst = existing_invoice.customer.gst
            existing_invoice.net_gst = net_gst
            existing_invoice.total_incl_gst = total_incl_gst
            existing_invoice.invoice_number = invoice_number
            existing_invoice.save()
            return Response(data=response.json(), status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)