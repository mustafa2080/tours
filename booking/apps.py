from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'
    verbose_name = _('Booking Management') # Translatable verbose name

    def ready(self):
        # Import translation options here to ensure they are registered
        import booking.translation
