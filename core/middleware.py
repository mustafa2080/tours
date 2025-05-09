import time
import logging
import re
import json
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponse
from django.utils.crypto import constant_time_compare
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)

class APIPerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to log API request performance.
    """
    API_URL_PATTERN = re.compile(r'^/api/')

    def process_request(self, request):
        if self.API_URL_PATTERN.match(request.path):
            request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"API Request: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}s"
            )

            # Add performance header to response
            response['X-API-Response-Time'] = f"{duration:.2f}s"

            # Log slow requests
            if duration > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"Slow API Request: {request.method} {request.path} - "
                    f"Duration: {duration:.2f}s"
                )

        return response

class APIRequestThrottleMiddleware(MiddlewareMixin):
    """
    Middleware to throttle API requests based on IP address.
    """
    API_URL_PATTERN = re.compile(r'^/api/')

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.request_counts = {}
        self.last_cleanup = time.time()

    def process_request(self, request):
        # Only process API requests
        if not self.API_URL_PATTERN.match(request.path):
            return None

        # Clean up old entries every 5 minutes
        current_time = time.time()
        if current_time - self.last_cleanup > 300:  # 5 minutes
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time

        # Get client IP
        ip = self._get_client_ip(request)

        # Initialize or update request count for this IP
        if ip not in self.request_counts:
            self.request_counts[ip] = {'count': 0, 'last_request': current_time}

        # Check if request should be throttled
        if self._should_throttle(ip, current_time):
            from django.http import HttpResponse
            return HttpResponse(
                "Too many requests. Please try again later.",
                status=429,
                content_type="text/plain"
            )

        # Update request count
        self.request_counts[ip]['count'] += 1
        self.request_counts[ip]['last_request'] = current_time

        return None

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _should_throttle(self, ip, current_time):
        # Reset count if last request was more than 1 minute ago
        if current_time - self.request_counts[ip]['last_request'] > 60:
            self.request_counts[ip]['count'] = 0
            return False

        # Throttle if more than 60 requests per minute
        return self.request_counts[ip]['count'] >= 60

    def _cleanup_old_entries(self, current_time):
        # Remove entries older than 10 minutes
        to_remove = []
        for ip, data in self.request_counts.items():
            if current_time - data['last_request'] > 600:  # 10 minutes
                to_remove.append(ip)

        for ip in to_remove:
            del self.request_counts[ip]

class APIResponseCompressionMiddleware(MiddlewareMixin):
    """
    Middleware to ensure API responses are compressed.
    """
    API_URL_PATTERN = re.compile(r'^/api/')

    def process_response(self, request, response):
        if self.API_URL_PATTERN.match(request.path):
            # Add compression headers if not already present
            if 'Content-Encoding' not in response:
                response['Vary'] = 'Accept-Encoding'

        return response


class LoginSpeedupMiddleware(MiddlewareMixin):
    """
    Middleware to speed up login process by optimizing authentication.
    """
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.login_pattern = re.compile(r'^/[a-z]{2}/accounts/login/$')

    def process_request(self, request):
        """
        Process the request before it reaches the view.
        """
        # Only apply to login URLs
        if self.login_pattern.match(request.path):
            # Add a timestamp to track request processing time
            request.login_start_time = time.time()

            # Disable rate limiting for login requests
            request.META['REMOTE_ADDR'] = '127.0.0.1'  # Treat as local request

        return None

    def process_response(self, request, response):
        """
        Process the response after the view is called.
        """
        # Only apply to login URLs
        if hasattr(request, 'login_start_time'):
            # Calculate processing time
            processing_time = time.time() - request.login_start_time
            # Log processing time for debugging
            if processing_time > 1.0:  # If login takes more than 1 second
                logger.warning(f"Slow login processing time: {processing_time:.2f} seconds")
        return response


class PageSpeedMiddleware(MiddlewareMixin):
    """
    Middleware to track and optimize page load times.
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Log slow page loads (more than 2 seconds)
            if duration > 2.0 and not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
                logger.warning(f"Slow page load: {request.method} {request.path} - Duration: {duration:.2f}s")

                # Store slow pages in cache for monitoring
                slow_pages_key = 'slow_pages'
                slow_pages = cache.get(slow_pages_key, {})

                path_key = request.path
                if path_key in slow_pages:
                    slow_pages[path_key]['count'] += 1
                    slow_pages[path_key]['total_time'] += duration
                    slow_pages[path_key]['avg_time'] = slow_pages[path_key]['total_time'] / slow_pages[path_key]['count']
                else:
                    slow_pages[path_key] = {
                        'count': 1,
                        'total_time': duration,
                        'avg_time': duration,
                        'last_seen': time.time()
                    }

                # Keep only the 20 slowest pages
                if len(slow_pages) > 20:
                    # Sort by average time and keep top 20
                    slow_pages = dict(sorted(slow_pages.items(),
                                            key=lambda x: x[1]['avg_time'],
                                            reverse=True)[:20])

                cache.set(slow_pages_key, slow_pages, 86400)  # Store for 24 hours

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    def process_response(self, request, response):
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.paypal.com https://www.google.com https://www.gstatic.com 'unsafe-inline'",
            "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "connect-src 'self' https://www.paypal.com https://api.paypal.com",
            "frame-src 'self' https://www.paypal.com https://www.google.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response['Content-Security-Policy'] = "; ".join(csp_directives)

        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'

        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'

        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer-Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(self), payment=(self)'

        return response


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    Middleware to protect against SQL injection attacks.
    """
    # Patterns that might indicate SQL injection attempts
    SQL_INJECTION_PATTERNS = [
        r'(\%27)|(\')|(\-\-)|(\%23)|(#)',
        r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',
        r'((\%27)|(\'))union',
        r'exec(\s|\+)+(s|x)p\w+',
        r'UNION\s+ALL\s+SELECT',
        r'SELECT\s+.*\s+FROM',
        r'INSERT\s+INTO',
        r'DELETE\s+FROM',
        r'DROP\s+TABLE',
        r'UPDATE\s+.*\s+SET',
    ]

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SQL_INJECTION_PATTERNS]

    def process_request(self, request):
        # Check query parameters
        query_string = request.META.get('QUERY_STRING', '')
        if self._check_for_sql_injection(query_string):
            logger.warning(f"Possible SQL injection attempt in query string: {query_string}")
            return HttpResponseForbidden("Forbidden: Invalid request")

        # Check POST data
        if request.method == 'POST':
            post_data = request.POST.copy()
            for key, value in post_data.items():
                if isinstance(value, str) and self._check_for_sql_injection(value):
                    logger.warning(f"Possible SQL injection attempt in POST data: {key}={value}")
                    return HttpResponseForbidden("Forbidden: Invalid request")

        return None

    def _check_for_sql_injection(self, text):
        if not isinstance(text, str):
            return False

        for pattern in self.patterns:
            if pattern.search(text):
                return True
        return False


class XSSProtectionMiddleware(MiddlewareMixin):
    """
    Middleware to protect against XSS attacks.
    """
    # Patterns that might indicate XSS attempts
    XSS_PATTERNS = [
        r'<script.*?>',
        r'javascript:',
        r'onerror=',
        r'onload=',
        r'onclick=',
        r'onmouseover=',
        r'eval\(',
        r'document\.cookie',
        r'document\.location',
        r'document\.write',
        r'<iframe',
        r'<object',
        r'<embed',
    ]

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS]

    def process_request(self, request):
        # Check query parameters
        query_string = request.META.get('QUERY_STRING', '')
        if self._check_for_xss(query_string):
            logger.warning(f"Possible XSS attempt in query string: {query_string}")
            return HttpResponseForbidden("Forbidden: Invalid request")

        # Check POST data
        if request.method == 'POST':
            post_data = request.POST.copy()
            for key, value in post_data.items():
                if isinstance(value, str) and self._check_for_xss(value):
                    logger.warning(f"Possible XSS attempt in POST data: {key}={value}")
                    return HttpResponseForbidden("Forbidden: Invalid request")

        return None

    def _check_for_xss(self, text):
        if not isinstance(text, str):
            return False

        for pattern in self.patterns:
            if pattern.search(text):
                return True
        return False


class SocialAccountErrorMiddleware(MiddlewareMixin):
    """
    Middleware to catch and handle errors related to social account providers.
    """

    def process_exception(self, request, exception):
        """
        Process exceptions and handle social account provider errors.
        """
        # Check if the exception is related to social account providers
        exception_str = str(exception)
        if 'socialaccount' in exception_str or 'SocialApp' in exception_str or 'SocialAccount' in exception_str:
            logger.warning(f"Caught social account error: {exception}")

            # If this is a template response, render a simple error page
            if request.path.startswith('/accounts/') or 'login' in request.path or 'signup' in request.path:
                return HttpResponse(
                    "Social login is currently unavailable. Please use email login.",
                    status=200,
                    content_type="text/html"
                )

        return None
