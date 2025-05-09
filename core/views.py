from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token


def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view.
    """
    return render(request, 'errors/csrf_failure.html', {
        'reason': reason
    })


def csrf_token_view(request):
    """
    View to set CSRF cookie.
    """
    # Get the CSRF token for this request
    csrf_token = get_token(request)
    
    # Return the token in a JSON response
    return JsonResponse({'csrfToken': csrf_token})
