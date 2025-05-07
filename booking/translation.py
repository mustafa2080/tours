from modeltranslation.translator import register, TranslationOptions
from .models import Booking

# Example: If Booking model had a translatable 'description' field:
# @register(Booking)
# class BookingTranslationOptions(TranslationOptions):
#     fields = ('description',)

# Currently, no fields in the Booking model require translation.
# This file is included for consistency and future expansion.
# If you add translatable fields to Booking or other models in this app,
# register them here following the pattern above.
