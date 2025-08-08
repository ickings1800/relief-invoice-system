import json
import time
from datetime import datetime
from decimal import ROUND_UP, Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..freshbooks import freshbooks_access
from ..managers import get_company_from_request, get_object_or_404_with_company
from ..models import *
from ..tasks import *
from .serializers import *


@api_view(["GET"])
def group_list(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        groups = Group.objects.filter(company=company)
        group_list_serializer = GroupListSerializer(groups, many=True)
        return Response(status=status.HTTP_200_OK, data=group_list_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def customer_list(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customers = Customer.objects.filter(company=company).prefetch_related(
            "customergroup_set", "customergroup_set__group"
        )
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def product_list(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customer_id = request.GET.get("customer_id")
        if customer_id:
            products_existing = CustomerProduct.objects.filter(company=company, customer_id=customer_id).distinct(
                "product_id"
            )
            products_existing_ids = [cp.product_id for cp in products_existing]
            products = Product.objects.filter(company=company).exclude(id__in=products_existing_ids)
        else:
            products = Product.objects.filter(company=company)
        product_serializer = ProductListDetailUpdateSerializer(products, many=True)
        return Response(status=status.HTTP_200_OK, data=product_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@freshbooks_access
def product_detail(request, freshbooks_svc, pk):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        product = get_object_or_404_with_company(Product, company, pk=pk)
        product_detail = freshbooks_svc.freshbooks_product_detail(product.freshbooks_item_id)
        return Response(status=status.HTTP_200_OK, data=product_detail)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def orderitem_update(request, pk):
    if request.method == "PUT":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        update_data = request.data
        orderitem = get_object_or_404_with_company(OrderItem, company, pk=pk)
        orderitem_update_serializer = OrderItemUpdateSerializer(orderitem, data=update_data)
        if orderitem_update_serializer.is_valid():
            orderitem_update_serializer.save()
            return Response(status=status.HTTP_200_OK, data=orderitem_update_serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=orderitem_update_serializer.errors)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def route_detail(request, pk):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        route = get_object_or_404_with_company(Route, company, pk=pk)
        route_serializer = RouteSerializer(route)
        return Response(status=status.HTTP_200_OK, data=route_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def route_update(request, pk):
    if request.method == "PUT":
        #  try:
        #      body = json.loads(request.data.get('body'))
        #  except Exception as e:
        #      return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "error parsing json"})

        #  upload_files = request.data.getlist('upload_files')
        body = request.data
        route_pk = body.get("id")
        validated_note = body.get("note")
        validated_do_number = body.get("do_number")
        validated_po_number = body.get("po_number")
        validated_orderitems = body.get("orderitem_set")

        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        route = Route.objects.filter(company=company, pk=route_pk).first()
        if not route:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Route not found"})
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
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "do_number is not an integer"},
                )

            if validated_do_number != route.do_number:
                route_exists = Route.objects.filter(company=company, do_number=validated_do_number).count()
                if route_exists > 0:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"error": "route already exists with do_number {0}".format(validated_do_number)},
                    )
                else:
                    route.do_number = do_number_int

        for oi in validated_orderitems:
            oi_id = oi.get("id")
            oi_driver_qty = oi.get("driver_quantity")
            oi_qty = oi.get("quantity")
            print("quantites: ", oi_driver_qty, oi_qty)
            orderitem = OrderItem.objects.filter(company=company, pk=oi_id).first()
            if not orderitem:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={"error": "OrderItem not found"},
                )
            try:
                if oi_driver_qty is None:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"error": "driver quantity is none"},
                    )
                if int(oi_driver_qty) < 0 or int(oi_qty) < 0:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"error": "driver quantity or quantity cannot be less than zero"},
                    )
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": e})

            orderitem.quantity = int(oi_qty)
            orderitem.driver_quantity = int(oi_driver_qty)
            #  don't change unit price when updating orderitem
            orderitem.save()
        print("after orderitem save")
        rs = RouteSerializer(route)
        print(rs.data)
        return Response(status=status.HTTP_200_OK, data=rs.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def update_grouping(request):
    if request.method == "PUT":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        group_id = request.data.get("group_id", None)
        arrangement = request.data.get("arrangement", None)
        if group_id and isinstance(arrangement, list):
            customers = CustomerGroup.update_grouping(company, group_id, arrangement)
            customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
            return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)


@api_view(["POST"])
def group_create(request):
    if request.method == "POST":
        try:
            group_create_serializer = GroupCreateSerializer(data=request.data)
            if group_create_serializer.is_valid():
                new_group = group_create_serializer.save()
                print(type(new_group))
                group_list_serializer = GroupListSerializer(new_group)
                return Response(status=status.HTTP_201_CREATED, data=group_list_serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)
        except Exception as group_name_exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": str(group_name_exists)},
            )


@api_view(["GET"])
def customerproduct_list(request, pk):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customerproducts = CustomerProduct.objects.filter(company=company, customer_id=pk)
        customerproduct_list_serializer = CustomerProductListDetailSerializer(customerproducts, many=True)
        return Response(status=status.HTTP_200_OK, data=customerproduct_list_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def customerproduct_detail(request, pk):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customerproduct = get_object_or_404_with_company(CustomerProduct, company, pk=pk)
        customerproduct_list_serializer = CustomerProductListDetailSerializer(customerproduct)
        return Response(status=status.HTTP_200_OK, data=customerproduct_list_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def customerproduct_create(request):
    if request.method == "POST":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        request.data["company"] = company.id
        customerproduct_create_serializer = CustomerProductCreateSerializer(data=request.data)
        if customerproduct_create_serializer.is_valid():
            customerproduct_create_serializer.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data=customerproduct_create_serializer.data,
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data=customerproduct_create_serializer.errors,
        )
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@freshbooks_access
def customerproduct_update(request, freshbooks_svc, pk):
    freshbooks_tax_id = request.data.get("freshbooks_tax_1", None)
    quote_price = request.data.get("quote_price", None)
    print("fb_tax_id: ", freshbooks_tax_id)
    print("quote_price:", quote_price)
    try:
        if freshbooks_tax_id:
            get_valid_tax = freshbooks_svc.get_freshbooks_tax(freshbooks_tax_id)
            if not get_valid_tax.get("taxid"):
                return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})

    company = get_company_from_request(request)
    if not company:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
    customerproduct = CustomerProduct.objects.filter(company=company, pk=pk).first()
    if not customerproduct:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "CustomerProduct not found"})
    customerproduct.freshbooks_tax_1 = freshbooks_tax_id
    customerproduct.quote_price = quote_price
    customerproduct.save()
    customerproduct_serializer = CustomerProductListDetailSerializer(customerproduct)
    return Response(status=status.HTTP_200_OK, data=customerproduct_serializer.data)


@api_view(["GET"])
def invoice_detail(request, pk):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        invoice = get_object_or_404_with_company(Invoice, company, pk=pk)
        invoice_serializer = InvoiceDetailSerializer(invoice)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def invoice_list(request):
    company = get_company_from_request(request)
    if not company:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
    filter_customer_id = request.GET.get("customer_id")
    filter_invoice_year = request.GET.get("year")
    invoices = Invoice.objects.filter(company=company).select_related("customer")
    try:
        if filter_invoice_year:
            invoices = invoices.filter(date_generated__year=filter_invoice_year)
        if filter_customer_id:
            invoices = invoices.filter(customer__pk=filter_customer_id)
        invoice_serializer = InvoiceListSerializer(list(invoices), many=True, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    except ValueError:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": "Unable to filter invoice year"},
        )
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})


@api_view(["GET"])
def get_available_invoice_years_filter(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        available_years = Invoice.objects.filter(company=company).dates("date_generated", "year", order="DESC")
        years = [dt.year for dt in available_years]
        return Response(status=status.HTTP_200_OK, data=years)
    return Response(
        status=status.HTTP_400_BAD_REQUEST,
        data={"error": "Unable to get invoice years"},
    )


@api_view(["DELETE"])
def hard_delete_invoice(request, pk):
    if request.method == "DELETE":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        delete_invoice = (
            Invoice.objects.filter(company=company, pk=pk)
            .prefetch_related("orderitem_set", "orderitem_set__route")
            .first()
        )
        if not delete_invoice:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Invoice not found"})
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


@api_view(["POST"])
@freshbooks_access
def create_invoice(request, freshbooks_svc):
    if request.method == "POST":
        customer_id = request.data.get("customer_id")
        create_date = request.data.get("create_date")
        orderitems_id = request.data.get("orderitems_id")
        invoice_number = request.data.get("invoice_number")
        po_number = request.data.get("po_number")
        minus = request.data.get("discount")
        minus_description = request.data.get("discount_description")

        print(customer_id, create_date, orderitems_id, invoice_number, po_number)

        try:
            company = get_company_from_request(request)
            if not company:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
            invoice_customer = Customer.objects.filter(company=company, pk=customer_id).first()
            if not invoice_customer:
                return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Customer not found"})
            invoice_orderitems = OrderItem.objects.filter(company=company, pk__in=orderitems_id)
            parsed_create_date = datetime.strptime(create_date, "%Y-%m-%d")
            minus_decimal = Decimal(minus) if minus > 0 else Decimal(0)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)

        if len(invoice_orderitems) == 0:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "No orderitems found for invoice creation"},
            )

        if not OrderItem.check_orderitem_consistent_pricing(invoice_orderitems):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "Orderitems unit pricing is not consistent"},
            )

        print(invoice_customer, invoice_orderitems, parsed_create_date)

        freshbooks_taxes = freshbooks_svc.get_freshbooks_taxes()

        freshbooks_tax_lookup = {
            tax.get("id"): {"name": tax.get("name"), "amount": tax.get("amount")} for tax in freshbooks_taxes
        }

        create_invoice_kwargs = {
            "invoice_number": invoice_number,
            "po_number": po_number,
            "minus_decimal": minus_decimal,
            "minus_description": minus_description,
        }

        print("freshbooks_tax_lookup: ", freshbooks_tax_lookup)
        create_invoice_kwargs = {
            "invoice_number": invoice_number,
            "po_number": po_number,
            "minus_decimal": minus_decimal,
            "minus_description": minus_description,
        }

        # . create the ask on huey, get the task id
        freshbooks_client_id = invoice_customer.freshbooks_client_id

        freshbooks_invoice_body = OrderItem.build_freshbooks_invoice_body(
            invoice_orderitems,
            freshbooks_client_id,
            invoice_number,
            po_number,
            parsed_create_date,
            freshbooks_tax_lookup,
        )

        invoice = freshbooks_svc.create_freshbooks_invoice(freshbooks_invoice_body)

        invoice_number = invoice.get("invoice_number")
        freshbooks_account_id = invoice.get("accounting_systemid")
        freshbooks_invoice_id = invoice.get("id")

        create_invoice_kwargs = {
            "invoice_number": invoice_number,
            "po_number": po_number,
            "minus_decimal": minus_decimal,
            "minus_description": minus_description,
        }

        new_invoice = Invoice.create_local_invoice(
            company,
            invoice_orderitems,
            invoice_customer,
            parsed_create_date,
            freshbooks_account_id,
            freshbooks_invoice_id,
            **create_invoice_kwargs,
        )
        return Response(
            data=InvoiceDetailSerializer(new_invoice).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)


@api_view(["DELETE"])
def customerproduct_delete(request, pk):
    if request.method == "DELETE":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customerproduct = get_object_or_404_with_company(CustomerProduct, company, id=pk)
        orderitems = OrderItem.objects.filter(company=company, customerproduct_id=customerproduct.pk)
        print("orderitems: ", orderitems)
        if len(orderitems) == 0:
            customerproduct.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Customerproduct has references to it"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            # Dont implement soft delete for now
            # customerproduct.end_date = date.today()
            # customerproduct.save()
            # customerproduct_serializer = CustomerProductListDetailSerializer(instance=customerproduct)
            # return Response(customerproduct_serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all_quotes(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customer_id = request.GET.get("customer_id", None)
        customerproducts = CustomerProduct.objects.filter(company=company).select_related("customer", "product")
        if customer_id:
            customerproducts = CustomerProduct.objects.filter(company=company, customer_id=customer_id)
        customerproduct_serializer = CustomerProductListDetailSerializer(customerproducts, many=True)
        return Response(status=status.HTTP_200_OK, data=customerproduct_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@freshbooks_access
def get_all_taxes(request, freshbooks_svc):
    if request.method == "GET":
        taxes_arr = freshbooks_svc.get_freshbooks_taxes()
        return Response(status=status.HTTP_200_OK, data=taxes_arr)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def bulk_import_orders(request):
    if request.method == "POST":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})

        dataArr = request.data
        #  TODO: use a serializer to save model object instead
        error_rows = []
        for row in dataArr:
            customer_id = row.get("selectedCustomer").get("id")
            customerproduct_id = row.get("selectedProduct").get("id")
            quantity = row.get("quantity")
            date = row.get("date")
            do_number = row.get("do_number") or str(round(time.time() * 1000))
            po_number = row.get("po_number")

            customer_exists = Customer.objects.filter(company=company, id=customer_id).first()
            customerproduct_exists = CustomerProduct.objects.filter(company=company, id=customerproduct_id).first()
            route_exists = Route.objects.filter(company=company, do_number=do_number, date=date)

            if customer_exists and customerproduct_exists:
                if len(route_exists) > 0:
                    route = route_exists[0]
                    new_orderitem = OrderItem(
                        company=company,
                        quantity=quantity,
                        driver_quantity=quantity,
                        note=po_number,
                        unit_price=customerproduct_exists.quote_price,
                        customerproduct=customerproduct_exists,
                        route=route,
                    )
                    new_orderitem.save()
                else:
                    route = Route(company=company, do_number=do_number, date=date)
                    route.save()
                    new_orderitem = OrderItem(
                        company=company,
                        quantity=quantity,
                        driver_quantity=quantity,
                        note=po_number,
                        unit_price=customerproduct_exists.quote_price,
                        customerproduct=customerproduct_exists,
                        route=route,
                    )
                    new_orderitem.save()
            else:
                error_rows.append(row)

        if len(error_rows) > 0:
            return Response(status=status.HTTP_200_OK, data=error_rows)
        return Response(status=status.HTTP_201_CREATED, data=request.data)


@api_view(["GET"])
def get_filter_orderitem_rows(request):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        customer_ids = request.GET.get("customer_ids")

        parsed_start_date = None
        parsed_end_date = None
        parsed_customer_ids = None

        try:
            if start_date:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")

            if end_date:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")

            if customer_ids:
                parsed_customer_ids = [x for x in customer_ids.split(";") if x != ""]

        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        orderitem_qset = OrderItem.objects.filter(company=company).select_related(
            "route",
            "customerproduct",
            "customerproduct__customer",
            "customerproduct__product",
        )

        if parsed_start_date:
            orderitem_qset = orderitem_qset.filter(route__date__gte=parsed_start_date)
        if parsed_end_date:
            orderitem_qset = orderitem_qset.filter(route__date__lte=parsed_end_date)
        if parsed_customer_ids:
            orderitem_qset = orderitem_qset.filter(customerproduct__customer_id__in=parsed_customer_ids)

        orderitem_qset = orderitem_qset.filter(invoice__isnull=True)
        rows = list(orderitem_qset)
        orderitem_serializer = OrderItemSerializer(rows, many=True)
        return Response(status=status.HTTP_200_OK, data=orderitem_serializer.data)


@api_view(["GET"])
@freshbooks_access
def get_freshbooks_products(request, freshbooks_svc):
    item_arr = freshbooks_svc.update_freshbooks_products()
    company = get_company_from_request(request)
    if not company:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})

    for item in item_arr:
        item_name = item.get("name")
        item_unit_price = item.get("unit_cost").get("amount")
        item_id = item.get("id")
        item_accounting_systemid = item.get("accounting_systemid")

        # This is a sync operation, need to handle all companies
        item_queryset = Product.objects.filter(
            company=company, freshbooks_item_id=item_id, freshbooks_account_id=item_accounting_systemid
        )
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
                company=company,
                name=item_name,
                unit_price=item_unit_price,
                freshbooks_item_id=item_id,
                freshbooks_account_id=item_accounting_systemid,
            )
            new_item.save()
    return Response(status=status.HTTP_200_OK, data=item_arr)


@api_view(["GET"])
@freshbooks_access
def get_freshbooks_import_clients(request, freshbooks_svc):
    company = get_company_from_request(request)
    if not company:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
    # This is a sync operation, need to handle all companies
    existing_freshbooks_clients = Customer.objects.filter(
        company=company, freshbooks_account_id__isnull=False, freshbooks_client_id__isnull=False
    )
    existing_client_ids = [client.freshbooks_client_id for client in existing_freshbooks_clients]
    freshbooks_clients = freshbooks_svc.get_freshbooks_clients()
    not_exists_freshbooks_client = []
    for client in freshbooks_clients:
        if str(client.get("id")) not in existing_client_ids:
            not_exists_freshbooks_client.append(client)
    return Response(status=status.HTTP_200_OK, data=not_exists_freshbooks_client)


@api_view(["POST"])
@freshbooks_access
def import_freshbooks_clients(request, freshbooks_svc):
    if request.method == "POST":
        import_client_ids = request.data.get("freshbooks_id_list")
        valid_import_client_ids = []
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        for import_client_id in import_client_ids:
            valid_client = freshbooks_svc.get_freshbooks_client(import_client_id)
            print(valid_client)
            res = valid_client.get("response").get("result").get("client")
            if res.get("id"):
                valid_import_client_ids.append(res)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, data=import_client_ids)
        Customer.import_freshbooks_clients(company, valid_import_client_ids)
        return Response(status=status.HTTP_201_CREATED, data=import_client_ids)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@freshbooks_access
def get_freshbooks_import_products(request, freshbooks_svc):
    if request.method == "GET":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        # This is a sync operation, need to handle all companies
        existing_freshbooks_products = Product.objects.filter(
            company=company, freshbooks_account_id__isnull=False, freshbooks_item_id__isnull=False
        )
        existing_product_ids = [product.freshbooks_item_id for product in existing_freshbooks_products]
        freshbooks_products = freshbooks_svc.get_freshbooks_products()

        not_exists_freshbooks_products = []
        for product in freshbooks_products:
            if str(product.get("id")) not in existing_product_ids:
                not_exists_freshbooks_products.append(product)
        return Response(status=status.HTTP_200_OK, data=not_exists_freshbooks_products)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@freshbooks_access
def import_freshbooks_products(request, freshbooks_svc):
    if request.method == "POST":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        import_product_ids = request.data.get("freshbooks_id_list")
        valid_import_product_list = []
        for import_product_id in import_product_ids:
            valid_product = freshbooks_svc.freshbooks_product_detail(import_product_id)
            print(valid_product)
            res = valid_product.get("response").get("result").get("item")
            if res.get("id"):
                valid_import_product_list.append(res)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND, data=import_product_ids)
        print(valid_import_product_list)
        Product.freshbooks_import_products(company, valid_import_product_list)
        return Response(status=status.HTTP_201_CREATED, data=valid_import_product_list)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@freshbooks_access
def get_freshbooks_clients(request, freshbooks_svc):
    freshbooks_clients = freshbooks_svc.get_freshbooks_clients()
    return Response(status=status.HTTP_200_OK, data=freshbooks_clients)


@api_view(["PUT"])
@freshbooks_access
def link_customer(request, freshbooks_svc):
    if request.method == "PUT":
        customer_id = request.data.get("customer_id")
        freshbooks_client_id = request.data.get("freshbooks_client_id", None)
        pivot_invoice = request.data.get("pivot_invoice", False)
        gst = request.data.get("gst", 0)
        download_prefix = request.data.get("download_prefix", None)
        download_suffix = request.data.get("download_suffix", None)
        to_fax = request.data.get("to_fax", False)
        to_email = request.data.get("to_email", False)
        to_print = request.data.get("to_print", False)
        to_whatsapp = request.data.get("to_whatsapp", False)
        freshbooks_client = None
        if not customer_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        customer_obj = Customer.objects.filter(company=company, pk=customer_id).first()
        if not customer_obj:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Customer not found"})
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
            freshbooks_client = response.get("response").get("result").get("client")
        if freshbooks_client_id and freshbooks_client:
            customer_obj.freshbooks_client_id = str(freshbooks_client.get("id"))
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


@api_view(["PUT"])
@freshbooks_access
def link_product(request, freshbooks_svc):
    if request.method == "PUT":
        product_id = request.data.get("product_id")
        freshbooks_item_id = request.data.get("freshbooks_item_id", None)
        freshbooks_product = None
        if not product_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        product_obj = Product.objects.filter(company=company, pk=product_id).first()
        if not product_obj:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Product not found"})
        if not product_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if freshbooks_item_id:
            response = freshbooks_svc.freshbooks_product_detail(freshbooks_item_id)
            freshbooks_product = response.get("response").get("result").get("item")
        if freshbooks_item_id and freshbooks_product:
            product_obj.freshbooks_item_id = str(freshbooks_product.get("id"))
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


@api_view(["DELETE"])
def orderitem_delete(request, pk):
    if request.method == "DELETE":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        orderitem = OrderItem.objects.filter(company=company, id=pk).select_related("route").first()
        if not orderitem:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "OrderItem not found"})
        route = orderitem.route
        if orderitem:
            orderitem.delete()
            if route.orderitem_set.count() == 0:
                route.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@freshbooks_access
def customer_sync(request, freshbooks_svc):
    if request.method == "POST":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        try:
            freshbooks_svc.update_freshbooks_clients(company)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})
        customers = Customer.objects.filter(company=company).prefetch_related(
            "customergroup_set", "customergroup_set__group"
        )
        customer_serializer = CustomerListDetailUpdateSerializer(customers, many=True)
        return Response(status=status.HTTP_200_OK, data=customer_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@freshbooks_access
def invoice_sync(request, freshbooks_svc):
    if request.method == "POST":
        company = get_company_from_request(request)
        if not company:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
        sync_invoices = Invoice.objects.filter(company=company)
        for invoice in sync_invoices:
            freshbooks_invoice_search = freshbooks_svc.search_freshbooks_invoices(invoice.invoice_number)
            if len(freshbooks_invoice_search) > 0:
                freshbooks_invoice = freshbooks_invoice_search[0]
                invoice.po_number = freshbooks_invoice.get("po_number")
                invoice.date_created = freshbooks_invoice.get("create_date")
                invoice.freshbooks_account_id = freshbooks_invoice.get("accounting_systemid")
                invoice.freshbooks_invoice_id = freshbooks_invoice.get("invoiceid")
                invoice.save()
        invoice_serializer = InvoiceListSerializer(sync_invoices, context={"request": request}, many=True)
        return Response(status=status.HTTP_200_OK, data=invoice_serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@freshbooks_access
def invoice_update(request, freshbooks_svc, pk):
    if request.method == "PUT":
        #  list of ints
        orderitems_id = request.data.get("orderitems_id")
        invoice_number = request.data.get("invoice_number")
        po_number = request.data.get("po_number")
        minus = request.data.get("discount")
        minus_description = request.data.get("discount_description")

        print(orderitems_id, invoice_number, po_number)

        try:
            company = get_company_from_request(request)
            if not company:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
            existing_invoice = Invoice.objects.filter(company=company, pk=pk).prefetch_related("orderitem_set").first()
            if not existing_invoice:
                return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Invoice not found"})
            minus_decimal = Decimal(minus)
        except Exception as e:
            print(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)

        invoice_lines = []

        #  list of ints

        print("Selected ID: ", orderitems_id)

        orderitem_set_existing_invoice = OrderItem.objects.filter(company=company, pk__in=orderitems_id)

        price_map = {}
        for oi in orderitem_set_existing_invoice:
            product_name = oi.customerproduct.product.name
            if not price_map.get(product_name):
                price_map[product_name] = oi.unit_price
            if price_map[product_name] != oi.unit_price:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "Orderitems unit pricing is inconsistent"},
                )

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
                    datetime.strftime(orderitem.route.date, "%d-%m-%Y"),
                    orderitem.route.do_number,
                )

                if orderitem.note:
                    description += "P/O: {0}".format(orderitem.note)

                invoice_line = {
                    "type": 0,
                    "description": description,
                    "taxName1": tax.get("name"),
                    "taxAmount1": tax.get("amount"),
                    "name": orderitem.customerproduct.product.name,
                    "qty": orderitem.driver_quantity,
                    "unit_cost": {"amount": str(orderitem.unit_price)},
                }

                invoice_lines.append(invoice_line)
            else:
                description = "DATE: {0} D/O: {1} ".format(
                    datetime.strftime(orderitem.route.date, "%d-%m-%Y"),
                    orderitem.route.do_number,
                )

                if orderitem.note:
                    description += "P/O: {0}".format(orderitem.note)

                invoice_line = {
                    "type": 0,
                    "description": description,
                    "name": orderitem.customerproduct.product.name,
                    "qty": orderitem.driver_quantity,
                    "unit_cost": {"amount": str(orderitem.unit_price)},
                }
                invoice_lines.append(invoice_line)

        net_total = 0
        for orderitem in existing_invoice.orderitem_set.all():
            net_total += orderitem.driver_quantity * orderitem.unit_price

        body = {
            "invoice": {
                "invoice_number": invoice_number,
                "po_number": po_number,
                "lines": [line for line in invoice_lines],
            }
        }

        gst_decimal = Decimal(existing_invoice.gst / 100)
        net_total -= minus_decimal
        net_gst = (net_total * gst_decimal).quantize(Decimal(".0001"), rounding=ROUND_UP)
        total_incl_gst = (net_total + net_gst).quantize(Decimal(".0001"), rounding=ROUND_UP)

        #  update invoice
        print(json.dumps(body))

        freshbooks_updated_invoice = freshbooks_svc.update_freshbooks_invoice(
            existing_invoice.freshbooks_invoice_id, body
        )

        invoice_number = freshbooks_updated_invoice.get("invoice_number")
        date_created = freshbooks_updated_invoice.get("create_date")
        freshbooks_account_id = freshbooks_updated_invoice.get("accounting_systemid")
        freshbooks_invoice_id = freshbooks_updated_invoice.get("id")

        existing_invoice.company = company
        existing_invoice.date_created = None
        existing_invoice.po_number = po_number
        existing_invoice.net_total = net_total
        existing_invoice.gst = existing_invoice.gst
        existing_invoice.net_gst = net_gst
        existing_invoice.total_incl_gst = total_incl_gst
        existing_invoice.invoice_number = invoice_number
        existing_invoice.minus = minus_decimal
        existing_invoice.discount_description = minus_description
        existing_invoice.huey_task_id = None
        existing_invoice.freshbooks_invoice_id = freshbooks_invoice_id
        existing_invoice.freshbooks_account_id = freshbooks_account_id
        existing_invoice.invoice_number = invoice_number
        existing_invoice.date_created = date_created
        existing_invoice.save(
            update_fields=[
                "company",
                "date_created",
                "po_number",
                "net_total",
                "gst",
                "net_gst",
                "total_incl_gst",
                "invoice_number",
                "minus",
                "discount_description",
                "huey_task_id",
                "freshbooks_invoice_id",
                "freshbooks_account_id",
                "invoice_number",
                "date_created",
            ]
        )

        return Response(
            data=InvoiceDetailSerializer(existing_invoice).data,
            status=status.HTTP_200_OK,
        )
    return Response(status=status.HTTP_400_BAD_REQUEST, data=request.data)


@api_view(["GET"])
@freshbooks_access
def invoice_start_download(request, freshbooks_svc):
    """
    Start the download of a invoice by invoice number or pk.
    Huey task will be created to prepare to download the invoice.
    Huey task id will be returned to the client.
    """

    def valid_invoice_number(invoice_number_from, invoice_number_to):
        if invoice_number_from and invoice_number_to:
            if invoice_number_to > invoice_number_from:
                return True
        return False

    invoice_number_from = request.GET.get("from", None)
    invoice_number_to = request.GET.get("to", None)

    if not valid_invoice_number(invoice_number_from, invoice_number_to):
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": "Invoice number (to and from) must be provided and 'to' must be greater than 'from'."},
        )

    company = get_company_from_request(request)
    if not company:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Company not found"})
    huey_download_task = huey_download_invoice_main_task(invoice_number_from, invoice_number_to, request.user, company)
    status_url = request.build_absolute_uri(
        reverse("pos:invoice_download_status") + f"?task_id={huey_download_task.id}&filename={invoice_number_to}.pdf"
    )
    return Response(status=status.HTTP_202_ACCEPTED, data={"status": "pending", "status_url": status_url})


@api_view(["GET"])
def invoice_download_status(request):
    """
    Check the status of the invoice download task.
    """
    task_id = request.GET.get("task_id", None)
    filename = request.GET.get("filename", "download")
    if not task_id:
        return Response(
            {"status": "error", "message": "Task ID must be provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    huey = settings.HUEY
    task_result = huey.get(task_id, peek=True)
    try:
        if task_result:
            url = reverse("pos:download_invoice_zip", kwargs={"huey_task_id": task_id})
            return Response(
                {
                    "status": "completed",
                    "zip_url": request.build_absolute_uri(f"{url}?filename={filename}"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": "pending", "zip_url": None},
                status=status.HTTP_202_ACCEPTED,
            )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
