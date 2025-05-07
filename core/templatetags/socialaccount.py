"""
Custom template tags to replace the socialaccount template tags.
"""

from django import template

register = template.Library()

@register.simple_tag
def get_providers(*args, **kwargs):
    """
    Return an empty list of providers.
    """
    return []

@register.simple_tag
def provider_login_url(*args, **kwargs):
    """
    Return an empty URL.
    """
    return '#'

@register.simple_tag
def providers_media_js(*args, **kwargs):
    """
    Return an empty string.
    """
    return ''
