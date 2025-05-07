from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TourConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tour'
    verbose_name = _('Tour Management')

    def ready(self):
        # Import translation options here to ensure they are registered
        import tour.translation
