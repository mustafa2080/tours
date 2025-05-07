from django import template

register = template.Library()

@register.filter
def map_attribute(queryset, attribute):
    """
    Returns a list of values for a given attribute from a queryset
    Example: {{ user.wishlist_items.all|map_attribute:"tour" }}
    """
    return [getattr(obj, attribute) for obj in queryset]