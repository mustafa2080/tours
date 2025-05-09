import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

class CSRFDebugMiddleware(MiddlewareMixin):
    """
    Middleware to debug CSRF issues by logging CSRF token information.
    """
    
    def process_request(self, request):
        """
        Process the request and log CSRF token information.
        """
        # Only process POST requests
        if request.method == 'POST':
            # Get the CSRF token from the request
            csrf_token = request.META.get('CSRF_COOKIE', None)
            csrf_token_from_post = request.POST.get('csrfmiddlewaretoken', None)
            
            # Log CSRF token information
            logger.info(f"CSRF Debug - Request Path: {request.path}")
            logger.info(f"CSRF Debug - CSRF Cookie: {'Present' if csrf_token else 'Missing'}")
            logger.info(f"CSRF Debug - CSRF Token in POST: {'Present' if csrf_token_from_post else 'Missing'}")
            
            # Check if the CSRF token is missing
            if not csrf_token:
                logger.warning(f"CSRF Debug - CSRF Cookie is missing for POST request to {request.path}")
                # Generate a new CSRF token
                get_token(request)
            
            # Check if the CSRF token in the POST data is missing
            if not csrf_token_from_post:
                logger.warning(f"CSRF Debug - CSRF Token in POST data is missing for request to {request.path}")
        
        return None
    
    def process_response(self, request, response):
        """
        Process the response and ensure CSRF cookie is set.
        """
        # Ensure CSRF cookie is set for all responses
        if not response.cookies.get('csrftoken'):
            # Generate a CSRF token and set it in the cookie
            get_token(request)
            
            # Log that we're setting a CSRF cookie
            logger.info(f"CSRF Debug - Setting CSRF cookie for response to {request.path}")
        
        return response


class CSRFFixMiddleware(MiddlewareMixin):
    """
    Middleware to fix CSRF issues by ensuring CSRF cookie is set.
    """
    
    def process_request(self, request):
        """
        Process the request and ensure CSRF cookie is set.
        """
        # Ensure CSRF cookie is set for all requests
        get_token(request)
        
        return None
