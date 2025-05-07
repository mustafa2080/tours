from django import forms
from .models import Payment
from django.utils.translation import gettext_lazy as _

# Example form if you needed manual payment entry (unlikely for Stripe/PayPal)
# class PaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = ['booking', 'amount', 'payment_method', 'transaction_id', 'status']

# More likely, forms might be used for selecting payment method before redirecting
class PaymentMethodForm(forms.Form):
    payment_method = forms.ChoiceField(
        label=_("Select Payment Method"),
        choices=Payment.payment_method.field.choices,
        widget=forms.RadioSelect(attrs={'class': 'space-y-2'}),
        required=True
    )
