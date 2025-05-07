from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    """Model for storing currency information"""
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1.0)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class SiteSetting(models.Model):
    """Model to store site-wide settings"""
    site_name = models.CharField(_("Site Name"), max_length=100)
    site_logo = models.ImageField(_("Site Logo"), upload_to='site/')
    email = models.EmailField(_("Contact Email"))
    phone = models.CharField(_("Contact Phone"), max_length=20)
    address = models.TextField(_("Address"))
    facebook_url = models.URLField(_("Facebook URL"), blank=True, null=True)
    twitter_url = models.URLField(_("Twitter URL"), blank=True, null=True)
    instagram_url = models.URLField(_("Instagram URL"), blank=True, null=True)
    youtube_url = models.URLField(_("YouTube URL"), blank=True, null=True)
    default_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, 
                                          related_name='default_currency',
                                          verbose_name=_("Default Currency"))
    about_us = models.TextField(_("About Us"), blank=True)
    privacy_policy = models.TextField(_("Privacy Policy"), blank=True)
    terms_conditions = models.TextField(_("Terms and Conditions"), blank=True)
    
    class Meta:
        verbose_name = _("Site Setting")
        verbose_name_plural = _("Site Settings")
    
    def __str__(self):
        return self.site_name


class FAQ(models.Model):
    """Model to store frequently asked questions"""
    question = models.CharField(_("Question"), max_length=255)
    answer = models.TextField(_("Answer"))
    order = models.PositiveIntegerField(_("Display Order"), default=0)
    is_active = models.BooleanField(_("Is Active"), default=True)
    
    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ['order']
    
    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    """Model to store contact form messages"""
    name = models.CharField(_("Name"), max_length=100)
    email = models.EmailField(_("Email"))
    subject = models.CharField(_("Subject"), max_length=200)
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    is_read = models.BooleanField(_("Is Read"), default=False)
    
    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Notification(models.Model):
    """Model to store notifications for users"""
    NOTIFICATION_TYPES = (
        ('booking', _('Booking')),
        ('payment', _('Payment')),
        ('system', _('System')),
        ('promotion', _('Promotion')),
    )
    
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, 
                             related_name='notifications', verbose_name=_("User"))
    title = models.CharField(_("Title"), max_length=100)
    message = models.TextField(_("Message"))
    notification_type = models.CharField(_("Type"), max_length=20, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    is_read = models.BooleanField(_("Is Read"), default=False)
    
    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type}: {self.title}"


class Newsletter(models.Model):
    """Model to store newsletter subscribers"""
    email = models.EmailField(_("Email"), unique=True)
    subscribed_at = models.DateTimeField(_("Subscribed At"), auto_now_add=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    
    class Meta:
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")
    
    def __str__(self):
        return self.email
