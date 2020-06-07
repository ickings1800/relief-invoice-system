from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

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


class CustomerGroupSerializer(serializers.HyperlinkedModelSerializer):
    customer_name = serializers.SerializerMethodField()
    group_id = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomerGroup
        fields = ('id', 'index', 'customer_name', 'customer_id', 'group_id', 'group_name', 'url')
        extra_kwargs = {
            'url': {'view_name': 'pos:customer_detail_view', 'lookup_field': 'id'},
        }

    def get_customer_name(self, obj):
        return obj.customer.name

    def get_group_id(self, obj):
        return obj.group.id

    def get_group_name(self, obj):
        return obj.group.name


class SimpleGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)

    def save(self):
        return Group.group_create(self.validated_data['name'])


class GroupListSerializer(serializers.ModelSerializer):
    customergroup_set = CustomerGroupSerializer(many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'customergroup_set')


class CustomerListDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name')


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


class TripRouteCheckedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('checked',)


class TripListDetailUpdateSerializer(serializers.HyperlinkedModelSerializer):
    route_set = TripRouteCheckedSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('url', 'pk', 'date', 'notes', 'packaging_methods', 'route_set')
        extra_kwargs = {'url': {'view_name': 'pos:trip_detail', 'lookup_field': 'pk'}}


class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('date', 'notes')


class CustomerProductListDetailSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProduct
        fields = ('id', 'quote_price', 'product', 'product_id', 'index', 'start_date', 'end_date')

    def get_product(self, obj):
        return obj.product.name

    def get_product_id(self, obj):
        return obj.product.id


class CustomerProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('customer', 'product', 'quote_price')

    def create(self, validated_data):
        customer_id = validated_data.get('customer')
        existing_customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)
        validated_data['index'] = len(existing_customerproducts)
        print(validated_data)
        return super(CustomerProductCreateSerializer, self).create(validated_data)


class CustomerProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('id', 'quote_price', 'end_date')


class InvoiceListSerializer(serializers.ModelSerializer):
    route_set = SerializerMethodField()

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
                  'route_set',)

    def get_route_set(self, obj):
        ordered_routes = obj.route_set.order_by('trip__date')
        return RouteSerializer(ordered_routes, many=True, context=self.context).data


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
    customerproduct_index = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'driver_quantity', 'quantity', 'note', 'packing', 'customerproduct', 'customerproduct_index', 'customer', 'customer_id')

    def get_customerproduct(self, obj):
        return obj.customerproduct.product.name

    def get_customerproduct_index(self, obj):
        return obj.customerproduct.index

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
        fields = ('id', 'index', 'do_number', 'note', 'trip_date', 'packing', 'checked', 'orderitem_set')

    def get_trip_date(self, obj):
        return obj.trip.date.strftime("%d-%m-%Y")

    def get_packing(self, obj):
        if obj.trip.packaging_methods:
            return [e.strip() for e in obj.trip.packaging_methods.split(',')]
        return []


class RouteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'do_number', 'note', 'checked',)


class TripDetailSerializer(serializers.ModelSerializer):
    route_set = RouteSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('date', 'notes', 'packaging_methods', 'route_set',)


class InvoiceDetailSerializer(serializers.ModelSerializer):
    route_set = SerializerMethodField()

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

    def get_route_set(self, obj):
        ordered_routes = obj.route_set.order_by('trip__date')
        return RouteSerializer(ordered_routes, many=True, context=self.context).data



class RouteListSerializer(serializers.HyperlinkedModelSerializer):
    invoice_number = serializers.SerializerMethodField()
    trip_date = serializers.SerializerMethodField()
    trip_url = serializers.HyperlinkedIdentityField(view_name="pos:trip_detail", lookup_field="trip_id", lookup_url_kwarg="pk")
    orderitem_set = OrderItemSerializer(many=True)

    class Meta:
        model = Route
        fields = ('trip_url', 'id', 'checked', 'index', 'do_number', 'note', 'invoice_number', 'trip_date', 'orderitem_set')

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