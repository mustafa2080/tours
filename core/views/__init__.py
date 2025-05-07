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
