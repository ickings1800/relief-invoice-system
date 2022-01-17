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
            'country', 'download_prefix', 'download_suffix', 'to_fax','to_email',
            'to_print', 'to_whatsapp'
        )

    def get_group(self, obj):
        return [customergroup.group.name for customergroup in obj.customergroup_set.all()]


class ProductListDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'unit_price', 'freshbooks_item_id', 'freshbooks_account_id')


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


class InvoiceListSerializer(serializers.HyperlinkedModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_pk = serializers.SerializerMethodField()
    download_url = serializers.HyperlinkedIdentityField(
        view_name="pos:invoice_download", lookup_field="pk", lookup_url_kwarg="pk"
    )
    attachments_url = serializers.HyperlinkedIdentityField(
        view_name="pos:invoice_attachments", lookup_field="pk", lookup_url_kwarg="pk"
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
            'date_created',
            'po_number',
            'minus',
            'discount_description',
            'discount_percentage',
            'download_url',
            'attachments_url',
            'customer_pk'
        )

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
    do_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id', 'driver_quantity', 'quantity', 'customer_name', 
            'customer_id', 'product_name', 'date', 'do_number', 
            'unit_price', 'note', 'do_image'
        )

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

    def get_do_image(self, obj):
        if obj.route.do_image:
            return obj.route.do_image.url
        return None


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'driver_quantity', 'quantity', 'note')


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
    orderitem_set = OrderItemSerializer(many=True)

    class Meta:
        model = Route
        fields = ('id', 'checked', 'index', 'do_number', 'note', 'invoice_number', 'trip_date', 'orderitem_set')

    def get_invoice_number(self, obj):
        if obj.invoice:
            return obj.invoice.invoice_number
        else:
            return ''

    def get_trip_date(self, obj):
        if (obj.trip):
            return obj.trip.date.strftime("%d-%m-%Y")