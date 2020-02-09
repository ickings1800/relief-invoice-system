from rest_framework import serializers
from ..models import Customer, Product, Trip, Route, OrderItem, Invoice, CustomerProduct, CustomerGroup, Group


class TripAddRouteSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)
    customer = serializers.IntegerField(required=False)
    do_number = serializers.CharField(required=False, max_length=8, allow_blank=True)

    def create(self, validated_data):
        note = validated_data.get('note')
        do_number = validated_data.get('do_number')
        customer = validated_data.get('customer')
        return Route(note=note, do_number=do_number)


class CustomerListDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'address', 'postal_code', 'tel_no', 'fax_no', 'term', 'gst')


class CustomerCreateSerializer(serializers.ModelSerializer):
    group = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        group_id = validated_data.pop('group', None)
        new_customer = super().create(validated_data)
        group = Group.objects.get(id=group_id)
        new_customer_group = CustomerGroup.objects.create(customer=new_customer, group=group)
        return new_customer

    def validate_group(self, value):
        customer_group = Group.objects.get(id=value)
        if customer_group:
            return value
        else:
            raise serializers.ValidationError("Group does not exist")

    class Meta:
        model = Customer
        fields = ('id', 'name', 'address', 'postal_code', 'tel_no', 'fax_no', 'term', 'gst', 'group')


class CustomerGroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerGroup
        fields = ('id', 'group')


class ProductListDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'specification')


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'specification')


class TripListDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('id', 'date', 'notes', 'packaging_methods')


class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('date', 'notes')


class CustomerProductListDetailSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProduct
        fields = ('id', 'quote_price', 'product')

    def get_product(self, obj):
        return obj.product.name


class CustomerProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('customer', 'product', 'quote_price')


class CustomerProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('id', 'quote_price', 'end_date')


class InvoiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('id',
                  'invoice_year',
                  'invoice_number',
                  'start_date',
                  'end_date',
                  'minus',
                  'gst',
                  'original_total',
                  'net_total',
                  'net_gst',
                  'total_incl_gst',
                  'remark',
                  'customer',
                  'date_generated')


class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = (
            'invoice_year',
            'invoice_number',
            'start_date',
            'end_date',
            'minus',
            'gst',
            'remark',
            'customer',
            'route_id_list')


class OrderItemSerializer(serializers.ModelSerializer):
    customerproduct = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'driver_quantity', 'quantity', 'note', 'packing', 'customerproduct', 'customer', 'customer_id')

    def get_customerproduct(self, obj):
        return obj.customerproduct.product.name

    def get_customer(self, obj):
        return obj.customerproduct.customer.name

    def get_customer_id(self, obj):
        return obj.customerproduct.customer.pk


class OrderItemUpdateDetailSerializer(serializers.ModelSerializer):
    customerproduct = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'driver_quantity', 'quantity', 'note', 'packing', 'customerproduct')

    def get_customerproduct(self, obj):
        return obj.customerproduct.product.name


class RouteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('do_number', 'note',)


class RouteSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)
    trip_date = serializers.SerializerMethodField()
    packing = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ('id', 'index', 'do_number', 'note', 'orderitem_set', 'trip_date', 'packing',)

    def get_trip_date(self, obj):
        return obj.trip.date.strftime("%d-%m-%Y")

    def get_packing(self, obj):
        remove_space_packing_list = [e.strip() for e in obj.trip.packaging_methods.split(',')]
        return remove_space_packing_list


class RouteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'do_number', 'note')


class TripDetailSerializer(serializers.ModelSerializer):
    route_set = RouteSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('date', 'notes', 'packaging_methods', 'route_set',)


class InvoiceDetailSerializer(serializers.ModelSerializer):
    route_set = RouteSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ('id',
                  'invoice_year',
                  'invoice_number',
                  'start_date',
                  'end_date',
                  'minus',
                  'gst',
                  'original_total',
                  'net_total',
                  'net_gst',
                  'total_incl_gst',
                  'remark',
                  'customer',
                  'date_generated',
                  'route_set')


class RouteListSerializer(serializers.ModelSerializer):
    invoice_number = serializers.SerializerMethodField()
    trip_date = serializers.SerializerMethodField()
    orderitem_set = OrderItemSerializer(many=True)

    class Meta:
        model = Route
        fields = ('id', 'index', 'do_number', 'note', 'invoice_number', 'trip_date', 'orderitem_set')

    def get_invoice_number(self, obj):
        if obj.invoice:
            return obj.invoice.invoice_number
        else:
            return ''

    def get_trip_date(self, obj):
        return obj.trip.date.strftime("%d-%m-%Y")


# class CustomerGroupSwapSerializer(serializers.Serializer):
#     group_id = serializers.IntegerField()
#     customers = serializers.ListField()
#
#     def update(self, instance, validated_data):
#         print(validated_data.get('group_id'))
#         print(validated_data.get('customers'))