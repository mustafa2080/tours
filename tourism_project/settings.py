import os
import secrets
from pathlib import Path

# Django imports
# Create a simple translation function that doesn't depend on Django
def _(text):
    """
    Simple translation function that returns the text unchanged.
    This avoids dependency on Django's translation module.
    In a real application, this would be replaced by Django's gettext_lazy.
    """
    return text

# Define a function to generate a random secret key
def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    return secrets.token_urlsafe(50)

# Define our own config function to avoid dependency issues
def config(key, default=None, cast=None):
    """
    Get configuration from environment variables with fallback to default values.
    Similar to python-decouple's config function.
    """
    value = os.environ.get(key, default)
    if cast is not None and value is not None:
        try:
            if cast == bool:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', 'yes', '1', 'y')
            return cast(value)
        except (ValueError, TypeError):
            return default
    return value

# Define our own Csv function for parsing comma-separated values
def Csv():
    """
    Parse comma-separated values from environment variables.
    Similar to python-decouple's Csv function.
    """
    def converter(value):
        return value.split(',') if value else []
    return converter

# Define a function to parse database URLs
def parse_db_url(url):
    """
    Parse a database URL into Django database connection settings.
    Similar to dj-database-url's parse function.
    """
    if not url:
        return None

    # Simple parsing for common database URLs
    if url.startswith('sqlite:///'):
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': url[10:],
        }
    elif url.startswith('postgres://') or url.startswith('postgresql://'):
        # Very basic parsing - in production, use the actual dj-database-url package
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',  # Default values
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '5432',
        }

    return None

# Create a simple dj_database_url module-like object
class DatabaseURL:
    def parse(self, url):
        return parse_db_url(url)

dj_database_url = DatabaseURL()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get configuration from environment variables
SECRET_KEY = config('SECRET_KEY', default=get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG is set based on environment variable
DEBUG = config('DEBUG', default=False, cast=bool)

# Allow hosts based on environment variable
# For Railway deployment, we need to include 'healthcheck.railway.app'
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,healthcheck.railway.app', cast=Csv())

# Application definition
INSTALLED_APPS = [
    # Admin Interface
    'jazzmin',
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'crispy_forms',
    'crispy_tailwind',
    'modeltranslation',
    'corsheaders',
    'django_filters',
    'django_ckeditor_5',
    'widget_tweaks',
    # Project apps
    'core',
    'users',
    'tour',
    'booking',
    'blog',
    'reviews',
    'payments',
    'chatbots',
    'analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Session middleware must come before CSRF middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Cache middleware
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    # Compression middleware
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    # Security middleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Performance middleware removed
    # API performance middleware
    'core.middleware.APIPerformanceMiddleware',
    'core.middleware.APIRequestThrottleMiddleware',
    'core.middleware.APIResponseCompressionMiddleware',
    # Login speedup middleware
    'core.middleware.LoginSpeedupMiddleware',
    # Analytics middleware
    'analytics.middleware.AnalyticsMiddleware',
    # Error handling middleware
    'core.middleware.SocialAccountErrorMiddleware',
]

ROOT_URLCONF = 'tourism_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.currency_processor',
                'core.context_processors.loading_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'tourism_project.wsgi.application'

# Database configuration
# Use PostgreSQL for Railway deployment, fallback to SQLite for local development
import os

# Get the DATABASE_URL from environment variables (provided by Railway)
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Use PostgreSQL in production (Railway)
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Available languages
LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
    ('fr', _('French')),
    ('de', _('German')),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('ar', 'en', 'fr', 'de')

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise for static files in production
# Enable in production, disabled for local development
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' if not DEBUG else 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.CustomUser'

# Django AllAuth Configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# AllAuth settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = [
    'email*',
    'first_name*',
    'last_name*',
    'password1*',
    'password2*'
]
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
# SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

ACCOUNT_FORMS = {
    'signup': 'users.forms.CustomSignupForm',
    # Remove the custom login form to use the default one
}

# Social account providers
# These settings are loaded from environment variables for security
# To enable, uncomment this section and set the required environment variables
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': config('GOOGLE_CLIENT_ID', default=''),
#             'secret': config('GOOGLE_CLIENT_SECRET', default=''),
#             'key': ''
#         },
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         'AUTH_PARAMS': {
#             'access_type': 'online',
#         }
#     },
# }

LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Crispy Forms Settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Email settings
# Use SMTP in production, console backend for local development
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Performance optimizations
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    # Caching
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 15,  # 15 minutes
    # Content negotiation
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rest_framework.negotiation.DefaultContentNegotiation',
}

# CORS settings
CORS_ALLOW_CREDENTIALS = True
# In production, restrict CORS to specific origins
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development only
if not DEBUG:
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='https://your-railway-app.up.railway.app', cast=Csv())

# Site URL
# In production, get the URL from environment variables
SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')
SITE_NAME = 'Tourism Website'


# Currency settings
DEFAULT_CURRENCY_CODE = 'USD'
AVAILABLE_CURRENCIES = {
    'USD': {'symbol': '$', 'name': 'US Dollar'},
    'EUR': {'symbol': '€', 'name': 'Euro'},
    'GBP': {'symbol': '£', 'name': 'British Pound'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen'},
    'CNY': {'symbol': '¥', 'name': 'Chinese Yuan'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},
    'EGP': {'symbol': 'E£', 'name': 'Egyptian Pound'},
}

# PayPal settings for local development
PAYPAL_MODE = 'sandbox'  # Always use sandbox for local development
PAYPAL_CLIENT_ID = ''  # Add your sandbox client ID here for testing
PAYPAL_SECRET = ''  # Add your sandbox secret here for testing

# Use SITE_URL for building PayPal URLs
PAYPAL_RETURN_URL = f"{SITE_URL}/en/payments/confirm/"
PAYPAL_CANCEL_URL = f"{SITE_URL}/en/payments/cancel/"

# Enable test mode for offline development
# When True, PayPal integration will use fake responses instead of making real API calls
# This is useful for development without internet connection or when PayPal sandbox is down
PAYPAL_TEST_MODE = True  # Always use test mode for local development

# Celery settings
# In production, use environment variables for broker URL
# In development, use memory broker
CELERY_TASK_ALWAYS_EAGER = DEBUG  # Run tasks synchronously in development
CELERY_TASK_EAGER_PROPAGATES = DEBUG
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='memory://')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='cache')
CELERY_CACHE_BACKEND = 'memory' if DEBUG else 'default'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Chatbot settings for local development
OPENAI_API_KEY = ''  # Add your API key here for testing
DIALOGFLOW_PROJECT_ID = ''  # Add your project ID here for testing

# CKEditor 5 settings
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
            ]
        }
    }
}

CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_UPLOAD_PATH = 'uploads/ckeditor/'

# Cache settings
# Use memory cache in production, dummy cache in development
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Cache middleware
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'tourism'

# Logging for local development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Set to DEBUG for more detailed logs
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # Set to DEBUG to see all database queries
        },
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Changed to False to allow JavaScript access
CSRF_USE_SESSIONS = False  # Changed to False to use cookies instead of sessions
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'  # Custom CSRF failure view

# Security settings
# Enable security settings in production, disable in development
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if not DEBUG else None
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Jazzmin Settings
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Tourism Admin",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Tourism",
    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Tourism Admin",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Tourism Administration",
    # Copyright on the footer
    "copyright": "Tourism Ltd",
    # The model admin to search from the search bar
    "search_model": "users.CustomUser",
    # List of model admins to search from the search bar
    "search_models": ["users.CustomUser", "tour.Tour", "booking.Booking"],
    # Field name on user model that contains avatar image
    "user_avatar": "avatar",
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://example.com/support", "new_window": True},
        {"model": "users.CustomUser"},
        {"model": "tour.Tour"},
    ],
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Custom icons for side menu apps/models
    "icons": {
        "users": "fas fa-users",
        "users.CustomUser": "fas fa-user",
        "tour.Tour": "fas fa-globe",
        "tour.Destination": "fas fa-map-marker",
        "booking.Booking": "fas fa-calendar",
        "blog.Post": "fas fa-newspaper",
        "reviews.Review": "fas fa-star",
        "analytics.SiteVisit": "fas fa-chart-line",
        "analytics.TourView": "fas fa-eye",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
}

# Jazzmin UI Customizer settings
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    }
}

# Loading settings
LOADING_SPINNER_ENABLED = True
LOADING_SPINNER_CSS_CLASSES = 'custom-spinner floating'
LOADING_SPINNER_TEMPLATE = 'partials/loading.html'
LOADING_SPINNER_STYLE = 'dots'  # dots, pulse, bounce, wave
LOADING_SPINNER_SIZE = 'lg'     # sm, md, lg
LOADING_SPINNER_GLASS = True    # Whether to use glass morphism effect
LOADING_SHOW_DELAY_MS = 300
LOADING_HIDE_DELAY_MS = 300

# End of settings file
