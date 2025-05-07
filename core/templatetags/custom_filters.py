from django import template
from django.conf import settings
import locale
from decimal import Decimal

register = template.Library()

@register.filter
def split_lines(value):
    """
    Split a string by newlines and return a list of non-empty lines.

    Usage:
    {% for line in text|split_lines %}
        <li>{{ line }}</li>
    {% endfor %}
    """
    if not value:
        return []

    return [line.strip() for line in value.splitlines() if line.strip()]

@register.filter
def sub(value, arg):
    """
    Subtracts the arg from the value.

    Usage:
    {{ value|sub:arg }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def div(value, arg):
    """
    Divides the value by the arg.

    Usage:
    {{ value|div:arg }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """
    Multiplies the value by the arg.

    Usage:
    {{ value|mul:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='currency')
def currency(value, currency_code=None):
    """
    Format a value as currency.

    Usage:
        {{ value|currency:"USD" }}
        {{ value|currency }}  # Uses default currency from settings
    """
    if value is None:
        return ''

    # Get currency code from parameter or settings
    currency_code = currency_code or getattr(settings, 'DEFAULT_CURRENCY_CODE', 'USD')

    # Format based on currency code
    if currency_code == 'USD':
        return f"${value:.2f}"
    elif currency_code == 'EUR':
        return f"€{value:.2f}"
    elif currency_code == 'GBP':
        return f"£{value:.2f}"
    elif currency_code == 'JPY':
        return f"¥{value:.0f}"
    elif currency_code == 'CNY':
        return f"¥{value:.2f}"
    elif currency_code == 'AUD':
        return f"A${value:.2f}"
    elif currency_code == 'CAD':
        return f"C${value:.2f}"
    elif currency_code == 'CHF':
        return f"CHF {value:.2f}"
    elif currency_code == 'EGP':
        return f"E£{value:.2f}"
    else:
        # Default format for other currencies
        return f"{value:.2f} {currency_code}"

@register.filter(name='format_price')
def format_price(value, currency_code=None):
    """
    Format a price value with thousand separators and currency symbol.

    Usage:
        {{ value|format_price:"USD" }}
        {{ value|format_price }}  # Uses default currency from settings
    """
    if value is None:
        return ''

    # Get currency code from parameter or settings
    currency_code = currency_code or getattr(settings, 'DEFAULT_CURRENCY_CODE', 'USD')

    # Format with thousand separators
    try:
        # Try to use locale-specific formatting
        locale.setlocale(locale.LC_ALL, '')
        formatted_value = locale.format_string("%.2f", float(value), grouping=True)
    except (ValueError, locale.Error):
        # Fallback to simple formatting
        formatted_value = f"{float(value):,.2f}"

    # Add currency symbol
    if currency_code == 'USD':
        return f"${formatted_value}"
    elif currency_code == 'EUR':
        return f"€{formatted_value}"
    elif currency_code == 'GBP':
        return f"£{formatted_value}"
    elif currency_code == 'JPY':
        return f"¥{formatted_value.split('.')[0]}"  # No decimal places for JPY
    elif currency_code == 'CNY':
        return f"¥{formatted_value}"
    elif currency_code == 'AUD':
        return f"A${formatted_value}"
    elif currency_code == 'CAD':
        return f"C${formatted_value}"
    elif currency_code == 'CHF':
        return f"CHF {formatted_value}"
    elif currency_code == 'EGP':
        return f"E£{formatted_value}"
    else:
        # Default format for other currencies
        return f"{formatted_value} {currency_code}"
