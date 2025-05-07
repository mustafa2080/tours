"""
Performance monitoring views for the tourism project.
"""
import time
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

@staff_member_required
def performance_dashboard(request):
    """
    Display performance statistics for the site.
    """
    # Get slow pages from cache
    slow_pages = cache.get('slow_pages', {})
    
    # Convert timestamps to datetime objects
    for path, data in slow_pages.items():
        data['last_seen'] = timezone.datetime.fromtimestamp(data['last_seen'])
    
    # Get database query statistics
    start_time = time.time()
    query_count = len(connection.queries)
    query_time = sum(float(q.get('time', 0)) for q in connection.queries)
    
    # Get cache statistics (these would need to be tracked separately in a real app)
    cache_hits = cache.get('cache_hits', 0)
    cache_misses = cache.get('cache_misses', 0)
    
    # Calculate page load time
    page_load_time = time.time() - start_time
    
    context = {
        'slow_pages': slow_pages,
        'query_count': query_count,
        'query_time': query_time,
        'page_load_time': page_load_time,
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
    }
    
    return render(request, 'performance_optimizations.html', context)
