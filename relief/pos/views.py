from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, FormView, DeleteView, DetailView
from .models import Customer, Product, Trip, CustomerProduct, Route, OrderItem, Invoice, Company
from .forms import CustomerForm, ProductForm, TripForm, TripDetailForm, CustomerProductCreateForm, \
    CustomerProductUpdateForm, OrderItemFormSet, RouteForm, \
    InvoiceDateRangeForm, InvoiceOrderItemForm, InvoiceAddOrderForm, InvoiceForm, RouteArrangementFormSet
from django.db.models import Max
from datetime import datetime, date, timedelta
from collections import defaultdict
from decimal import Decimal


# Create your views here.

class CustomerIndexView(ListView):
    template_name = 'pos/customer/index.html'
    context_object_name = 'customer_list'

    def get_queryset(self):
        return Customer.objects.all()


class ProductIndexView(ListView):
    template_name = 'pos/product/index.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        return Product.objects.all()


class TripIndexView(ListView):
    template_name = 'pos/trip/index.html'
    context_object_name = 'trip_list'

    def get_queryset(self):
        return Trip.objects.all().order_by('-date')


class CustomerProductListView(ListView):
    template_name = 'pos/customerproduct/index.html'
    context_object_name = 'customerproduct_list'

    def get_queryset(self):
        customer = self.kwargs['pk']
        return CustomerProduct.objects.filter(customer_id=customer)

    def get_context_data(self, **kwargs):
        context = super(CustomerProductListView, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, pk=self.kwargs['pk'])
        context['customer'] = customer
        return context


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'pos/customer/detail.html'


class CustomerRouteView(ListView):
    template_name = 'pos/route/customer_routes.html'
    context_object_name = 'route_list'

    def get_queryset(self):
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        route_list = Route.get_customer_routes(customer.id)
        return route_list

    def get_context_data(self, **kwargs):
        context = super(CustomerRouteView, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        context['customer'] = customer
        return context





class TripCopyView(FormView):
    template_name = 'pos/trip/copy.html'
    form_class = TripForm

    def get_context_data(self, **kwargs):
        trip_pk = self.kwargs.get('pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        context = super(TripCopyView, self).get_context_data(**kwargs)
        context['trip'] = trip
        return context

    def get_initial(self):
        trip = Trip.objects.get(pk=self.kwargs['pk'])
        initial = super(TripCopyView, self).get_initial()
        initial['date'] = trip.date
        initial['notes'] = trip.notes
        initial['packaging'] = trip.packaging_methods
        return initial

    def form_valid(self, form):
        new_trip = Trip.objects.create(
            date=form.cleaned_data['date'],
            notes=form.cleaned_data['notes'],
            packaging_methods=form.cleaned_data['packaging']
        )
        new_trip.save()
        trip_copy = self.kwargs.get('pk')
        if trip_copy:
            trip = get_object_or_404(Trip, pk=trip_copy)
            for r in trip.route_set.all():
                orderitems = [OrderItem(quantity=oi.quantity,
                                        driver_quantity=0,
                                        note=oi.note,
                                        customerproduct=oi.customerproduct,
                                        packing=oi.packing) for oi in r.orderitem_set.all()]
                r.pk = None
                r.do_number = ""
                r.invoice = None
                r.trip = new_trip
                r.save()
                for oi in orderitems:
                    oi.route = r
                    oi.pk = None
                    oi.save()
        return HttpResponseRedirect(reverse('pos:trip_index'))

    def get_success_url(self):
        return reverse('pos:trip_index')


class TripDetailView(FormView):
    model = Trip
    template_name = 'pos/trip/detail.html'
    form_class = TripDetailForm

    def get_context_data(self, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs['pk'])
        routes = Route.objects.filter(trip_id=trip.pk).order_by('index')
        packing = trip.packaging_methods.split(',')
        # sum = Trip.get_packing_sum(trip.pk)
        context = super(TripDetailView, self).get_context_data(**kwargs)
        context['trip'] = trip
        context['routes'] = routes
        context['customers'] = Customer.objects.all()
        context['packing'] = packing
        # context['sum'] = sum
        # print(sum)
        return context

    def get_success_url(self):
        return reverse('pos:trip_detail', kwargs={'pk':self.kwargs['pk']})


def print_trip_detail(request, pk):
    template_name = 'pos/trip/print_detail.html'
    trip = get_object_or_404(Trip, pk=pk)
    routes = trip.route_set.all().order_by('index')
    [r.orderitem_set.all() for r in routes]
    packing = []
    if trip.packaging_methods:
        packing = [key for key in trip.packaging_methods.split(',')]
    packing_sum_ddict = defaultdict(int)

    for r in routes:
        for oi in r.orderitem_set.all():
            if oi.packing:
                for method, value in oi.packing.items():
                    if oi.packing.get(method):
                        packing_sum_ddict[method] += value

    packing_sum = {k: v for k, v in packing_sum_ddict.items()}

    context = {}
    context['trip'] = trip
    context['routes'] = routes
    context['packing'] = packing
    context['packing_sum'] = packing_sum
    return render(request, template_name, context)


class TripDeleteView(DeleteView):
    template_name = 'pos/trip/trip_confirm_delete.html'
    model = Trip

    def get_object(self, queryset=None):
        return Trip.objects.get(pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse('pos:trip_index')


def TripArrangementView(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    template_name = 'pos/trip/arrange.html'
    packing = []
    if trip.packaging_methods:
        packing = [key for key in trip.packaging_methods.split(',')]
    packing_sum_ddict = defaultdict(int)
    route_arrange = trip.route_set.all().order_by('index')

    for r in route_arrange:
        for oi in r.orderitem_set.all():
            if oi.packing:
                for method, value in oi.packing.items():
                    if oi.packing.get(method):
                        packing_sum_ddict[method] += value

    packing_sum = {k: v for k, v in packing_sum_ddict.items()}

    context = {'trip': trip,
               'packing': packing,
               'packing_sum': packing_sum,
               'errors': []}

    if request.method == 'POST':
        arrange_formset = RouteArrangementFormSet(request.POST)
        context['arrange_formset'] = arrange_formset
        if arrange_formset.is_valid():
            order_index = [r.cleaned_data['index'] for r in arrange_formset.forms]
            index_range = [i+1 for i in range(len(arrange_formset))]
            valid_range = all(elem in order_index for elem in index_range)
            if not valid_range:
                context['errors'].append("Numbering not in sequence.")
                return render(request, template_name, context)

            arrange_formset.save()
            return HttpResponseRedirect(reverse('pos:trip_detail', kwargs={'pk': pk}))

        return render(request, template_name, context)

    arrange_formset = RouteArrangementFormSet(queryset=route_arrange)
    context['arrange_formset'] = arrange_formset
    return render(request, template_name, context)


class RouteEditView(UpdateView):
    model = Route
    template_name = 'pos/route/edit.html'
    form_class = RouteForm

    def get_context_data(self, **kwargs):
        route = get_object_or_404(Route, pk=self.kwargs['pk'])
        packing = []
        if route.trip.packaging_methods:
            packing = [key for key in route.trip.packaging_methods.split(',')]
        oi_formset = OrderItemFormSet(instance=route, form_kwargs={'packing': packing})
        #  Read JSON and output to packing table.
        context = super().get_context_data(**kwargs)
        context['route'] = route
        context['orderitems'] = oi_formset
        context['packing'] = packing
        return context

    def form_valid(self, form):
        route = get_object_or_404(Route, pk=self.kwargs['pk'])
        packing = []
        if route.trip.packaging_methods:
            packing = [key for key in route.trip.packaging_methods.split(',')]
        oi_formset = OrderItemFormSet(self.request.POST, instance=route, form_kwargs={'packing': packing})
        if oi_formset.is_valid() and form.is_valid():
            for oi_form in oi_formset:
                oi_form.save(packing)
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        route = get_object_or_404(Route, pk=self.kwargs['pk'])
        return reverse('pos:trip_detail', kwargs={'pk':route.trip.id})


class RouteDeleteView(DeleteView):
    model = Route
    template_name = 'pos/route/route_confirm_delete.html'

    def get_object(self, queryset=None):
        route = get_object_or_404(Route, pk=self.kwargs['route_pk'])
        return route

    def delete(self, request, *args, **kwargs):
        trip_id = self.get_object().trip.pk
        super(RouteDeleteView, self).delete(request, args, kwargs)
        Trip.rearrange_trip_routes_after_delete(trip_id)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('pos:trip_detail', kwargs={'pk':self.kwargs['trip_pk']})


def InvoiceDateRangeView(request, pk):
    template_name = 'pos/invoice/invoice_select_order.html'

    if request.method == 'GET':
        customer = get_object_or_404(Customer, id=pk)
        date_start_string = request.GET.get('date_start', '')
        date_end_string = request.GET.get('date_end', '')

        if date_start_string and date_end_string:
            date_form = InvoiceDateRangeForm(request.GET)
            date_start = datetime.strptime(date_start_string, "%d/%m/%Y")
            date_end = datetime.strptime(date_end_string, "%d/%m/%Y")
            #  date_start will start from exactly midnight by default
            #  date_end will have to add timedelta because it will also end at exactly at midnight,
            #  causing the last route order to not be included.
            date_end += timedelta(hours=23, minutes=59, seconds=59)
            date_end_formatted = datetime.strftime(date_end,'%Y-%m-%d %H:%M:%S')
            date_start_formatted = datetime.strftime(date_start, '%Y-%m-%d %H:%M:%S')
            request.session['date_start'] = date_start_formatted
            request.session['date_end'] = date_end_formatted

            route_list = Route.get_customer_routes_orderitems_by_date(date_start_formatted,
                                                                      date_end_formatted,
                                                                      customer.id)

            customerproducts = CustomerProduct.objects.filter(customer_id=customer.id)

            routes_display = []
            for route in route_list:
                row = {}
                row['date'] = route.trip.date
                row['id'] = route.id
                for oi in route.orderitem_set.all():
                    row[oi.customerproduct.id] = oi.quantity
                routes_display.append(row)
            return render(request, template_name, {'date_form': date_form,
                                                   'customer': customer,
                                                   'routes': routes_display,
                                                   'customerproducts': customerproducts })
        else:
            date_form = InvoiceDateRangeForm()
            return render(request, template_name, {'date_form': date_form,
                                                   'customer': customer })



    if request.method == 'POST':
        selected = request.POST.getlist('routes')
        request.session['route_select'] = selected
        return HttpResponseRedirect(reverse('pos:invoice_orderassign', kwargs={'pk':pk}))


def InvoiceOrderAssignView(request, pk):
    template_name = 'pos/invoice/invoice_assign.html'
    req_post = request.POST.copy()
    customer = get_object_or_404(Customer, id=pk)
    customerproducts = CustomerProduct.objects.filter(customer_id=pk)
    trip_start = request.session['date_start']
    trip_end = request.session['date_end']
    parse_trip_start = datetime.strptime(trip_start, '%Y-%m-%d %H:%M:%S')
    parse_trip_end = datetime.strptime(trip_end, '%Y-%m-%d %H:%M:%S')
    trip_start_formatted = datetime.strftime(parse_trip_start, '%d/%m/%Y')
    trip_end_formatted = datetime.strftime(parse_trip_end, '%d/%m/%Y')

    trips = Trip.objects.filter(date__lte=parse_trip_end, date__gte=parse_trip_start).order_by('date')
    rows_list = []
    all_valid = True
    if request.method == 'POST':
        add_form = InvoiceAddOrderForm(req_post,
                                       trips=trips,
                                       customerproducts=customerproducts)

        if req_post.get('add_btn'):
            all_valid = False
            if add_form.is_valid():
                do_number = add_form.cleaned_data['do_number']
                trip_id = add_form.cleaned_data['date']
                trip = get_object_or_404(Trip, id=trip_id)
                route_index_max = trip.route_set.all().aggregate(Max('index'))
                if route_index_max.get('index__max') is None:
                    route_index_max['index__max'] = 0
                route = Route(index=route_index_max.get('index__max') + 1, do_number=do_number, trip_id=trip.pk)
                route.save()
                request.session['route_select'].append(route.pk)
                # Append operations does not get saved to the object if this modified flag is not set.
                # https://code.djangoproject.com/wiki/NewbieMistakes#Appendingtoalistinsessiondoesntwork
                # See "Appending to a list in session doesn't work section
                request.session.modified = True
                additional_order_fields = {}
                for cp in customerproducts:
                    orderitem_quantity = add_form.cleaned_data[cp.product.name]
                    if orderitem_quantity is None:
                        orderitem_quantity = 0
                    orderitem = OrderItem(quantity=orderitem_quantity,
                                          customerproduct=cp,
                                          route=route)
                    orderitem.save()
                    additional_order_fields[cp.product.name] = orderitem_quantity


                additional_order = InvoiceOrderItemForm(prefix=str(route.pk),
                                                        orderitems=route.orderitem_set.all(),
                                                        do_number=route.do_number)
                for k,v in additional_order_fields.items():
                    additional_order.fields[k] = v
                additional_order.fields['do_number'] = route.do_number
                for k,v in additional_order.fields.items():
                    req_post[additional_order.prefix + '-' + k] = v
                add_form = InvoiceAddOrderForm(trips=trips, customerproducts=customerproducts)

        routes = request.session['route_select']


        for r in routes:
            row = {}
            route = get_object_or_404(Route, id=r)
            route_orderitems = list(route.orderitem_set.all())
            form = InvoiceOrderItemForm(req_post,
                                        prefix=str(route.id),
                                        orderitems=route_orderitems,
                                        do_number=route.do_number)
            row['date'] = route.trip.date
            row['form'] = form
            rows_list.append(row)
            if form.is_valid():
                route.do_number = form.cleaned_data['do_number']
                for oi in route_orderitems:
                    oi_driver_quantity = form.cleaned_data[oi.customerproduct.product.name]
                    oi.driver_quantity = oi_driver_quantity
                    oi.save()
                route.save()
            else:
                all_valid = False

        if all_valid:
            invoice_year = datetime.now().year
            invoice_number = Invoice.get_next_invoice_number()
            invoice_pk = Invoice.generate_invoice(customer.gst,
                                                  trip_start_formatted,
                                                  trip_end_formatted,
                                                  invoice_year,
                                                  invoice_number,
                                                  routes)
            return HttpResponseRedirect(reverse('pos:invoice_view', kwargs={'pk': invoice_pk}))
        else:
            return render(request, template_name, {'rows_list': rows_list,
                                                   'customer': customer,
                                                   'customerproducts': customerproducts,
                                                   'add_order':add_form })


    if request.method == 'GET':
        routes = request.session['route_select']
        add_order_form = InvoiceAddOrderForm(trips=trips, customerproducts=customerproducts)
        assign_routes = Route.objects.filter(id__in=routes)
        for r in assign_routes:
            row = {}
            form = InvoiceOrderItemForm(prefix=str(r.id),
                                        orderitems=list(r.orderitem_set.all()),
                                        do_number=r.do_number)
            row['date'] = r.trip.date
            row['form'] = form
            rows_list.append(row)
        return render(request, template_name, {'rows_list': rows_list,
                                               'customer': customer,
                                               'customerproducts': customerproducts,
                                               'add_order':add_order_form })


class InvoiceHistoryView(ListView):
    template_name = 'pos/invoice/invoice_history.html'
    context_object_name = 'invoice_list'

    def get_queryset(self):
        return Invoice.objects.all()


def InvoiceSingleView(request, pk):
    template_name = 'pos/invoice/invoice_single_view.html'
    if request.GET.get('print'):
        template_name = 'pos/invoice/invoice_single_view_print.html'

    invoice_id = pk
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice_form = InvoiceForm(instance=invoice)

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, instance=invoice)
        if invoice_form.is_valid():
            minus = invoice_form.cleaned_data.get('minus')
            remark = invoice_form.cleaned_data.get('remark')
            invoice_year = invoice_form.cleaned_data.get('invoice_year')
            invoice_number = invoice_form.cleaned_data.get('invoice_number')

            gst = Decimal(invoice_form.instance.gst/100)
            original_total = Decimal(invoice.original_total)
            net_total = Decimal(original_total - minus)
            net_gst = Decimal(gst * net_total)
            total_incl_gst = Decimal(net_total + net_gst)

            invoice.remark = remark
            invoice.original_total = original_total
            invoice.net_total = net_total
            invoice.net_gst = net_gst
            invoice.total_incl_gst = total_incl_gst
            invoice.invoice_year = invoice_year
            invoice.invoice_number = invoice_number
            invoice.save()
            return HttpResponseRedirect(request.path_info)

    company_info = get_object_or_404(Company, id=1)
    routes = invoice.route_set.all().order_by('trip__date')
    customer = routes[0].orderitem_set.all()[0].customerproduct.customer
    customerproducts = CustomerProduct.objects.filter(customer_id=customer.id)
    rows_list = []

    quantity = {cp.product.name:0 for cp in customerproducts}
    unit_price = {cp.product.name:0 for cp in customerproducts}
    nett_amt = {cp.product.name:0 for cp in customerproducts}

    for r in routes:
        row = {}
        route = get_object_or_404(Route, id=r.pk)
        row['date'] = route.trip.date
        row['do_number'] = route.do_number
        route_orderitems = list(route.orderitem_set.all())
        for oi in route_orderitems:
            quantity[oi.customerproduct.product.name] += oi.driver_quantity
            #  use orderitem's existing unit_price, customerproduct price may not be what it was before.
            #  if unit price row updates every iteration, may calculate total wrongly
            #  e.g. if an orderitem's price is different for a single row.
            #  but usually an invoice's customerproduct quote is consistent.
            unit_price[oi.customerproduct.product.name] = oi.unit_price

            if oi.quantity != oi.driver_quantity:
                row[oi.customerproduct.product.name] = str(oi.quantity) + " \u2794 " + str(oi.driver_quantity)
            else:
                row[oi.customerproduct.product.name] = oi.driver_quantity

        rows_list.append(row)

    for cp in nett_amt.keys():
        nett_amt[cp] = quantity[cp] * unit_price[cp]

    return render(request, template_name, {'company':company_info,
                                           'customer':customer,
                                           'customerproducts':customerproducts,
                                           'invoice':invoice,
                                           'rows_list':rows_list,
                                           'quantity':quantity,
                                           'unit_price':unit_price,
                                           'nett_amt':nett_amt,
                                           'invoice_form':invoice_form})


class InvoiceDeleteView(DeleteView):
    template_name = 'pos/invoice/invoice_confirm_delete.html'
    model = Invoice

    def get_object(self, queryset=None):
        return Invoice.objects.get(pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse('pos:invoice_history')


class InvoiceCustomerView(ListView):
    template_name = 'pos/invoice/customer_invoice.html'
    context_object_name = 'invoice_list'

    def get_queryset(self):
        customer_pk = self.kwargs['pk']
        customer = get_object_or_404(Customer, id=customer_pk)
        invoices = Invoice.get_customer_invoices(customer.pk)
        return invoices

    def get_context_data(self, **kwargs):
        context = super(InvoiceCustomerView, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        context['customer'] = customer
        return context