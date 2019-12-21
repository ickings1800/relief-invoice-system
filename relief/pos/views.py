from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, FormView, DeleteView, DetailView
from .models import Customer, Product, Trip, CustomerProduct, Route, OrderItem, Invoice, Company, CustomerGroup, Group
from .forms import CustomerForm, ProductForm, TripForm, TripDetailForm, CustomerProductCreateForm, \
    CustomerProductUpdateForm, OrderItemFormSet, RouteForm, \
    InvoiceDateRangeForm, InvoiceOrderItemForm, InvoiceAddOrderForm, InvoiceForm, RouteArrangementFormSet
from collections import defaultdict
from io import BytesIO


# Create your views here.

class CustomerIndexView(ListView):
    template_name = 'pos/customer/index.html'
    context_object_name = 'group_dict'

    def get_queryset(self):
        group_dict = {}
        groups = Group.objects.all()
        for g in groups:
            customer_groups = list(CustomerGroup.objects.filter(group_id=g.pk).order_by('index'))
            group_dict[g.name] = customer_groups
        return group_dict


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

    def get_context_data(self, **kwargs):
        customer = self.kwargs['pk']
        context = super(CustomerDetailView, self).get_context_data(**kwargs)
        customer_group = get_object_or_404(CustomerGroup, customer_id=customer)
        groups = Group.objects.all()
        context['customer_group'] = customer_group
        context['groups'] = groups
        return context


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
        context = super(TripDetailView, self).get_context_data(**kwargs)
        context['trip'] = trip
        context['routes'] = trip.route_set.all().order_by('index')
        context['customers'] = Customer.objects.all()
        if trip.packaging_methods:
            packing = trip.packaging_methods.split(',')
            context['packing'] = [e.strip() for e in packing]
        return context

    def get_success_url(self):
        return reverse('pos:trip_detail', kwargs={'pk':self.kwargs['pk']})


def print_trip_detail(request, pk):
    template_name = 'pos/trip/print_detail.html'
    trip = get_object_or_404(Trip, pk=pk)
    routes = Route.objects.filter(trip_id=trip.pk).order_by('index')
    context = {'trip': trip, 'routes': routes}
    if trip.packaging_methods:
        packing = trip.packaging_methods.split(',')
        context['packing'] = [e.strip() for e in packing]
    return render(request, template_name, context)


class TripDeleteView(DeleteView):
    template_name = 'pos/trip/trip_confirm_delete.html'
    model = Trip

    def get_object(self, queryset=None):
        return Trip.objects.get(pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse('pos:trip_index')


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
        customer_group = CustomerGroup.objects.filter(customer_id=customer.pk)[0]
        customer_groups = CustomerGroup.objects.filter(group_id=customer_group.group_id).order_by('index')
        return render(request, template_name, {'customer': customer, 'customer_groups':customer_groups})


def InvoiceSingleView(request, invoice_pk):
    invoice_file = Invoice.export_invoice_to_pdf(int(invoice_pk))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename={0}.pdf'.format(invoice_pk)
    response.write(invoice_file.getvalue())
    return response


class InvoiceHistoryView(ListView):
    template_name = 'pos/invoice/invoice_history.html'
    context_object_name = 'invoice_list'

    def get_queryset(self):
        return Invoice.objects.all()



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