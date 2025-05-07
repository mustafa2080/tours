from .models import Currency
from django.conf import settings
import json

def loading_processor(request):
    """Add loading spinner configuration to all templates"""
    # Get loading settings from settings.py
    loading_enabled = getattr(settings, 'LOADING_SPINNER_ENABLED', True)
    loading_css_classes = getattr(settings, 'LOADING_SPINNER_CSS_CLASSES', 'custom-spinner floating')
    loading_template = getattr(settings, 'LOADING_SPINNER_TEMPLATE', 'partials/loading.html')
    loading_show_delay = getattr(settings, 'LOADING_SHOW_DELAY_MS', 300)
    loading_hide_delay = getattr(settings, 'LOADING_HIDE_DELAY_MS', 300)
    loading_style = getattr(settings, 'LOADING_SPINNER_STYLE', 'dots')
    loading_size = getattr(settings, 'LOADING_SPINNER_SIZE', 'lg')
    loading_glass = getattr(settings, 'LOADING_SPINNER_GLASS', True)

    # Create a JSON configuration for JavaScript
    loading_config = {
        'enabled': loading_enabled,
        'showDelayMs': loading_show_delay,
        'hideDelayMs': loading_hide_delay,
        'style': loading_style,
        'size': loading_size,
        'glass': loading_glass
    }

    return {
        'LOADING_ENABLED': loading_enabled,
        'LOADING_CSS_CLASSES': loading_css_classes,
        'LOADING_TEMPLATE': loading_template,
        'LOADING_SHOW_DELAY_MS': loading_show_delay,
        'LOADING_HIDE_DELAY_MS': loading_hide_delay,
        'LOADING_STYLE': loading_style,
        'LOADING_SIZE': loading_size,
        'LOADING_GLASS': loading_glass,
        'LOADING_CONFIG_JSON': json.dumps(loading_config),
    }

def currency_processor(request):
    """Add currency information to all templates"""
    # Get current currency from session or default to settings
    current_currency_code = request.session.get('currency_code', settings.DEFAULT_CURRENCY_CODE)

    try:
        current_currency = Currency.objects.get(code=current_currency_code)
    except Currency.DoesNotExist:
        # Fallback to USD if selected currency doesn't exist
        try:
            current_currency = Currency.objects.get(code='USD')
            request.session['currency_code'] = 'USD'
        except Currency.DoesNotExist:
            # Handle case where Currency table might be empty
            current_currency = None

    # Get all active currencies for the dropdown
    # Ensure we have the four required currencies: USD, EUR, GBP, EGP
    currencies = Currency.objects.filter(code__in=['USD', 'EUR', 'GBP', 'EGP'], is_active=True)

    return {
        'DEFAULT_CURRENCY_CODE': settings.DEFAULT_CURRENCY_CODE,
        'current_currency_code': current_currency_code,
        'current_currency': current_currency,
        'available_currencies': currencies,
    }
