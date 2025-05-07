from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from .models import CustomUser

# استيرادات أخرى للفورمات العادية
class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'date_of_birth', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class UserProfileForm(forms.ModelForm):
    """Form for users to update their own profile information."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            pass  # Placeholder for styling

# فورم الـ Signup المخصصة
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label=_('First Name'))
    last_name = forms.CharField(max_length=30, label=_('Last Name'))
    username = forms.CharField(max_length=150, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make first_name and last_name required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        """Basic email validation for signup"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()

            # Check if email already exists - but don't raise an error
            # This allows the form to be submitted, and the server will handle duplicates
            if CustomUser.objects.filter(email__iexact=email).exists():
                # Just log it, don't raise an error
                print(f"Email {email} already exists, but allowing form submission")

        return email

    def clean(self):
        cleaned_data = super().clean()
        if 'password1' in cleaned_data and 'password2' in cleaned_data:
            if cleaned_data['password1'] != cleaned_data['password2']:
                raise forms.ValidationError(_("Passwords don't match"))

        # Generar automáticamente el nombre de usuario a partir del correo electrónico
        if 'email' in cleaned_data:
            email_username = cleaned_data['email'].split('@')[0]
            # Asegurarse de que el nombre de usuario sea único
            base_username = email_username
            counter = 1
            while CustomUser.objects.filter(username=email_username).exists():
                email_username = f"{base_username}{counter}"
                counter += 1
            cleaned_data['username'] = email_username

        return cleaned_data

# Remove the CustomLoginForm class entirely to use the default one from allauth