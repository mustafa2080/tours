from django import template
from decimal import Decimal
from core.models import Currency

register = template.Library()

@register.filter
def convert_price(price, currency_code='USD'):
    """Convert price to the specified currency"""
    if not price:
        return "0.00"
        
    try:
        # Get the exchange rate for the target currency
        currency = Currency.objects.get(code=currency_code)
        converted_price = Decimal(price) * currency.exchange_rate
        
        # Format with 2 decimal places
        return f"{converted_price:.2f}"
    except Currency.DoesNotExist:
        return price
    except Exception:
        return price

@register.simple_tag
def currency_symbol(currency_code='USD'):
    """Return the symbol for the specified currency"""
    try:
        currency = Currency.objects.get(code=currency_code)
        return currency.symbol
    except Currency.DoesNotExist:
        return '$'  # Default to USD symbol