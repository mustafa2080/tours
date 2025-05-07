"""
Custom authentication views to replace the allauth views.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext as _

@csrf_protect
def custom_login(request):
    """
    Custom login view to replace the allauth login view.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to the next page or home
            next_url = request.POST.get('next', reverse('core:home'))
            return redirect(next_url)
        else:
            messages.error(request, _('Invalid username or password.'))
    
    return render(request, 'account/login_simple.html', {
        'form': None,
        'signup_url': reverse('account_signup'),
    })
