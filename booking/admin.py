from django.contrib import admin
from decimal import Decimal
from .models import Booking
# from .models import Passenger # Uncomment if Passenger model is used
# from modeltranslation.admin import TranslationAdmin # No longer needed for this admin

# No need for explicit import if not using TranslationAdmin here
# import booking.translation

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin): # Reverted to standard ModelAdmin
    list_display = ('id', 'user', 'tour', 'booking_date', 'start_date', 'status', 'total_price') # Added user/tour
    list_filter = ('status', 'booking_date', 'start_date', 'tour') # Added tour filter
    search_fields = ('id', 'user__email', 'tour__name') # Adjust search fields based on actual relations
    readonly_fields = ('booking_date', 'created_at', 'updated_at') # Removed total_price from readonly_fields
    fieldsets = (
        (None, {
            'fields': ('user', 'tour', 'status', 'start_date', 'end_date') # Added user and tour back
        }),
        ('Details', {
            'fields': ('num_adults', 'num_children', 'special_requests', 'total_price'),
        }),
        ('Timestamps', {
            'fields': ('booking_date', 'created_at', 'updated_at'),
            'classes': ('collapse',) # Make this section collapsible
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Calculate total price if not provided
        if not obj.total_price and obj.tour:
            # Get the tour price (use discount_price if available, otherwise regular price)
            if obj.tour.discount_price:
                base_price = obj.tour.discount_price
            else:
                base_price = obj.tour.price
                
            # Calculate total based on adults and children (assuming children pay half price)
            # Convert the float to Decimal to avoid type error
            obj.total_price = (base_price * obj.num_adults) + (base_price * Decimal('0.5') * obj.num_children)
            
        super().save_model(request, obj, form, change)

    # If using Passenger model:
    # inlines = [PassengerInline] # Define PassengerInline below

# Uncomment and define if Passenger model is used
# class PassengerInline(admin.TabularInline):
#     model = Passenger
#     extra = 1 # Number of extra forms to display

# Note: If the Booking model itself needs translatable fields (e.g., a description),
# ensure those fields are registered in booking/translation.py and inherit from TranslationAdmin here.
# Currently, Booking model fields seem non-translatable, so inheriting from admin.ModelAdmin would also work.
# However, using TranslationAdmin is harmless even if no fields are translated yet.
