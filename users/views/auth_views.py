from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import DatabaseError

from allauth.account.views import SignupView, LoginView
from allauth.account.forms import SignupForm, LoginForm

class SafeSignupView(SignupView):
    """
    A safe version of the SignupView that doesn't depend on the django_site table.
    This is used as a fallback when the site table doesn't exist yet.
    """
    template_name = 'account/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        try:
            # Try to use the original SignupView
            return super().dispatch(request, *args, **kwargs)
        except DatabaseError as e:
            # If there's a database error (like missing django_site table),
            # render a simple signup form
            if 'django_site' in str(e):
                messages.error(request, _("The site is still being set up. Please try again later."))
                return redirect('core:home')
            # For other database errors, re-raise
            raise
            
class SafeLoginView(LoginView):
    """
    A safe version of the LoginView that doesn't depend on the django_site table.
    This is used as a fallback when the site table doesn't exist yet.
    """
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        try:
            # Try to use the original LoginView
            return super().dispatch(request, *args, **kwargs)
        except DatabaseError as e:
            # If there's a database error (like missing django_site table),
            # render a simple login form
            if 'django_site' in str(e):
                messages.error(request, _("The site is still being set up. Please try again later."))
                return redirect('core:home')
            # For other database errors, re-raise
            raise
