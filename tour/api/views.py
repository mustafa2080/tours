from django.db.models import Prefetch, Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from tour.models import Tour, Destination, Category, Activity
from .serializers import (
    TourSerializer, DestinationSerializer, CategorySerializer,
    ActivitySerializer, TourListSerializer
)
from .pagination import OptimizedPageNumberPagination, LargeResultsSetPagination
from .decorators import method_cache, method_cache_per_user


@method_decorator(cache_page(60*5, cache='api'), name='list')  # Cache list for 5 minutes
@method_decorator(cache_page(60*15, cache='api'), name='retrieve')  # Cache detail for 15 minutes
class TourViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Tours with optimized performance."""
    queryset = Tour.objects.filter(is_active=True)
    serializer_class = TourSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = OptimizedPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'destination', 'duration', 'price_range']
    search_fields = ['title', 'description', 'destination__name', 'category__name']
    ordering_fields = ['price', 'duration', 'created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        """
        queryset = Tour.objects.filter(is_active=True)

        # Add select_related for foreign keys
        queryset = queryset.select_related('destination', 'category')

        # Add prefetch_related for many-to-many relationships
        queryset = queryset.prefetch_related(
            'activities',
            'images',
            Prefetch('reviews', queryset=self.get_active_reviews())
        )

        # Add annotations for calculated fields
        queryset = queryset.annotate(
            review_count=Count('reviews', distinct=True),
            avg_rating=Avg('reviews__rating')
        )

        return queryset

    def get_active_reviews(self):
        """Get only approved reviews."""
        from reviews.models import Review
        return Review.objects.filter(is_approved=True)

    def get_serializer_class(self):
        """
        Use a different serializer for list view to improve performance.
        """
        if self.action == 'list':
            return TourListSerializer
        return TourSerializer

    def list(self, request, *args, **kwargs):
        """
        Optimized list view with caching.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Optimized detail view with caching.
        """
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(60*30, cache='api'))  # Cache for 30 minutes
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Return featured tours.
        """
        featured_tours = self.get_queryset().filter(is_featured=True)[:6]
        serializer = TourListSerializer(featured_tours, many=True, context={'request': request})
        return Response(serializer.data)

    @method_decorator(cache_page(60*30, cache='api'))  # Cache for 30 minutes
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Return popular tours based on booking count.
        """
        popular_tours = self.get_queryset().order_by('-booking_count')[:6]
        serializer = TourListSerializer(popular_tours, many=True, context={'request': request})
        return Response(serializer.data)


@method_decorator(cache_page(60*60), name='dispatch')  # Cache for 1 hour
class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Destinations with caching."""
    queryset = Destination.objects.filter(is_active=True)
    serializer_class = DestinationSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = LargeResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'country']
    ordering_fields = ['name', 'country']

    def get_queryset(self):
        """
        Optimize queryset with annotations.
        """
        return Destination.objects.filter(is_active=True).annotate(
            tour_count=Count('tours', distinct=True)
        )


@method_decorator(cache_page(60*60*24), name='dispatch')  # Cache for 24 hours
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Tour Categories with caching."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """
        Optimize queryset with annotations.
        """
        return Category.objects.filter(is_active=True).annotate(
            tour_count=Count('tours', distinct=True)
        )


@method_decorator(cache_page(60*60*24), name='dispatch')  # Cache for 24 hours
class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing Tour Activities with caching."""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LargeResultsSetPagination