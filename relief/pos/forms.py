from datetime import date

from django import forms


class ImportFileForm(forms.Form):
    import_customer_file = forms.FileField(
        required=False, widget=forms.TextInput(attrs={"class": "form-input", "type": "file"})
    )
    import_product_file = forms.FileField(
        required=False, widget=forms.TextInput(attrs={"class": "form-input", "type": "file"})
    )
    import_quote_file = forms.FileField(
        required=False, widget=forms.TextInput(attrs={"class": "form-input", "type": "file"})
    )
    import_orderitem_file = forms.FileField(
        required=False, widget=forms.TextInput(attrs={"class": "form-input", "type": "file"})
    )
    import_detrack_file = forms.FileField(
        required=False, widget=forms.TextInput(attrs={"class": "form-input", "type": "file"})
    )
    import_invoice_file = forms.FileField(
        required=False, widget=forms.TextInput(attrs={"class": "form-input", "type": "file"})
    )


class ExportOrderItemForm(forms.Form):
    start_date = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"class": "form-input", "type": "date", "value": date.today()})
    )
    end_date = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"class": "form-input", "type": "date", "value": date.today()})
    )


class ExportInvoiceForm(forms.Form):
    start_date = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"class": "form-input", "type": "date", "value": date.today()})
    )
    end_date = forms.DateField(
        required=True, widget=forms.TextInput(attrs={"class": "form-input", "type": "date", "value": date.today()})
    )


class CompanySelectForm(forms.Form):
    company = forms.ChoiceField(required=True, choices=[])

    def __init__(self, *args, **kwargs):
        companies = kwargs.pop("companies", [])
        super(CompanySelectForm, self).__init__(*args, **kwargs)
        self.fields["company"].choices = [(account_id, account_name) for account_id, account_name in companies.items()]
        self.fields["company"].widget.attrs.update({"class": "form-select"})

    def clean_company(self):
        company = self.cleaned_data.get("company")
        if company not in self.fields["company"].choices:
            raise forms.ValidationError("Please select a valid company")
        return company
