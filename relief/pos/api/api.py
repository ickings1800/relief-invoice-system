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
    TripDetailSerializer, OrderItemUpdateDetailSerializer, RouteUpdateSerializer, RouteDetailSerializer, RouteSerializer,\
    InvoiceCreateSerializer, InvoiceDetailSerializer, CustomerGroupUpdateSerializer

from ..models import Trip, Route, Customer, CustomerProduct, OrderItem, Product, Invoice, CustomerGroup, Group
from datetime import datetime, timedelta, date
from django.db.models import Prefetch


class CustomerList(ListAPIView):
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)


class CustomerDetail(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerListDetailUpdateSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CustomerUpdate(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerListDetailUpdateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CustomerCreate(CreateAPIView):
    serializer_class = CustomerCreateSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        return self.create(request, *args, **kwargs)


class CustomerGroupUpdate(UpdateAPIView):
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupUpdateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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


class ProductDetail(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListDetailUpdateSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ProductCreate(CreateAPIView):
    serializer_class = ProductCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductUpdate(UpdateAPIView):
    serializer_class = ProductListDetailUpdateSerializer
    queryset = Product.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
            trips = Trip.objects.all()
        trip_serializer = TripListDetailUpdateSerializer(trips, many=True)
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
            trip = Trip.objects.get(pk=self.kwargs['pk'])
            routes = trip.route_set.all().order_by('index')
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        route_serializer = RouteSerializer(instance=routes, many=True)
        return Response(status=status.HTTP_200_OK, data=route_serializer.data)


class OrderItemDetail(RetrieveAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemUpdateDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OrderItemUpdate(UpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemUpdateDetailSerializer

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


@api_view(['POST'])
def customergroup_arrange(request, group_id):
    if request.method == 'POST':
        customergroups = CustomerGroup.objects.filter(group_id=group_id)
        customergroup_list_arrangement = request.data['arrangement']
        CustomerGroup.customergroup_swap(customergroups, customergroup_list_arrangement)
        return Response(status=status.HTTP_200_OK, data=request.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def group_change(request, pk):
    if request.method == 'PUT':
        group_id = request.data['group']
        Group.group_change(pk, group_id)
        return Response(status=status.HTTP_200_OK, data=request.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


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
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        customer_id = self.kwargs['pk']
        if start_date and end_date:
            customerproducts = CustomerProduct.get_customerproducts_by_date(customer_id, start_date, end_date)
        else:
            customerproducts = CustomerProduct.get_latest_customerproducts(customer_id)
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
        customerproduct_id = request.data.get('id')
        new_quote_price = request.data.pop('quote_price')
        new_start_date = request.data.get('end_date')
        existing_customerproduct = CustomerProduct.objects.get(id=customerproduct_id)
        if datetime.strptime(new_start_date, '%Y-%m-%d').date() <= existing_customerproduct.start_date:
            return Response({"error": "End date is earlier than or equal to start date"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            new_customerproduct = CustomerProduct(customer_id=existing_customerproduct.customer_id,
                                                  product_id=existing_customerproduct.product_id,
                                                  quote_price=new_quote_price,
                                                  start_date=new_start_date)
            new_customerproduct.save()
            return self.update(request, *args, **kwargs)


class CustomerRouteList(ListAPIView):
    def get(self, request, *args, **kwargs):
        customer_id = self.kwargs['pk']
        date_start_string = self.request.query_params.get('start_date')
        date_end_string = self.request.query_params.get('end_date')
        if date_start_string is not None and date_end_string is not None:
            date_start = datetime.strptime(date_start_string, '%Y-%m-%d %H:%M:%S')
            date_end = datetime.strptime(date_end_string, '%Y-%m-%d %H:%M:%S')
            #  date_start will start from exactly midnight by default
            #  date_end will have to add timedelta because it will also end at exactly at midnight,
            #  causing the last route order to not be included.
            date_end += timedelta(hours=23, minutes=59, seconds=59)
            date_end_formatted = datetime.strftime(date_end, '%Y-%m-%d %H:%M:%S')
            date_start_formatted = datetime.strftime(date_start, '%Y-%m-%d %H:%M:%S')
            routes = Route.get_customer_routes_orderitems_by_date(date_start_formatted, date_end_formatted, customer_id)
            route_serializer = RouteSerializer(routes, many=True)
        else:
            routes = Route.get_customer_routes(customer_id)
            route_serializer = RouteListSerializer(routes, many=True)

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
        invoices = Invoice.objects.all()
        invoice_serializer = InvoiceListSerializer(invoices, many=True)
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
                rs = RouteListSerializer(route_list, many=True)
                return Response(status=status.HTTP_200_OK, data=rs.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response(status.HTTP_400_BAD_REQUEST)


class InvoiceDelete(DestroyAPIView):
    queryset = Invoice.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class InvoiceCreate(CreateAPIView):
    serializer_class = InvoiceCreateSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        customer_id = request.data.get('customer')
        customer_gst = request.data.get('gst')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        invoice_year = request.data.get('invoice_year')
        invoice_number = request.data.get('invoice_number')
        route_id_list = request.data.get('route_id_list')
        print(customer_gst, start_date, end_date, invoice_year, invoice_number, route_id_list)
        if len(route_id_list) > 0:
            try:
                invoice_id = Invoice.generate_invoice(customer_id, customer_gst, start_date, end_date, invoice_year,
                                                  invoice_number, route_id_list)
                pdf_url = reverse('pos:invoice_pdf_view', args=[invoice_id])
            except ValueError as e:
                return Response({str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Route list is empty'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'pdf_url': pdf_url}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def trip_packing_sum(request, pk):
    if request.method == 'GET':
        trip_id = pk
        packing_sum = Trip.get_packing_sum(trip_id)
        return Response(status=status.HTTP_200_OK, data=packing_sum)


@api_view(['GET'])
def get_invoice_number(request):
    if request.method == 'GET':
        invoice_number = Invoice.get_next_invoice_number()
        data = {'number': invoice_number}
        return Response(status=status.HTTP_200_OK, data=data)
