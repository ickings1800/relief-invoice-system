from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .serializers import TripAddRouteSerializer, \
    TripListDetailUpdateSerializer, CustomerListDetailUpdateSerializer, ProductListDetailUpdateSerializer, \
    CustomerCreateSerializer, ProductCreateSerializer, TripCreateSerializer, CustomerProductListDetailSerializer,\
    CustomerProductCreateSerializer, CustomerProductUpdateSerializer, RouteListSerializer, InvoiceListSerializer,\
    TripDetailSerializer, OrderItemUpdateDetailSerializer, RouteUpdateSerializer, RouteDetailSerializer

from ..models import Trip, Route, Customer, CustomerProduct, OrderItem, Product, Invoice


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
        return self.create(request, *args, **kwargs)


class ProductList(ListAPIView):
    def get(self, request, *args, **kwargs):
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
        trip = Trip.objects.all()
        trip_serializer = TripListDetailUpdateSerializer(trip, many=True)
        return Response(status=status.HTTP_200_OK, data=trip_serializer.data)


class TripDetail(RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripListDetailUpdateSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TripCreate(CreateAPIView):
    serializer_class = TripCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TripUpdate(UpdateAPIView):
    serializer_class = TripListDetailUpdateSerializer
    queryset = Trip.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
        print(validated_note, validated_customer)
        Trip.create_route(trip.pk, validated_note, customer_id=validated_customer)
        return Response(status=status.HTTP_201_CREATED, data=request.data)


class TripRouteList(ListAPIView):
    def get(self, request, *args, **kwargs):
        try:
            trip = Trip.objects.get(pk=self.kwargs['pk'])
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        trip_serializer = TripDetailSerializer(instance=trip)
        return Response(status=status.HTTP_200_OK, data=trip_serializer.data)


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
    serializer_class = RouteDetailSerializer

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
        customerproducts = CustomerProduct.objects.filter(customer=self.kwargs['pk'])
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
        return self.update(request, *args, **kwargs)


class CustomerRouteList(ListAPIView):
    def get(self, request, *args, **kwargs):
        routes = Route.get_customer_routes(self.kwargs['pk'])
        route_serializer = RouteListSerializer(routes, many=True)
        return Response(status=status.HTTP_200_OK, data=route_serializer.data)


class CustomerInvoiceList(ListAPIView):
    def get(self, request, *args, **kwargs):
        invoices = Invoice.get_customer_invoices(self.kwargs['pk'])
        invoice_serializer = InvoiceListSerializer(invoices, many=True)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)


class InvoiceList(ListAPIView):
    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.all()
        invoice_serializer = InvoiceListSerializer(invoices, many=True)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)


class InvoiceDelete(DestroyAPIView):
    queryset = Invoice.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

