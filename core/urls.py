from django.urls import path
from django.views.i18n import set_language  # Add this import
from django.contrib.admin.views.decorators import staff_member_required
from .views import (
    HomeView, AboutView, FAQListView, ContactView,
    TermsConditionsView, PrivacyPolicyView,
    subscribe_newsletter, set_currency, get_exchange_rates,
    performance_dashboard, healthcheck
)
from . import views

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('faq/', FAQListView.as_view(), name='faq'),
    path('terms/', TermsConditionsView.as_view(), name='terms'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
    path('newsletter/subscribe/', subscribe_newsletter, name='newsletter_subscribe'),
    # path('i18n/setlang/', set_language, name='set_language'), # Removed, defined globally in project urls.py
    path('set-currency/', set_currency, name='set_currency'),
    path('api/exchange-rates/', get_exchange_rates, name='get_exchange_rates'),

    # Performance monitoring
    path('admin/performance/', staff_member_required(performance_dashboard), name='performance_dashboard'),

    # Health check
    path('health/', healthcheck, name='healthcheck'),

    # CSRF token
    path('csrf/', views.csrf_token_view, name='csrf_token'),
]
