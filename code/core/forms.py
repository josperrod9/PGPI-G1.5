from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import UserProfile


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('C', 'Contrareembolso')
)

SHIPPING_CHOICES = (
    ('R', 'Recogida en tienda: Calle Avenida de la Reina Mercedes, 51'),
    ('D', 'Envío a domicilio')
)


class CheckoutForm(forms.Form):
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    shipping_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=SHIPPING_CHOICES)

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)

class UpdateShippingAddressForm(forms.Form):
    shipping_address = forms.CharField(required=True, label='Nueva dirección de envío')

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'email']

class OpinionCreateForm(forms.Form):
    title = forms.CharField(required=True, label='Título', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(required=True, label='Descripción',max_length=200, widget=forms.Textarea(attrs={'class': 'form-control'}))
    

class ResponseCreateForm(forms.Form):
    description = forms.CharField(required=True, label='Ponga aqui su respuesta', max_length=200, widget=forms.Textarea(attrs={'class': 'form-control'}))