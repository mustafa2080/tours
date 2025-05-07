from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the argument.
    
    Usage: {{ value|multiply:arg }}
    Example: {{ 5|multiply:10 }} will output 50
    """
    try:
        # Convert to Decimal for precise calculations
        value = Decimal(str(value))
        arg = Decimal(str(arg))
        return value * arg
    except (ValueError, TypeError):
        return 0
