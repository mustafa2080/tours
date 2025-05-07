import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from .models import Currency, SiteSetting, FAQ, ContactMessage, Notification, Newsletter

# Ensure translation registration happens before admin classes are defined
import core.translation


@admin.register(Currency)
class CurrencyAdmin(TranslationAdmin): # Changed from admin.ModelAdmin
    list_display = ('name', 'code', 'symbol', 'exchange_rate')
    search_fields = ('name', 'code')
    # Add the translated field to list_display if needed, e.g., list_display = ('name_en', 'name_ar', ...)
    # Or rely on the default TranslationAdmin behavior which adds language tabs.


@admin.register(SiteSetting)
class SiteSettingAdmin(TranslationAdmin):
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('site_name', 'site_logo', 'email', 'phone', 'address', 'default_currency')
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url')
        }),
        (_('Content'), {
            'fields': ('about_us', 'privacy_policy', 'terms_conditions')
        }),
    )


@admin.register(FAQ)
class FAQAdmin(TranslationAdmin):
    list_display = ('question', 'order', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = _("Mark selected messages as read")
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = _("Mark selected messages as unread")
    
    actions = [mark_as_read, mark_as_unread]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)

    def export_emails(self, request, queryset):
        """Exports selected newsletter subscriber emails as a CSV file."""
        meta = self.model._meta
        field_names = ['email', 'subscribed_at', 'is_active'] # Fields to include in CSV

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
        writer = csv.writer(response)

        writer.writerow([_(field_name).capitalize() for field_name in field_names]) # Write header row (translated)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_emails.short_description = _("Export selected emails as CSV")

    actions = [export_emails]
