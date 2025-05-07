from modeltranslation.translator import register, TranslationOptions
from .models import (
    Destination, Category, Activity, Tour, TourItinerary, 
    TourFAQ, Promotion, TourGuide # Added TourGuide, TourReview
)


@register(Destination)
class DestinationTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Activity)
class ActivityTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Tour)
class TourTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description', 'included_services', 
              'excluded_services', 'meeting_point')


@register(TourItinerary)
class TourItineraryTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'meals', 'accommodation')


@register(TourFAQ)
class TourFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(Promotion)
class PromotionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(TourGuide)
class TourGuideTranslationOptions(TranslationOptions):
    fields = ('bio', 'languages') # languages might be tricky if it's a structured field
