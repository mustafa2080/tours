"""
Health check views for the application.
"""
from django.http import HttpResponse

def healthcheck(request):
    """
    Simple health check view that verifies the application is running.
    """
    return HttpResponse("OK", content_type="text/plain")
