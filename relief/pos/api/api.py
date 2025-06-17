from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes
from django.conf import settings
from datetime import datetime
from requests_oauthlib import OAuth2Session
from decimal import Decimal, ROUND_UP
from ..freshbooks import freshbooks_access
from ..services import FreshbooksService
from ..models import *
from .serializers import *
import json
import requests
import os


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def update_do_number_webhook(request):
    update_order_url = 'https://app.detrack.com/api/v2/dn/jobs/update'
    #  condition for info received, in progress, partial complete and completed
    data = request.data
    put_data = {}
    tracking_status = data.get('tracking_status')
    do_number = data.get('do_number')
    order_type = data.get('type')
    if order_type == 'Delivery':
        if tracking_status in ['Info received', 'Out for delivery']:
            #  to update order attachment url with the do_number
            domain = os.environ['CSRF_TRUSTED_ORIGIN']
            put_data['attachment_url'] = f'{domain}/pos/receipt/{do_number}'
            headers = {
                'Content-Type': 'application/json',
                'X-API-KEY': settings.DETRACK_API_KEY
            }
            put_object = {'do_number': do_number, 'data': put_data}
            put_object_json = json.dumps(put_object)
            response = requests.put(update_order_url, data=put_object_json, headers=headers)
            return Response(status=status.HTTP_200_OK, data=response.json())
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def group_list(request):
    if request.method == 'GET':
        groups = Group.objects.all()
        group_list_serializer = GroupListSerializer(groups, many=True)
        return Response(status=status.HTTP_200_OK, data=group_list_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.prefetch_related(
            'customergroup_set', 'customergroup_set__group')
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def product_list(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customer_id')
        if customer_id:
            products_existing = CustomerProduct.objects.filter(
                customer_id=customer_id).distinct('product_id')
            products_existing_ids = [cp.product_id for cp in products_existing]
            products = Product.objects.exclude(id__in=products_existing_ids)
        else:
            products = Product.objects.all()
        product_serializer = ProductListDetailUpdateSerializer(products, many=True)
        return Response(status=status.HTTP_200_OK, data=product_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@freshbooks_access
def product_detail(request, freshbooks_svc, pk):
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=pk)
        token = request.session['oauth_token']
        freshbooks = FreshbooksService(product.freshbooks_account_id, token)
        product_detail = freshbooks.freshbooks_product_detail(product.freshbooks_item_id)
        return Response(status=status.HTTP_200_OK, data=product_detail)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def orderitem_update(request, pk):
    if request.method == 'PUT':
        update_data = request.data
        orderitem = get_object_or_404(OrderItem, pk=pk)
        orderitem_update_serializer = OrderItemUpdateSerializer(orderitem, data=update_data)
        if orderitem_update_serializer.is_valid():
            orderitem_update_serializer.save()
            return Response(status=status.HTTP_200_OK, data=orderitem_update_serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=orderitem_update_serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def route_detail(request, pk):
    if request.method == 'GET':
        route = get_object_or_404(Route, pk=pk)
        route_serializer = RouteSerializer(route)
        return Response(status=status.HTTP_200_OK, data=route_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def route_update(request, pk):
    if request.method == 'PUT':
        #  try:
        #      body = json.loads(request.data.get('body'))
        #  except Exception as e:
        #      return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "error parsing json"})

        #  upload_files = request.data.getlist('upload_files')
        body = request.data
        route_pk = body.get('id')
        validated_note = body.get('note')
        validated_do_number = body.get('do_number')
        validated_po_number = body.get('po_number')
        validated_orderitems = body.get('orderitem_set')

        route = Route.objects.get(pk=route_pk)
        if route.po_number != validated_po_number:
            route.po_number = validated_po_number
        if route.note != validated_note:
            route.note = validated_note

        route.save()

        if not route:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "route id not found"})

        if validated_do_number:
            try:
                do_number_int = int(validated_do_number)
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "do_number is not an integer"})

            if validated_do_number != route.do_number:
                route_exists = Route.objects.filter(do_number=validated_do_number).count()
                if route_exists > 0:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"error": "route already exists with do_number {0}".format(
                            validated_do_number)}
                    )
                else:
                    route.do_number = do_number_int

        for oi in validated_orderitems:
            oi_id = oi.get('id')
            oi_driver_qty = oi.get('driver_quantity')
            oi_qty = oi.get('quantity')
            print("quantites: ", oi_driver_qty, oi_qty)
            orderitem = OrderItem.objects.get(pk=oi_id)
            try:
                if not orderitem:
                    return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "orderitem id not found"})
                if oi_driver_qty is None:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"error": "driver quantity is none"}
                    )
                if int(oi_driver_qty) < 0 or int(oi_qty) < 0:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"error": "driver quantity or quantity cannot be less than zero"}
                    )
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": e})

            orderitem.quantity = int(oi_qty)
            orderitem.driver_quantity = int(oi_driver_qty)
            #  don't change unit price when updating orderitem
            orderitem.save()
        print('after orderitem save')
        rs = RouteSerializer(route)
        print(rs.data)
        return Response(status=status.HTTP_200_OK, data=rs.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['GET'])
def customerproduct_list(request, pk):
    if request.method == 'GET':
        customerproducts = CustomerProduct.objects.filter(customer_id=pk)
        customerproduct_list_serializer = CustomerProductListDetailSerializer(
            customerproducts, many=True)
        return Response(status=status.HTTP_200_OK, data=customerproduct_list_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def customerproduct_detail(request, pk):
    if request.method == 'GET':
        customerproduct = get_object_or_404(CustomerProduct, pk=pk)
        customerproduct_list_serializer = CustomerProductListDetailSerializer(customerproduct)
        return Response(status=status.HTTP_200_OK, data=customerproduct_list_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def customerproduct_create(request):
    if request.method == 'POST':
        customerproduct_create_serializer = CustomerProductCreateSerializer(data=request.data)
        if customerproduct_create_serializer.is_valid():
            customerproduct_create_serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=customerproduct_create_serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=customerproduct_create_serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@freshbooks_access
def customerproduct_update(request, freshbooks_svc, pk):
    freshbooks_tax_id = request.data.get('freshbooks_tax_1', None)
    quote_price = request.data.get('quote_price', None)
    print('fb_tax_id: ', freshbooks_tax_id)
    print('quote_price:', quote_price)
    try:
        if freshbooks_tax_id:
            get_valid_tax = freshbooks_svc.get_freshbooks_tax(freshbooks_tax_id)
            if not get_valid_tax.get('taxid'):
                return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})

    customerproduct = CustomerProduct.objects.get(pk=pk)
    customerproduct.freshbooks_tax_1 = freshbooks_tax_id
    customerproduct.quote_price = quote_price
    customerproduct.save()
    customerproduct_serializer = CustomerProductListDetailSerializer(customerproduct)
    return Response(status=status.HTTP_200_OK, data=customerproduct_serializer.data)


@api_view(['GET'])
def invoice_detail(request, pk):
    if request.method == 'GET':
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice_serializer = InvoiceDetailSerializer(invoice)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def invoice_list(request):
    filter_customer_id = request.GET.get('customer_id')
    filter_invoice_year = request.GET.get('year')
    invoices = Invoice.objects.select_related('customer')
    try:
        if filter_invoice_year:
            invoices = invoices.filter(date_generated__year=filter_invoice_year)
        if filter_customer_id:
            invoices = invoices.filter(customer__pk=filter_customer_id)
        invoice_serializer = InvoiceListSerializer(
            list(invoices), many=True, context={'request': request}
        )
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Unable to filter invoice year'})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})


@api_view(['GET'])
def get_available_invoice_years_filter(request):
    if request.method == 'GET':
        available_years = Invoice.objects.dates('date_generated', 'year', order='DESC')
        years = [dt.year for dt in available_years]
        return Response(status=status.HTTP_200_OK, data=years)
    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Unable to get invoice years'})


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
@freshbooks_access
def create_invoice(request, freshbooks_svc):
    if request.method == 'POST':
        customer_id = request.data.get('customer_id')
        create_date = request.data.get('create_date')
        orderitems_id = request.data.get('orderitems_id')
        invoice_number = request.data.get('invoice_number')
        po_number = request.data.get('po_number')
        minus = request.data.get('discount')
        minus_description = request.data.get('discount_description')

        print(customer_id, create_date, orderitems_id, invoice_number, po_number)

        try:
            invoice_customer = Customer.objects.get(pk=customer_id)
            invoice_orderitems = OrderItem.objects.filter(pk__in=orderitems_id)
            parsed_create_date = datetime.strptime(create_date, "%Y-%m-%d")
            minus_decimal = Decimal(0)
            if minus:
                minus_decimal = Decimal(minus)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)

        price_map = {}
        for oi in invoice_orderitems:
            product_name = oi.customerproduct.product.name
            if not price_map.get(product_name):
                price_map[product_name] = oi.unit_price
            if price_map[product_name] != oi.unit_price:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Orderitems unit pricing is inconsistent"})

        print(invoice_customer, invoice_orderitems, parsed_create_date)

        freshbooks_client_id = invoice_customer.freshbooks_client_id

        if len(invoice_orderitems) > 0:
            invoice_lines = []

            for orderitem in invoice_orderitems:
                tax_id = orderitem.customerproduct.freshbooks_tax_1
                if tax_id:
                    tax = freshbooks_svc.get_freshbooks_tax(tax_id)
                    description = "DATE: {0} D/O: {1} ".format(
                        datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                        orderitem.route.do_number
                    )

                    if orderitem.note:
                        description += "P/O: {0}".format(orderitem.note)

                    invoice_line = {
                        "type": 0,
                        "description": description,
                        "taxName1": tax.get('name'),
                        "taxAmount1": tax.get('amount'),
                        "name": orderitem.customerproduct.product.name,
                        "qty": orderitem.driver_quantity,
                        "unit_cost": {"amount": str(orderitem.unit_price)}
                    }

                    invoice_lines.append(invoice_line)
                else:
                    description = "DATE: {0} D/O: {1} ".format(
                        datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                        orderitem.route.do_number
                    )

                    if orderitem.note:
                        description += "P/O: {0}".format(orderitem.note)

                    invoice_line = {
                        "type": 0,
                        "description": description,
                        "name": orderitem.customerproduct.product.name,
                        "qty": orderitem.driver_quantity,
                        "unit_cost": {"amount": str(orderitem.unit_price)}
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
                    "lines": [line for line in invoice_lines]
                }
            }
            #  create invoice
            print(json.dumps(body))
            invoice = freshbooks_svc.create_freshbooks_invoice(body)
            invoice_number = invoice.get('invoice_number')
            freshbooks_account_id = invoice.get('accounting_systemid')
            freshbooks_invoice_id = invoice.get('id')
            created_date = invoice.get('create_date')

            gst_decimal = Decimal(invoice_customer.gst / 100)
            net_total -= minus_decimal
            net_gst = (net_total * gst_decimal).quantize(Decimal('.0001'), rounding=ROUND_UP)
            total_incl_gst = (net_total + net_gst).quantize(Decimal('.0001'), rounding=ROUND_UP)

            new_invoice = Invoice(
                date_created=created_date,
                po_number=po_number,
                net_total=net_total,
                gst=invoice_customer.gst,
                net_gst=net_gst,
                minus=minus_decimal,
                discount_description=minus_description,
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

            invoice_serializer = InvoiceDetailSerializer(new_invoice)
            return Response(data=invoice_serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)


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


@api_view(['GET'])
def get_all_quotes(request):
    if (request.method == 'GET'):
        customer_id = request.GET.get('customer_id', None)
        customerproducts = CustomerProduct.objects.select_related('customer', 'product')
        if customer_id:
            customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)
        customerproduct_serializer = CustomerProductListDetailSerializer(
            customerproducts, many=True)
        return Response(status=status.HTTP_200_OK, data=customerproduct_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@freshbooks_access
def get_all_taxes(request, freshbooks_svc):
    if (request.method == 'GET'):
        taxes_arr = freshbooks_svc.get_freshbooks_taxes()
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
            po_number = row.get('po_number')

            customer_exists = Customer.objects.get(id=customer_id)
            customerproduct_exists = CustomerProduct.objects.get(id=customerproduct_id)
            route_exists = Route.objects.filter(do_number=do_number, date=date)

            if (customer_exists and customerproduct_exists):
                if (len(route_exists) > 0):
                    route = route_exists[0]
                    new_orderitem = OrderItem(
                        quantity=quantity,
                        driver_quantity=quantity,
                        note=po_number,
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
                        note=po_number,
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
                parsed_customer_ids = [x for x in customer_ids.split(';') if x != '']

        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
            orderitem_qset = orderitem_qset.filter(
                customerproduct__customer_id__in=parsed_customer_ids)

        orderitem_qset = orderitem_qset.filter(invoice__isnull=True)
        rows = list(orderitem_qset)
        orderitem_serializer = OrderItemSerializer(rows, many=True)
        return Response(status=status.HTTP_200_OK, data=orderitem_serializer.data)


@api_view(['GET'])
@freshbooks_access
def get_freshbooks_products(request, freshbooks_svc):
    item_arr = freshbooks_svc.update_freshbooks_products()
    for item in item_arr:
        item_name = item.get('name')
        item_unit_price = item.get('unit_cost').get('amount')
        item_id = item.get('id')
        item_accounting_systemid = item.get('accounting_systemid')

        item_queryset = Product.objects.filter(
            freshbooks_item_id=item_id, freshbooks_account_id=item_accounting_systemid)
        if len(item_queryset) > 0:
            save_item = False
            update_item = item_queryset.get()
            if update_item.name != item_name:
                update_item.name = item_name
                save_item = True
            if update_item.unit_price != item_unit_price:
                update_item.unit_price = item_unit_price
                save_item = True
            if save_item:
                update_item.save()
        else:
            new_item = Product(
                name=item_name,
                unit_price=item_unit_price,
                freshbooks_item_id=item_id,
                freshbooks_account_id=item_accounting_systemid
            )
            new_item.save()
    return Response(status=status.HTTP_200_OK, data=item_arr)


@api_view(['GET'])
@freshbooks_access
def get_freshbooks_import_clients(request, freshbooks_svc):
    existing_freshbooks_clients = Customer.objects.filter(
        freshbooks_account_id__isnull=False, freshbooks_client_id__isnull=False)
    existing_client_ids = [client.freshbooks_client_id for client in existing_freshbooks_clients]
    freshbooks_clients = freshbooks_svc.get_freshbooks_clients()
    not_exists_freshbooks_client = []
    for client in freshbooks_clients:
        if str(client.get('id')) not in existing_client_ids:
            not_exists_freshbooks_client.append(client)
    return Response(status=status.HTTP_200_OK, data=not_exists_freshbooks_client)


@api_view(['POST'])
@freshbooks_access
def import_freshbooks_clients(request, freshbooks_svc):
    if request.method == 'POST':
        import_client_ids = request.data.get('freshbooks_id_list')
        valid_import_client_ids = []
        for import_client_id in import_client_ids:
            valid_client = freshbooks_svc.get_freshbooks_client(import_client_id)
            print(valid_client)
            res = valid_client.get('response').get('result').get('client')
            if res.get('id'):
                valid_import_client_ids.append(res)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, data=import_client_ids)
        Customer.import_freshbooks_clients(valid_import_client_ids, freshbooks_account_id, token)
        return Response(status=status.HTTP_201_CREATED, data=import_client_ids)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@freshbooks_access
def get_freshbooks_import_products(request, freshbooks_svc):
    if request.method == 'GET':
        existing_freshbooks_products = Product.objects.filter(
            freshbooks_account_id__isnull=False, freshbooks_item_id__isnull=False)
        existing_product_ids = [
            product.freshbooks_item_id for product in existing_freshbooks_products]
        freshbooks_products = freshbooks_svc.get_freshbooks_products()

        not_exists_freshbooks_products = []
        for product in freshbooks_products:
            if str(product.get('id')) not in existing_product_ids:
                not_exists_freshbooks_products.append(product)
        return Response(status=status.HTTP_200_OK, data=not_exists_freshbooks_products)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@freshbooks_access
def import_freshbooks_products(request, freshbooks_svc):
    if request.method == 'POST':
        import_product_ids = request.data.get('freshbooks_id_list')
        valid_import_product_list = []
        for import_product_id in import_product_ids:
            valid_product = freshbooks_svc.freshbooks_product_detail(import_product_id)
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
@freshbooks_access
def get_freshbooks_clients(request, freshbooks_svc):
    freshbooks_clients = freshbooks_svc.get_freshbooks_clients()
    return Response(status=status.HTTP_200_OK, data=freshbooks_clients)


@api_view(['PUT'])
@freshbooks_access
def link_customer(request, freshbooks_svc):
    if request.method == 'PUT':
        customer_id = request.data.get('customer_id')
        freshbooks_client_id = request.data.get('freshbooks_client_id', None)
        pivot_invoice = request.data.get('pivot_invoice', False)
        gst = request.data.get('gst', 0)
        download_prefix = request.data.get('download_prefix', None)
        download_suffix = request.data.get('download_suffix', None)
        to_fax = request.data.get('to_fax', False)
        to_email = request.data.get('to_email', False)
        to_print = request.data.get('to_print', False)
        to_whatsapp = request.data.get('to_whatsapp', False)
        freshbooks_client = None
        if not customer_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        customer_obj = Customer.objects.get(pk=customer_id)
        if not customer_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        customer_obj.pivot_invoice = pivot_invoice
        customer_obj.gst = gst
        customer_obj.download_prefix = download_prefix
        customer_obj.download_suffix = download_suffix
        customer_obj.to_fax = to_fax
        customer_obj.to_email = to_email
        customer_obj.to_print = to_print
        customer_obj.to_whatsapp = to_whatsapp
        
        if freshbooks_client_id:
            response = freshbooks_svc.get_freshbooks_client(freshbooks_client_id)
            freshbooks_client = response.get('response').get('result').get('client')
        if freshbooks_client_id and freshbooks_client:
            customer_obj.freshbooks_client_id = str(freshbooks_client.get('id'))
            customer_obj.save()
            customer_serializer = CustomerListDetailUpdateSerializer(customer_obj)
            return Response(data=customer_serializer.data, status=status.HTTP_200_OK)
        if not freshbooks_client_id:
            customer_obj.freshbooks_client_id = None
            customer_obj.freshbooks_account_id = None
            customer_obj.save()
            customer_serializer = CustomerListDetailUpdateSerializer(customer_obj)
            return Response(data=customer_serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@freshbooks_access
def link_product(request, freshbooks_svc):
    if request.method == 'PUT':
        product_id = request.data.get('product_id')
        freshbooks_item_id = request.data.get('freshbooks_item_id', None)
        freshbooks_product = None
        if not product_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        product_obj = Product.objects.get(pk=product_id)
        if not product_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if freshbooks_item_id:
            response = freshbooks_svc.freshbooks_product_detail(freshbooks_item_id)
            freshbooks_product = response.get('response').get('result').get('item')
        if freshbooks_item_id and freshbooks_product:
            product_obj.freshbooks_item_id = str(freshbooks_product.get('id'))
            product_obj.save()
            product_serializer = ProductListDetailUpdateSerializer(product_obj)
            return Response(data=product_serializer.data, status=status.HTTP_200_OK)
        if not freshbooks_item_id:
            product_obj.freshbooks_item_id = None
            product_obj.freshbooks_account_id = None
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
@freshbooks_access
def customer_sync(request, freshbooks_svc):
    if request.method == 'POST':
        try:
            freshbooks_svc.update_freshbooks_clients()
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        customers = Customer.objects.prefetch_related(
            'customergroup_set', 'customergroup_set__group')
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@freshbooks_access
def invoice_sync(request, freshbooks_svc):
    if request.method == 'POST':
        sync_invoices = Invoice.objects.all()
        for invoice in sync_invoices:
            freshbooks_invoice_search = freshbooks_svc.search_freshbooks_invoices(invoice.invoice_number)
            if len(freshbooks_invoice_search) > 0:
                freshbooks_invoice = freshbooks_invoice_search[0]
                invoice.po_number = freshbooks_invoice.get('po_number')
                invoice.date_created = freshbooks_invoice.get('create_date')
                invoice.freshbooks_account_id = freshbooks_invoice.get('accounting_systemid')
                invoice.freshbooks_invoice_id = freshbooks_invoice.get('invoiceid')
                invoice.save()

        if not freshbooks_account_id or not token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        invoice_serializer = InvoiceListSerializer(
            sync_invoices, context={'request': request}, many=True)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@freshbooks_access
def invoice_update(request, freshbooks_svc, pk):
    if request.method == 'PUT':
        #  list of ints
        orderitems_id = request.data.get('orderitems_id')
        invoice_number = request.data.get('invoice_number')
        po_number = request.data.get('po_number')
        minus = request.data.get('discount')
        minus_description = request.data.get('discount_description')

        print(orderitems_id, invoice_number, po_number)

        try:
            existing_invoice = Invoice.objects.prefetch_related('orderitem_set').get(pk=pk)
            minus_decimal = Decimal(minus)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)

        invoice_lines = []

        #  list of ints

        print("Selected ID: ", orderitems_id)

        orderitem_set_existing_invoice = OrderItem.objects.filter(pk__in=orderitems_id)

        price_map = {}
        for oi in orderitem_set_existing_invoice:
            product_name = oi.customerproduct.product.name
            if not price_map.get(product_name):
                price_map[product_name] = oi.unit_price
            if price_map[product_name] != oi.unit_price:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Orderitems unit pricing is inconsistent"})

        for oi in existing_invoice.orderitem_set.all():
            print("set orderitem null -> ", oi.pk)
            print(oi.quantity, oi.driver_quantity, oi.unit_price)
            oi.invoice = None
            oi.save()

        for oi in orderitem_set_existing_invoice:
            oi.invoice = existing_invoice
            oi.save()

        existing_invoice.refresh_from_db()

        for orderitem in existing_invoice.orderitem_set.all():
            tax_id = orderitem.customerproduct.freshbooks_tax_1
            if tax_id:
                tax = freshbooks_svc.get_freshbooks_tax(tax_id)

                description = "DATE: {0} D/O: {1} ".format(
                    datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                    orderitem.route.do_number
                )

                if orderitem.note:
                    description += "P/O: {0}".format(orderitem.note)

                invoice_line = {
                    "type": 0,
                    "description": description,
                    "taxName1": tax.get('name'),
                    "taxAmount1": tax.get('amount'),
                    "name": orderitem.customerproduct.product.name,
                    "qty": orderitem.driver_quantity,
                    "unit_cost": {"amount": str(orderitem.unit_price)}
                }

                invoice_lines.append(invoice_line)
            else:
                description = "DATE: {0} D/O: {1} ".format(
                    datetime.strftime(orderitem.route.date, '%d-%m-%Y'),
                    orderitem.route.do_number
                )

                if orderitem.note:
                    description += "P/O: {0}".format(orderitem.note)

                invoice_line = {
                    "type": 0,
                    "description": description,
                    "name": orderitem.customerproduct.product.name,
                    "qty": orderitem.driver_quantity,
                    "unit_cost": {"amount": str(orderitem.unit_price)}
                }
                invoice_lines.append(invoice_line)

        net_total = 0
        for orderitem in existing_invoice.orderitem_set.all():
            net_total += (orderitem.driver_quantity * orderitem.unit_price)

        body = {
            "invoice": {
                "invoice_number": invoice_number,
                "po_number": po_number,
                "lines": [line for line in invoice_lines]
            }
        }

        #  update invoice
        print(json.dumps(body))
        freshbooks_updated_invoice = freshbooks_svc.update_freshbooks_invoice(
            existing_invoice.freshbooks_account_id, body
        )
        if response.status_code == 200:
            invoice_number = freshbooks_updated_invoice.get('invoice_number')
            date_created = freshbooks_updated_invoice.get('create_date')

            gst_decimal = Decimal(existing_invoice.gst / 100)
            net_total -= minus_decimal
            net_gst = (net_total * gst_decimal).quantize(Decimal('.0001'), rounding=ROUND_UP)
            total_incl_gst = (net_total + net_gst).quantize(Decimal('.0001'), rounding=ROUND_UP)

            existing_invoice.create_date = date_created
            existing_invoice.po_number = po_number
            existing_invoice.net_total = net_total
            existing_invoice.gst = existing_invoice.gst
            existing_invoice.net_gst = net_gst
            existing_invoice.total_incl_gst = total_incl_gst
            existing_invoice.invoice_number = invoice_number
            existing_invoice.minus = minus_decimal
            existing_invoice.discount_description = minus_description
            existing_invoice.save()
            return Response(data=response.json(), status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)
