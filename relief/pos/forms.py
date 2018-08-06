from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Customer, Product, Trip, Route, OrderItem, Invoice
from datetime import datetime


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'postal_code', 'tel_no', 'fax_no', 'term', 'gst']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'specification']


class RouteArrangementForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['index']


class TripForm(forms.Form):
    date = forms.DateTimeField(
        label="Date (DD/MM/YYYY HHMM)",
        widget= forms.DateTimeInput(format="%d/%m/%Y %H%M"),
        input_formats=["%d/%m/%Y %H%M"])
    notes = forms.CharField(widget=forms.Textarea, required=False)
    packaging = forms.CharField(widget=forms.Textarea(attrs={'rows':1}),
                                required=False,
                                label="Packaging Methods (Separate with ,)")

    class Meta:
        model = Trip
        fields = ['date', 'notes']

    def clean(self):
        super(TripForm, self).clean()
        packaging = [method.strip() for method in self.cleaned_data['packaging'].split(',')]
        if len(packaging) > 8:
            raise forms.ValidationError("Too many methods, must be less than eight")
        self.cleaned_data['packaging'] = ",".join(packaging)


class TripDetailForm(forms.Form):
    note_only = forms.BooleanField(
        label='Note only',
        widget=forms.CheckboxInput(),
        required=False
    )
    note = forms.CharField(widget=forms.Textarea(
        attrs={'rows':4, 'columns':15}),
        max_length=255,
        required=False)

    customer = forms.CharField(widget=forms.TextInput(
        attrs={'rows': 1}), required=False)


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['do_number', 'note']


class CustomerProductCreateForm(forms.Form):
    quote_price = forms.DecimalField(decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(CustomerProductCreateForm, self).__init__(*args, **kwargs)
        self.fields['customer'] = forms.ChoiceField(
            choices=[(c.id, c.name) for c in Customer.objects.all()], disabled=True
        )
        self.fields['product'] = forms.ChoiceField(
            choices=[(p.id, p.name) for p in Product.objects.all()]
        )


class CustomerProductUpdateForm(forms.Form):
    customer = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    product = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    quote_price = forms.DecimalField(decimal_places=2)


class InvoiceDateRangeForm(forms.Form):
    date_start = forms.DateField(
        label="From",
        widget= forms.DateInput(format="%d-%m-%Y"),
        input_formats=["%d-%m-%Y"])
    date_end = forms.DateField(
        label="To",
        widget= forms.DateInput(format="%d-%m-%Y"),
        input_formats=["%d-%m-%Y"])


class ModelIntegerField(forms.IntegerField):
    def __init__(self, *, pk, model, instance, **kwargs):
        self.pk = pk
        self.model = model
        self.instance = instance
        super().__init__(**kwargs)


class InvoiceOrderItemForm(forms.Form):
    do_number = forms.CharField(max_length=8)

    def __init__(self, *args, orderitems, do_number='', **kwargs):
        super(InvoiceOrderItemForm, self).__init__(*args, **kwargs)
        self.fields['do_number'].initial = do_number
        for oi in orderitems:
            self.fields[oi.customerproduct.product.name] = ModelIntegerField(pk=oi.pk,
                                                                             model=OrderItem,
                                                                             instance=oi,
                                                                             initial=oi.quantity,
                                                                             min_value=0,
                                                                             max_value=32767)


class InvoiceAddOrderForm(forms.Form):
    do_number = forms.CharField(max_length=8, label="D/O", required=False)

    def __init__(self, *args, trips, customerproducts, **kwargs):
        super(InvoiceAddOrderForm, self).__init__(*args, **kwargs)
        for cp in customerproducts:
            self.fields[cp.product.name] = forms.IntegerField(label='quantity',
                                                              min_value=0,
                                                              max_value=32767,
                                                              required=False)

        self.fields['date'] = forms.ChoiceField(choices=[(t.id, datetime.strftime(t.date,"%d/%m/%Y %H:%M")) for t in trips])


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_year',
                  'invoice_number',
                  'original_total',
                  'minus',
                  'net_total',
                  'net_gst',
                  'total_incl_gst',
                  'remark']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_total'].disabled = True
        self.fields['original_total'].label = 'TOTAL'
        self.fields['minus'].label = 'MINUS'
        self.fields['net_total'].disabled = True
        self.fields['net_total'].label = 'NETT'
        self.fields['net_gst'].disabled = True
        self.fields['total_incl_gst'].disabled = True
        self.fields['total_incl_gst'].label = 'TOTAL (GST)'
        self.fields['invoice_year'].required = False
        self.fields['invoice_number'].required = False

    def clean(self):
        cleaned_data = super().clean()
        invoice_year = cleaned_data.get('invoice_year')
        invoice_number = cleaned_data.get('invoice_number')
        if (invoice_year is None) != (invoice_number is None):
            raise forms.ValidationError("Invoice Year and Number cannot be empty.")


class OrderItemForm(forms.ModelForm):
    def __init__(self, packing, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        for method in packing:
            self.fields[method] = forms.IntegerField(min_value=1, required=False)
            if self.instance.packing:
                self.fields[method].initial = self.instance.packing[method]

    def save(self, packing, commit=True):
        self.instance.packing = {method: self.cleaned_data.get(method) for method in packing}
        super(OrderItemForm, self).save()

    class Meta:
        model = OrderItem
        fields = ['quantity', 'note']


OrderItemFormSet = inlineformset_factory(Route,
                                         OrderItem,
                                         form=OrderItemForm,
                                         extra=0,
                                         can_delete=False)

RouteArrangementFormSet = modelformset_factory(Route, RouteArrangementForm, extra=0)

