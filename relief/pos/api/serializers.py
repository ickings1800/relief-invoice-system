from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from ..models import Customer, Product, Trip, Route, OrderItem, Invoice, CustomerProduct, CustomerGroup, Group



class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)

    def save(self):
        return Group.group_create(self.validated_data['name'])


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class CustomerListDetailUpdateSerializer(serializers.ModelSerializer):
    group = SerializerMethodField()
    class Meta:
        model = Customer
        fields = (
            'id', 'name', 'gst', 'group', 'freshbooks_account_id',
            'freshbooks_client_id', 'pivot_invoice', 'address','postal_code',
            'country'
        )

    def get_group(self, obj):
        return [customergroup.group.name for customergroup in obj.customergroup_set.all()]


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


class ProductListDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'unit_price', 'freshbooks_item_id', 'freshbooks_account_id')


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
    trip_url = serializers.HyperlinkedIdentityField(
        view_name="pos:trip_detail", lookup_field="pk", lookup_url_kwarg="pk"
    )
    class Meta:
        model = Trip
        fields = ('pk', 'notes', 'route_set', 'trip_url')
        #fields = ('url', 'pk', 'date', 'notes', 'packaging_methods', 'route_set')
        #extra_kwargs = {'url': {'view_name': 'pos:trip_detail', 'lookup_field': 'pk'}}


class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('notes',)


class CustomerProductListDetailSerializer(serializers.ModelSerializer):
    customer_name = SerializerMethodField()
    product_name = SerializerMethodField()
    class Meta:
        model = CustomerProduct
        fields = (
            'id', 'customer_id', 'customer_name',
            'product_id', 'product_name', 'quote_price',
            'freshbooks_tax_1', 'archived'
        )

    def get_customer_name(self, obj):
        return obj.customer.name

    def get_product_name(self, obj):
        return obj.product.name


class CustomerProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('customer', 'product', 'quote_price', 'freshbooks_tax_1')


class CustomerProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('id', 'quote_price', 'freshbooks_tax_1', 'archived')


class InvoiceListSerializer(serializers.HyperlinkedModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_pk = serializers.SerializerMethodField()
    download_url = serializers.HyperlinkedIdentityField(
        view_name="pos:invoice_download", lookup_field="pk", lookup_url_kwarg="pk"
    )
    class Meta:
        model = Invoice
        fields = (
            'id',
            'invoice_number',
            'total_incl_gst',
            'remark',
            'customer_name',
            'date_generated',
            'po_number',
            'minus',
            'discount_description',
            'discount_percentage',
            'url',
            'download_url',
            'customer_pk'
        )
        extra_kwargs = {
            'url': {'view_name': 'pos:invoice_detail', 'lookup_field': 'pk'},
        }

    def get_customer_name(self, obj):
        return obj.customer.name

    def get_customer_pk(self, obj):
        return obj.customer.pk


class OrderItemSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    do_number = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'driver_quantity', 'quantity', 'customer_name', 'customer_id', 'product_name', 'date', 'do_number', 'unit_price', 'note')

    def get_customer_name(self, obj):
        return obj.customerproduct.customer.name

    def get_customer_id(self, obj):
        return obj.customerproduct.customer.id

    def get_product_name(self,obj):
        return obj.customerproduct.product.name

    def get_date(self, obj):
        return obj.route.date

    def get_do_number(self,obj):
        return obj.route.do_number


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'driver_quantity', 'quantity', 'note')


class RouteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('do_number', 'note',)


class RouteSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)
    date = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = (
            'id', 'index', 'do_number', 'po_number',
            'note', 'date', 'checked', 'orderitem_set'
        )

    def get_date(self, obj):
        return obj.date.strftime("%d-%m-%Y")


class RouteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'do_number', 'note', 'checked',)


class TripDetailSerializer(serializers.ModelSerializer):
    route_set = RouteSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('notes', 'route_set',)


class InvoiceDetailSerializer(serializers.ModelSerializer):
    orderitem_set = SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ('id',
                  'invoice_number',
                  'minus',
                  'gst',
                  'net_total',
                  'net_gst',
                  'total_incl_gst',
                  'remark',
                  'customer',
                  'po_number',
                  'discount_description',
                  'discount_percentage',
                  'date_generated',
                  'orderitem_set')

    def get_orderitem_set(self, obj):
        ordered_orderitem = obj.orderitem_set.order_by('route__date')
        return OrderItemSerializer(ordered_orderitem, many=True, context=self.context).data



class RouteListSerializer(serializers.HyperlinkedModelSerializer):
    invoice_number = serializers.SerializerMethodField()
    trip_date = serializers.SerializerMethodField()
    #trip_url = serializers.HyperlinkedIdentityField(view_name="pos:trip_detail", lookup_field="trip_id", lookup_url_kwarg="pk")
    orderitem_set = OrderItemSerializer(many=True)

    class Meta:
        model = Route
        #fields = ('trip_url', 'id', 'checked', 'index', 'do_number', 'note', 'invoice_number', 'trip_date', 'orderitem_set')
        fields = ('id', 'checked', 'index', 'do_number', 'note', 'invoice_number', 'trip_date', 'orderitem_set')

    def get_invoice_number(self, obj):
        if obj.invoice:
            return obj.invoice.invoice_number
        else:
            return ''

    def get_trip_date(self, obj):
        if (obj.trip):
            return obj.trip.date.strftime("%d-%m-%Y")


# class CustomerGroupSwapSerializer(serializers.Serializer):
#     group_id = serializers.IntegerField()
#     customers = serializers.ListField()
#
#     def update(self, instance, validated_data):
#         print(validated_data.get('group_id'))
#         print(validated_data.get('customers'))
