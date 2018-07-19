from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, FormView, DeleteView, DetailView
from .models import Customer, Product, Trip, CustomerProduct, Route, OrderItem, Invoice, Company, Packing
from .forms import CustomerForm, ProductForm, TripForm, TripDetailForm, CustomerProductCreateForm, \
    CustomerProductUpdateForm, OrderItemFormSet, RouteForm, \
    InvoiceDateRangeForm, InvoiceOrderItemForm, InvoiceAddOrderForm, InvoiceForm, RouteArrangementFormSet
from django.db.models import Max
from datetime import datetime, date
from collections import defaultdict

# Create your views here.

class CustomerIndexView(ListView):
    template_name = 'pos/customer/index.html'
    context_object_name = 'customer_list'

    def get_queryset(self):
        return Customer.objects.all()

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'pos/customer/detail.html'


class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'pos/customer/create.html'
    form_class = CustomerForm

    def get_success_url(self):
        return reverse('pos:customer_index')


class CustomerEditView(UpdateView):
    template_name = 'pos/customer/edit.html'
    model = Customer
    form_class = CustomerForm

    def get_success_url(self):
        return reverse('pos:customer_index')


class ProductIndexView(ListView):
    template_name = 'pos/product/index.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        return Product.objects.all()


class ProductCreateView(CreateView):
    model = Product
    template_name = 'pos/product/create.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse('pos:product_index')


class ProductEditView(UpdateView):
    model = Product
    template_name = 'pos/product/edit.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse('pos:product_index')


class CustomerRouteView(ListView):
    template_name = 'pos/route/customer_routes.html'
    context_object_name = 'route_list'

    def get_queryset(self):
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        route_list = Route.objects.filter(orderitem__customerproduct__customer_id=customer.pk)\
                                .filter((Q(orderitem__quantity__gt=0) | Q(orderitem__driver_quantity__gt=0)))\
            .distinct()
        return route_list

    def get_context_data(self, **kwargs):
        context = super(CustomerRouteView, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        context['customer'] = customer
        return context


class TripIndexView(ListView):
    template_name = 'pos/trip/index.html'
    context_object_name = 'trip_list'

    def get_queryset(self):
        return Trip.objects.all()


class TripCreateView(FormView):
    template_name = 'pos/trip/create.html'
    form_class = TripForm

    def form_valid(self, form):
        trip = Trip.objects.create(
            date=form.cleaned_data['date'],
            notes=form.cleaned_data['notes']
        )
        trip.save()
        return HttpResponseRedirect(reverse('pos:trip_index'))

    def get_success_url(self):
        return reverse('pos:trip_index')


class TripDetailView(FormView):
    model = Trip
    template_name = 'pos/trip/detail.html'
    form_class = TripDetailForm

    def get_context_data(self, **kwargs):
        trip = get_object_or_404(Trip, pk=self.kwargs['pk'])
        routes = trip.route_set.all().order_by('index')
        [r.orderitem_set.all() for r in routes]
        packing = [key.value for key in Packing]
        packing_sum_ddict = defaultdict(int)

        for r in routes:
            for oi in r.orderitem_set.all():
                if oi.packing:
                    for method, value in oi.packing.items():
                        if oi.packing.get(method):
                            packing_sum_ddict[method] += value

        packing_sum = {k: v for k, v in packing_sum_ddict.items()}
        print(packing_sum)

        context = super(TripDetailView, self).get_context_data(**kwargs)
        context['trip'] = trip
        context['routes'] = routes
        context['packing'] = packing
        context['packing_sum'] = packing_sum
        return context

    def form_valid(self, form):
        if form.is_valid():
            note_only = form.cleaned_data['note_only']
            note = form.cleaned_data['note']
            trip = Trip.objects.get(pk=self.kwargs['pk'])
            route_list = Route.objects.filter(trip_id=self.kwargs['pk'])
            route_indexes = [r.index for r in route_list]
            route = Route(index=max(route_indexes) + 1, trip=trip, note=note)
            route.save()

            if not note_only:
                customer_id = form.cleaned_data['customers']
                customerproducts = CustomerProduct.objects.filter(customer_id=customer_id)

                for cp in customerproducts:
                    orderitem = OrderItem(customerproduct=cp, route=route)
                    orderitem.save()

        return super(TripDetailView, self).form_valid(form)

    def get_success_url(self):
        return reverse('pos:trip_detail', kwargs={'pk':self.kwargs['pk']})


class TripEditView(FormView):
    template_name = 'pos/trip/edit.html'
    form_class = TripForm

    def get_context_data(self, **kwargs):
        trip = Trip.objects.get(pk=self.kwargs['pk'])
        context = super(TripEditView, self).get_context_data(**kwargs)
        context['trip'] = trip
        return context

    def get_initial(self):
        trip = Trip.objects.get(pk=self.kwargs['pk'])
        initial = super(TripEditView, self).get_initial()
        initial['date'] = trip.date
        initial['notes'] = trip.notes
        return initial

    def form_valid(self, form):
        trip_date = form.cleaned_data['date']
        trip_notes = form.cleaned_data['notes']
        trip_pk = self.kwargs['pk']

        trip = get_object_or_404(Trip, pk=trip_pk)
        trip.date = trip_date
        trip.notes = trip_notes
        trip.save()

        return super(TripEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse('pos:trip_index')


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
    packing = [key.value for key in Packing]
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
        packing = [key.value for key in Packing]
        oi_formset = OrderItemFormSet(instance=route, form_kwargs={'packing': packing})
        #  Read JSON and output to packing table.
        context = super().get_context_data(**kwargs)
        context['route'] = route
        context['orderitems'] = oi_formset
        context['packing'] = packing
        return context

    def form_valid(self, form):
        route = get_object_or_404(Route, pk=self.kwargs['pk'])
        packing = [key.value for key in Packing]
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
        super(RouteDeleteView, self).delete(request, args, kwargs)
        route_list = Route.objects.filter(trip_id=self.kwargs['trip_pk'])
        for i in range(len(route_list)):
            route_list[i].index = i+1
            route_list[i].save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('pos:trip_detail', kwargs={'pk':self.kwargs['trip_pk']})


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


class CustomerProductCreateView(FormView):
    template_name = 'pos/customerproduct/create.html'
    form_class = CustomerProductCreateForm

    def get_context_data(self, **kwargs):
        context = super(CustomerProductCreateView, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        context['customer'] = customer
        return context

    def get_initial(self):
        initial = super(CustomerProductCreateView, self).get_initial()
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        initial['customer'] = customer.id
        return initial

    def form_valid(self, form):
        customer_data = int(form.cleaned_data['customer'])
        product_data = int(form.cleaned_data['product'])
        quote = form.cleaned_data['quote_price']

        customerproduct_exists = CustomerProduct.objects.filter(customer_id=customer_data, product_id=product_data)
        if len(customerproduct_exists) > 0:
            form.add_error('product', "CustomerProduct already exists.")
            return self.render_to_response(self.get_context_data(form=form))
        else:
            customer = get_object_or_404(Customer, pk=customer_data)
            product = get_object_or_404(Product, pk=product_data)
            CustomerProduct.objects.create(customer_id=customer_data, product_id=product_data, quote_price=quote)
            return HttpResponseRedirect(reverse('pos:customerproduct_index', kwargs={'cust_pk':customer_data}))


class CustomerProductUpdateView(FormView):
    template_name = 'pos/customerproduct/edit.html'
    form_class = CustomerProductUpdateForm

    def get_context_data(self, **kwargs):
        customerproduct_id = self.kwargs['pk']
        customerproduct = get_object_or_404(CustomerProduct, id=customerproduct_id)
        context = super(CustomerProductUpdateView, self).get_context_data(**kwargs)
        context['customerproduct'] = customerproduct
        return context

    def get_initial(self):
        customerproduct_id = self.kwargs['pk']
        customerproduct = get_object_or_404(CustomerProduct, id=customerproduct_id)
        initial = super(CustomerProductUpdateView, self).get_initial()
        initial['customer'] = customerproduct.customer.name
        initial['product'] = customerproduct.product.name
        initial['quote_price'] = customerproduct.quote_price
        return initial

    def form_valid(self, form):
        customerproduct_id = self.kwargs['pk']
        quote_price = float(form.cleaned_data['quote_price'])
        customerproduct = get_object_or_404(CustomerProduct, id=customerproduct_id)
        customerproduct.quote_price = quote_price
        customerproduct.save()
        return super(CustomerProductUpdateView, self).form_valid(form)

    def get_success_url(self):
        customerproduct_id = self.kwargs['pk']
        customerproduct = get_object_or_404(CustomerProduct, id=customerproduct_id)
        customer_id = customerproduct.customer.id
        return reverse('pos:customerproduct_index', kwargs={'pk':customer_id})


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
            date_end_formatted =  datetime.strftime(date_end,'%Y-%m-%d')
            date_start_formatted = datetime.strftime(date_start, '%Y-%m-%d')
            request.session['date_start'] = date_start_formatted
            request.session['date_end'] = date_end_formatted

            route_list = Route.objects.filter(trip__date__lte=date_end_formatted,
                                              trip__date__gte=date_start_formatted,
                                              invoice__exact=None,
                                              orderitem__customerproduct__customer_id=customer.id)\
                                              .distinct()
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
    trips = Trip.objects.filter(date__lte=trip_end, date__gte=trip_start)
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
                route = Route(index=route_index_max.get('index__max') + 1, do_number=do_number, trip_id=trip.pk)
                route.save()
                request.session['route_select'].append(route.pk)
                additional_order_fields = {}
                for cp in customerproducts:
                    orderitem_quantity = add_form.cleaned_data[cp.product.name]
                    orderitem = OrderItem(quantity=orderitem_quantity,
                                          customerproduct=cp,
                                          route=route)
                    orderitem.save()
                    additional_order_fields[cp.product.name] = orderitem_quantity


                additional_order = InvoiceOrderItemForm(prefix=str(route.id),
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
            invoice = Invoice(gst=customer.gst, start_date=trip_start, end_date=trip_end)
            invoice.save()
            original_total = 0
            for r in routes:
                route = get_object_or_404(Route, id=r)
                route.invoice = invoice
                orderitems = route.orderitem_set.all()
                for oi in orderitems:
                    quote = oi.customerproduct.quote_price
                    oi.unit_price = quote
                    oi.save()
                    original_total += (oi.driver_quantity * oi.unit_price)
                route.save()

            net_total = original_total
            gst = original_total * invoice.gst
            invoice.net_total = net_total
            invoice.original_total = original_total
            invoice.net_gst = gst
            invoice.total_incl_gst = net_total + gst
            if invoice.gst > 0:
                invoice.invoice_year = int(date.strftime(date.today(), '%Y'))
                invoice_num_max = Invoice.objects.all().aggregate(Max('invoice_number'))
                # this condition only occurs on the first invoice (with gst) created.
                if invoice_num_max.get('invoice_number__max') is None:
                    invoice.invoice_number = 0
                else:
                    invoice.invoice_number = invoice_num_max.get('invoice_number__max') + 1
            invoice.save()
            return HttpResponseRedirect(reverse('pos:invoice_view', kwargs={'pk':invoice.pk}))
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
    invoice_id = pk
    invoice = get_object_or_404(Invoice, id=invoice_id)
    company_info = get_object_or_404(Company, id=1)
    routes = invoice.route_set.all()
    customer = routes[0].orderitem_set.all()[0].customerproduct.customer
    customerproducts = CustomerProduct.objects.filter(customer_id=customer.id)
    rows_list = []

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        if invoice_form.is_valid():
            minus = invoice_form.cleaned_data['minus']
            gst = invoice_form.cleaned_data['gst']
            remark = invoice_form.cleaned_data['remark']

            original_total = invoice.original_total
            net_total = original_total - minus
            net_gst = gst * net_total
            total_incl_gst = net_total + net_gst

            invoice.remark = remark
            invoice.original_total = original_total
            invoice.net_total = net_total
            invoice.net_gst = net_gst
            invoice.total_incl_gst = total_incl_gst
            invoice.save()
            return HttpResponseRedirect("")
        else:
            return render(request, template_name, {'company': company_info,
                                                   'customer': customer,
                                                   'invoice': invoice,
                                                   'invoice_form': invoice_form})

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

    invoice_form = InvoiceForm(instance=invoice)

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
        invoices = Invoice.objects.filter(route__orderitem__customerproduct__customer_id=customer.pk)\
            .distinct('pk')
        return invoices

    def get_context_data(self, **kwargs):
        context = super(InvoiceCustomerView, self).get_context_data(**kwargs)
        customer = get_object_or_404(Customer, id=self.kwargs['pk'])
        context['customer'] = customer
        return context