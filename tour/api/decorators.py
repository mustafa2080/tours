from functools import wraps
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.conf import settings

def cache_response(timeout=None, cache=None, key_prefix=None):
    """
    Cache the response of a view for a specified time.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            return cache_page(
                timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                cache=cache,
                key_prefix=key_prefix
            )(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def cache_per_user(timeout=None):
    """
    Cache the response of a view for each user separately.
    """
    def decorator(view_func):
        @wraps(view_func)
        @vary_on_cookie
        @vary_on_headers('Authorization')
        def _wrapped_view(request, *args, **kwargs):
            return cache_page(
                timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                cache='api'
            )(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def cache_public(timeout=None):
    """
    Cache the response of a public view (same for all users).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            return cache_page(
                timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                cache='api'
            )(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def method_cache(timeout=None):
    """
    Cache for class-based views or view methods, applying cache only to GET and HEAD methods.
    """
    def decorator(view_func):
        # Check if this is a class-based view
        if hasattr(view_func, 'dispatch'):
            # This is a class-based view
            view_func.dispatch = method_decorator(
                cache_page(
                    timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                    cache='api'
                )
            )(view_func.dispatch)
            return view_func
        else:
            # This is a function-based view or a method
            @wraps(view_func)
            def wrapped_view(*args, **kwargs):
                return cache_page(
                    timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                    cache='api'
                )(view_func)(*args, **kwargs)
            return wrapped_view
    return decorator

def method_cache_per_user(timeout=None):
    """
    Cache for class-based views or view methods, applying cache per user only to GET and HEAD methods.
    """
    def decorator(view_func):
        # Check if this is a class-based view
        if hasattr(view_func, 'dispatch'):
            # This is a class-based view
            view_func.dispatch = method_decorator(
                vary_on_cookie
            )(method_decorator(
                vary_on_headers('Authorization')
            )(method_decorator(
                cache_page(
                    timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                    cache='api'
                )
            )(view_func.dispatch)))
            return view_func
        else:
            # This is a function-based view or a method
            @wraps(view_func)
            def wrapped_view(*args, **kwargs):
                @vary_on_cookie
                @vary_on_headers('Authorization')
                def _wrapped_with_vary(request, *inner_args, **inner_kwargs):
                    return cache_page(
                        timeout or settings.REST_FRAMEWORK.get('DEFAULT_CACHE_RESPONSE_TIMEOUT', 900),
                        cache='api'
                    )(view_func)(request, *inner_args, **inner_kwargs)

                return _wrapped_with_vary(*args, **kwargs)
            return wrapped_view
    return decorator
