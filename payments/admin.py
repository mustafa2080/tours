from django.contrib import admin
from .models import Payment
from modeltranslation.admin import TranslationAdmin # Import if any fields become translatable

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin): # Inherit from TranslationAdmin if needed
    list_display = ('id', 'booking', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at') # Added booking
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('id', 'transaction_id', 'booking__id', 'booking__user__email', 'booking__tour__name') # Added user email and tour name
    readonly_fields = ('created_at', 'updated_at', 'transaction_id', 'amount', 'booking') # Make booking read-only too
    list_per_page = 25

    # Add actions if needed, e.g., manually mark as refunded
    # actions = ['mark_as_refunded']

    # def mark_as_refunded(self, request, queryset):
    #     # Add logic to interact with payment gateway API for actual refund
    #     updated = queryset.update(status='refunded')
    #     self.message_user(request, f"{updated} payments marked as refunded.")
    # mark_as_refunded.short_description = "Mark selected payments as refunded"
