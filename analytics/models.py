from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class SiteVisit(models.Model):
    """Model to track site visits with geolocation data"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='site_visits',
        verbose_name=_("User")
    )
    session_key = models.CharField(_("Session Key"), max_length=40, blank=True, null=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    user_agent = models.TextField(_("User Agent"), blank=True)
    path = models.CharField(_("Path"), max_length=255)
    referer = models.URLField(_("Referer"), blank=True, null=True)
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    
    # Geolocation data
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    region = models.CharField(_("Region"), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Site Visit")
        verbose_name_plural = _("Site Visits")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['country']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.path} - {self.timestamp}"
        return f"{self.ip_address} - {self.path} - {self.timestamp}"


class TourView(models.Model):
    """Model to track tour page views"""
    tour = models.ForeignKey(
        'tour.Tour', 
        on_delete=models.CASCADE, 
        related_name='analytics_views',
        verbose_name=_("Tour")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tour_views',
        verbose_name=_("User")
    )
    session_key = models.CharField(_("Session Key"), max_length=40, blank=True, null=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Tour View")
        verbose_name_plural = _("Tour Views")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['tour']),
        ]
        unique_together = [
            ('tour', 'ip_address', 'user', 'session_key')
        ]
    
    def __str__(self):
        return f"{self.tour.name} - {self.timestamp}"
