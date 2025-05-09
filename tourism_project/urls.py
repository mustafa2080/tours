"""
URL configuration for tourism_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from core.views import healthcheck
from users.views import SafeSignupView, SafeLoginView

urlpatterns = [
    # Health check - must be outside i18n_patterns to avoid language prefix
    path('health/', healthcheck, name='healthcheck'),
    # Root path health check for Railway
    path('', include(('core.urls', 'core'), namespace='core')),

    # CKEditor 5 URLs
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # API URLs
    path('api/tours/', include('tour.api.urls')),
    path('api/bookings/', include('booking.api.urls')),
    path('api/payments/', include('payments.api.urls')),
    path('api/users/', include('users.api.urls')),
    path('api/blog/', include('blog.api.urls')),
    path('api/reviews/', include('reviews.api.urls')), # Re-added
    path('api/chatbots/', include('chatbots.api.urls')),

    # Django REST Framework authentication
    path('api-auth/', include('rest_framework.urls')),
    path('i18n/setlang/', set_language, name='set_language'),
]


# Wrap these URLs in i18n_patterns to enable translation
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('tours/', include(('tour.urls', 'tour'))), # Explicitly set namespace
    path('bookings/', include(('booking.urls', 'booking'))), # Explicitly set namespace
    path('blog/', include('blog.urls')),
    path('reviews/', include('reviews.urls')), # Re-added
    path('payments/', include('payments.urls')),
    path('chat/', include('chatbots.urls')),

    # Custom auth views that handle missing django_site table
    path('accounts/signup/', SafeSignupView.as_view(), name='account_signup'),
    path('accounts/login/', SafeLoginView.as_view(), name='account_login'),

    # Include the rest of allauth URLs
    path('accounts/', include('allauth.urls')),

    path('users/', include('users.urls', namespace='users')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    prefix_default_language=True,
)

# Serve static and media files in development
if settings.DEBUG:
    # runserver automatically serves static files from STATICFILES_DIRS when DEBUG=True
    # Only add MEDIA files here
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
