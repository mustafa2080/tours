from django.contrib import admin
from .models import Review
from django.utils.translation import gettext_lazy as _


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour', 'rating', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'tour__name']
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = _("Approve selected reviews")

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = _("Disapprove selected reviews")