from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget



PAYMENT_CHOICE = (  
    ('P','paypal'),
    ('S' ,'Stripe')
)



class CheckoutForm(forms.Form):
    shipping_street_address = forms.CharField(required=False)
    shipping_apartment_address =forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
    required=False,
    widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
    }))
    shipping_zip = forms.CharField(required=False)
    billing_same_as_shipping = forms.BooleanField(widget= forms.CheckboxInput(), required=False)
    shipping_save_info =  forms.BooleanField(widget= forms.CheckboxInput(), required=False)
    shipping_use_default = forms.BooleanField(widget=forms.CheckboxInput(),required=False) 




    billing_street_address = forms.CharField(required=False)
    billing_apartment_address =forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
    required=False,
    widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
    }))
    billing_zip = forms.CharField(required=False)
    billing_use_default = forms.BooleanField(widget=forms.CheckboxInput(),required=False) 
    billing_save_info =  forms.BooleanField(widget= forms.CheckboxInput(), required=False)
    payment_method = forms.ChoiceField(widget=forms.RadioSelect(),choices=PAYMENT_CHOICE)

    

    


class CuponForm(forms.Form):
    cupon_code = forms.CharField()
    


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    email = forms.EmailField()
    resion = forms.CharField()


class SearchForm(forms.Form):
    search = forms.CharField()
