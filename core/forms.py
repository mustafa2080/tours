from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    """Form for contact page"""
    name = forms.CharField(
        label=_('Your Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your name')})
    )
    email = forms.EmailField(
        label=_('Your Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    subject = forms.CharField(
        label=_('Subject'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter subject')})
    )
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Enter your message')})
    )


class NewsletterForm(forms.Form):
    """Form for newsletter subscription"""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
