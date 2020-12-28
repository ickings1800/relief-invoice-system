from django import forms
from django.forms import formset_factory
from .models import Customer, Product, Trip, Route, OrderItem, Invoice, CustomerProduct
from datetime import datetime, date

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



class ImportFileForm(forms.Form):
    import_customer_file = forms.FileField(required=False, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'file'}))
    import_product_file = forms.FileField(required=False, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'file'}))
    import_quote_file = forms.FileField(required=False, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'file'}))
    import_orderitem_file = forms.FileField(required=False, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'file'}))
    import_invoice_file = forms.FileField(required=False, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'file'}))

class ExportOrderItemForm(forms.Form):
    start_date = forms.DateField(required=True, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'date', 'value': date.today()}))
    end_date = forms.DateField(required=True, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'date', 'value': date.today()}))

class ExportInvoiceForm(forms.Form):
    start_date = forms.DateField(required=True, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'date', 'value': date.today()}))
    end_date = forms.DateField(required=True, widget=forms.TextInput(attrs={'class':'form-input', 'type': 'date', 'value': date.today()}))    

# RouteArrangementFormSet = modelformset_factory(Route, RouteArrangementForm, extra=0)

