from rest_framework import serializers
from ..models import (
    Destination, DestinationImage, Category, Activity, Tour, TourImage,
    TourDate, TourGuide, TourItinerary, TourFAQ, Promotion
)
from users.models import CustomUser


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for user information"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'profile_image']

    def get_full_name(self, obj):
        return obj.get_full_name()


class DestinationImageSerializer(serializers.ModelSerializer):
    """Serializer for destination images"""
    class Meta:
        model = DestinationImage
        fields = ['id', 'image', 'caption', 'is_main']


class DestinationMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for destinations (used in nested relationships)"""
    class Meta:
        model = Destination
        fields = ['id', 'name', 'slug', 'cover_image', 'country', 'city']


class DestinationSerializer(serializers.ModelSerializer):
    """Full serializer for destinations"""
    images = DestinationImageSerializer(many=True, read_only=True)
    tour_count = serializers.SerializerMethodField()

    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image', 'country',
            'city', 'is_featured', 'images', 'tour_count'
        ]

    def get_tour_count(self, obj):
        return obj.tours.filter(is_active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for tour categories"""
    tour_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'tour_count']

    def get_tour_count(self, obj):
        return obj.tours.filter(is_active=True).count()


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for activities"""
    class Meta:
        model = Activity
        fields = ['id', 'name', 'icon', 'description']


class TourGuideSerializer(serializers.ModelSerializer):
    """Serializer for tour guides"""
    user = UserMinimalSerializer(read_only=True)
    speciality = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = TourGuide
        fields = [
            'id', 'user', 'bio', 'profile_image', 'years_experience',
            'languages', 'speciality', 'rating'
        ]


class TourImageSerializer(serializers.ModelSerializer):
    """Serializer for tour images"""
    class Meta:
        model = TourImage
        fields = ['id', 'image', 'caption', 'is_main']


class TourItinerarySerializer(serializers.ModelSerializer):
    """Serializer for tour itineraries"""
    class Meta:
        model = TourItinerary
        fields = ['id', 'day', 'title', 'description', 'meals', 'accommodation']


class TourFAQSerializer(serializers.ModelSerializer):
    """Serializer for tour FAQs"""
    class Meta:
        model = TourFAQ
        fields = ['id', 'question', 'answer', 'order']


class TourDateSerializer(serializers.ModelSerializer):
    """Serializer for tour dates"""
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = TourDate
        fields = ['id', 'start_date', 'end_date', 'available_seats', 'is_available']

    def get_is_available(self, obj):
        return obj.is_active and obj.available_seats > 0


class TourListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for tour lists with minimal data.
    Used for list views to improve performance.
    """
    destination_name = serializers.CharField(source='destination.name')
    destination_slug = serializers.CharField(source='destination.slug')
    destination_country = serializers.CharField(source='destination.country')
    category_name = serializers.CharField(source='category.name')
    category_slug = serializers.CharField(source='category.slug')
    discount_percentage = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tour
        fields = [
            'id', 'name', 'slug', 'short_description',
            'destination_name', 'destination_slug', 'destination_country',
            'category_name', 'category_slug',
            'duration_days', 'duration_nights', 'price',
            'discount_price', 'cover_image', 'discount_percentage',
            'avg_rating', 'review_count'
        ]


class TourMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for tours (used in lists)"""
    destination = DestinationMinimalSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'name', 'slug', 'short_description', 'destination',
            'categories', 'duration_days', 'duration_nights', 'price',
            'discount_price', 'cover_image', 'discount_percentage'
        ]

    def get_discount_percentage(self, obj):
        return obj.discount_percentage


class TourSerializer(serializers.ModelSerializer):
    """
    Full serializer for tours with optimized performance.
    Uses annotations from the queryset to avoid additional database queries.
    """
    destination = DestinationSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    images = TourImageSerializer(many=True, read_only=True)
    itinerary = TourItinerarySerializer(many=True, read_only=True)
    faqs = TourFAQSerializer(many=True, read_only=True)
    dates = TourDateSerializer(many=True, read_only=True)

    # Use annotated fields from the queryset
    review_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    # Add additional fields for better API responses
    available_dates_count = serializers.SerializerMethodField()
    next_available_date = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'destination', 'category', 'categories', 'activities', 'duration_days',
            'duration_nights', 'price', 'discount_price', 'currency',
            'max_people', 'min_age', 'difficulty', 'included_services',
            'excluded_services', 'meeting_point', 'cover_image',
            'highlight_video', 'map_location', 'latitude', 'longitude',
            'images', 'itinerary', 'faqs', 'dates', 'is_featured',
            'review_count', 'avg_rating', 'discount_percentage',
            'available_dates_count', 'next_available_date'
        ]

    def get_available_dates_count(self, obj):
        """Get count of available dates for this tour."""
        return obj.dates.filter(is_active=True, available_seats__gt=0).count()

    def get_next_available_date(self, obj):
        """Get the next available date for this tour."""
        from django.utils import timezone

        next_date = obj.dates.filter(
            is_active=True,
            available_seats__gt=0,
            start_date__gte=timezone.now().date()
        ).order_by('start_date').first()

        if next_date:
            return TourDateSerializer(next_date).data
        return None


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for promotions"""
    tours = TourMinimalSerializer(many=True, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'code', 'tours', 'discount_percentage',
            'description', 'start_date', 'end_date', 'is_valid'
        ]
