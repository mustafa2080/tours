"""
Performance optimization utilities for the tourism project.
"""
import time
import functools
import logging
from django.core.cache import cache
from django.conf import settings
from django.db import connection, reset_queries
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

def query_debugger(func):
    """
    Debug database queries for a function.
    Use as a decorator on view functions to log the number of queries executed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        query_count = len(connection.queries)
        query_time = sum(float(q.get('time', 0)) for q in connection.queries)
        
        logger.debug(f"Function: {func.__name__}")
        logger.debug(f"Number of Queries: {query_count}")
        logger.debug(f"Finished in: {(end - start):.2f}s")
        logger.debug(f"Query time: {query_time:.2f}s")
        
        # Log slow functions (taking more than 1 second)
        if end - start > 1.0:
            logger.warning(f"Slow function detected: {func.__name__} took {(end - start):.2f}s with {query_count} queries")
            
            # Log the actual queries if there are too many
            if query_count > 10:
                logger.warning("Queries executed:")
                for i, query in enumerate(connection.queries):
                    logger.warning(f"{i+1}. {query['sql']}")
        
        return result
    return wrapper


def method_query_debugger(name):
    """
    Debug database queries for a class method.
    Use as a decorator on class methods to log the number of queries executed.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            reset_queries()
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            query_count = len(connection.queries)
            query_time = sum(float(q.get('time', 0)) for q in connection.queries)
            
            logger.debug(f"Method: {name}.{func.__name__}")
            logger.debug(f"Number of Queries: {query_count}")
            logger.debug(f"Finished in: {(end - start):.2f}s")
            logger.debug(f"Query time: {query_time:.2f}s")
            
            # Log slow methods (taking more than 1 second)
            if end - start > 1.0:
                logger.warning(f"Slow method detected: {name}.{func.__name__} took {(end - start):.2f}s with {query_count} queries")
            
            return result
        return wrapper
    return decorator


def cache_page_for_user(timeout=3600):
    """
    Cache a view for a specific user.
    This is useful for views that are user-specific but can still be cached.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # For anonymous users, use the regular cache
                return view_func(request, *args, **kwargs)
            
            # For authenticated users, create a user-specific cache key
            cache_key = f"user_{request.user.id}_{request.path}"
            response = cache.get(cache_key)
            
            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def prefetch_related_objects(queryset, *related_lookups):
    """
    Prefetch related objects for a queryset to reduce database queries.
    This is a wrapper around Django's prefetch_related that logs the operation.
    """
    logger.debug(f"Prefetching related objects: {related_lookups}")
    return queryset.prefetch_related(*related_lookups)


def select_related_objects(queryset, *related_lookups):
    """
    Select related objects for a queryset to reduce database queries.
    This is a wrapper around Django's select_related that logs the operation.
    """
    logger.debug(f"Selecting related objects: {related_lookups}")
    return queryset.select_related(*related_lookups)
