from django import forms
from datetime import date


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