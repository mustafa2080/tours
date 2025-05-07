from django import template
from django.conf import settings
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from core.models import Currency
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.simple_tag(takes_context=True)
def convert_currency(context, value, original_currency_code=None):
    """
    Converts a given value from its original currency to the selected currency.
    Assumes exchange rates in the Currency model are relative to the base currency (settings.DEFAULT_CURRENCY_CODE).

    Usage: {% convert_currency tour.price tour.currency.code %}
           {% convert_currency tour.discount_price tour.currency.code %}
           {% convert_currency some_value 'USD' %} {# If original currency is known #}
    """
    try:
        # Ensure value is a Decimal for precision
        value = Decimal(str(value))
    except (TypeError, InvalidOperation, ValueError):
        logger.warning(f"Invalid value passed to convert_currency: {value}")
        return "" # Return empty string for invalid input values

    # Get the target currency object from the context (provided by context processor)
    target_currency = context.get('current_currency') # Use the correct context key
    if not target_currency:
        logger.warning("Target currency not found in template context.")
        return f"{value:.2f} ?" # Indicate missing target currency

    # If the original currency code is the same as the target, no conversion needed
    if original_currency_code == target_currency.code:
        # Format with 2 decimal places using ROUND_HALF_UP
        formatted_value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{target_currency.symbol}{formatted_value}"

    # Get the base currency code
    base_currency_code = settings.DEFAULT_CURRENCY_CODE

    # Get the exchange rate for the target currency from the database model
    target_rate = target_currency.exchange_rate
    if target_rate is None:
        logger.error(f"Exchange rate not found in DB for target currency: {target_currency.code}")
        return f"{value:.2f} {target_currency.code}!"

    # Get the exchange rate for the original currency from the database model
    original_rate = None
    original_currency = None
    if original_currency_code:
        try:
            original_currency = Currency.objects.get(code=original_currency_code)
            original_rate = original_currency.exchange_rate
        except Currency.DoesNotExist:
            logger.warning(f"Original currency not found in DB for code: {original_currency_code}")
            return f"{value:.2f} {original_currency_code}?" # Indicate missing original currency rate
    elif base_currency_code == target_currency.code:
         # If original code wasn't provided AND target is base, assume value is already in base
         original_rate = Decimal(1.0)
         original_currency_code = base_currency_code # For logging/error msg
    else:
        # Cannot proceed without original currency code if target isn't base
         logger.warning(f"Original currency code not provided and target is not base currency.")
         return f"{value:.2f} ?" # Indicate missing original currency info

    if original_rate is None:
        logger.error(f"Exchange rate not found in DB for original currency: {original_currency_code}")
        return f"{value:.2f} {original_currency_code}!"

    if original_rate == 0:
         logger.error(f"Original currency rate is zero in DB for code: {original_currency_code}")
         return f"{value:.2f} {original_currency_code}!" # Cannot divide by zero

    # Perform the conversion: (value / original_rate_to_base) * target_rate_to_base
    try:
        # Ensure rates are Decimal
        original_rate = Decimal(str(original_rate))
        target_rate = Decimal(str(target_rate))

        converted_value = (value / original_rate) * target_rate
        # Format with the target currency symbol and 2 decimal places, rounding correctly
        formatted_value = converted_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{target_currency.symbol}{formatted_value}"
    except (TypeError, InvalidOperation, ZeroDivisionError) as e:
         logger.error(f"Error during currency conversion calculation: {e}")
         return f"{value:.2f} ?" # Error during calculation
