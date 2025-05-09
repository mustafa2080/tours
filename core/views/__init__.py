"""
Views package for the core app.
"""

from .core_views import (
    HomeView,
    AboutView,
    FAQListView,
    ContactView,
    TermsConditionsView,
    PrivacyPolicyView,
    subscribe_newsletter,
    set_currency,
    get_exchange_rates,
    csrf_failure
)

from .performance import performance_dashboard
from .healthcheck import healthcheck

# Import the CSRF token view
from django.http import JsonResponse
from django.middleware.csrf import get_token

def csrf_token_view(request):
    """
    View to set CSRF cookie.
    """
    # Get the CSRF token for this request
    csrf_token = get_token(request)

    # Return the token in a JSON response
    return JsonResponse({'csrfToken': csrf_token})
