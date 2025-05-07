from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteVisit, TourView


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'country', 'path', 'timestamp')
    list_filter = ('timestamp', 'country')
    search_fields = ('user__username', 'ip_address', 'path')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'session_key', 'ip_address', 'user_agent', 'path', 
                      'referer', 'timestamp', 'country', 'city', 'region')


@admin.register(TourView)
class TourViewAdmin(admin.ModelAdmin):
    list_display = ('tour', 'user', 'ip_address', 'country', 'timestamp')
    list_filter = ('timestamp', 'country', 'tour')
    search_fields = ('tour__name', 'user__username', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('tour', 'user', 'session_key', 'ip_address', 'timestamp', 'country')
