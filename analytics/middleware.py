import logging
from django.utils import timezone
from django.db import DatabaseError
from .models import SiteVisit

logger = logging.getLogger(__name__)

class AnalyticsMiddleware:
    """Middleware to track site visits"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)

        # Skip tracking for admin, static, and media URLs
        if (request.path.startswith('/admin/') or
            request.path.startswith('/static/') or
            request.path.startswith('/media/')):
            return response

        try:
            # Check if the SiteVisit model is ready (table exists)
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM analytics_sitevisit LIMIT 1")
                table_exists = True
            except Exception:
                table_exists = False

            if not table_exists:
                # Skip tracking if the table doesn't exist yet
                return response

            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Get session key
            session_key = None
            if hasattr(request, 'session') and request.session.session_key:
                session_key = request.session.session_key

            # Create site visit record
            SiteVisit.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                path=request.path,
                referer=request.META.get('HTTP_REFERER', ''),
                # Geolocation data would be added by a background task
            )
        except DatabaseError as e:
            logger.error(f"Database error tracking site visit: {e}")
        except Exception as e:
            logger.error(f"Error tracking site visit: {e}")

        return response
