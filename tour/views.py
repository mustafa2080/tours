from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json # Import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Avg, F, Count, Min, Max # Import Count, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from users.models import WishlistItem # Import WishlistItem

from .models import (
    Destination, Category, Tour, Promotion
)
from reviews.models import Review
from .forms import TourSearchForm
from reviews.forms import ReviewForm # Import ReviewForm from reviews app

# Constants
TOURS_PER_PAGE = 9


class TourListView(ListView):
    """View to display all tours"""
    model = Tour
    template_name = 'tour/tour_list.html'
    context_object_name = 'tours'
    paginate_by = TOURS_PER_PAGE

    def get_queryset(self):
        """Check if the tour_tour table exists before querying"""
        try:
            # Check if the Tour table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM tour_tour LIMIT 1")
                    tour_table_exists = True
                except Exception:
                    tour_table_exists = False

            if not tour_table_exists:
                # Return an empty queryset if the table doesn't exist
                return Tour.objects.none()

            # If table exists, continue with normal query
            queryset = Tour.objects.filter(is_active=True)

            # Apply filters if provided
            filters = {}

            # Search filter
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search) |
                    Q(short_description__icontains=search) |
                    Q(destination__name__icontains=search) |
                    Q(destination__country__icontains=search) |
                    Q(destination__city__icontains=search)
                )

            # Destination filter
            destination = self.request.GET.get('destination')
            if destination:
                filters['destination__slug'] = destination

            # Category filter
            category = self.request.GET.get('category')
            if category:
                filters['categories__slug'] = category

            # Price range filter
            min_price = self.request.GET.get('min_price')
            max_price = self.request.GET.get('max_price')
            if min_price:
                filters['price__gte'] = min_price
            if max_price:
                filters['price__lte'] = max_price

            # Duration filter - simple exact duration matching
            duration = self.request.GET.get('duration')
            if duration:
                try:
                    duration_days = int(duration)
                    # All duration values are treated as exact matches
                    filters['duration_days'] = duration_days
                except (ValueError, TypeError):
                    pass

            # Apply filters
            if filters:
                queryset = queryset.filter(**filters).distinct()

            # Sorting
            sort_by = self.request.GET.get('sort', 'created_at')
            if sort_by == 'price_low':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_high':
                queryset = queryset.order_by('-price')
            elif sort_by == 'name':
                queryset = queryset.order_by('name')
            elif sort_by == 'popularity':
                # Corrected related name for reviews
                queryset = queryset.annotate(avg_rating=Avg('tour_reviews__rating')).order_by('-avg_rating')
            else:
                queryset = queryset.order_by('-created_at')

            return queryset

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in TourListView: {e}")
            return Tour.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destination.objects.filter(is_active=True)
        context['categories'] = Category.objects.filter(is_active=True)

        # Add filter parameters to context for the template
        context['selected_destination'] = self.request.GET.get('destination', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_min_price'] = self.request.GET.get('min_price', '0')
        context['selected_max_price'] = self.request.GET.get('max_price', '10000')
        context['selected_duration'] = self.request.GET.get('duration', '')
        context['selected_sort'] = self.request.GET.get('sort', 'created_at')
        context['search_query'] = self.request.GET.get('search', '')

        # Get min and max price for the price range slider
        try:
            min_db_price = Tour.objects.filter(is_active=True).aggregate(Min('price'))['price__min'] or 0
            max_db_price = Tour.objects.filter(is_active=True).aggregate(Max('price'))['price__max'] or 10000
            context['min_db_price'] = int(min_db_price)
            context['max_db_price'] = int(max_db_price)
        except Exception as e:
            context['min_db_price'] = 0
            context['max_db_price'] = 10000
            print(f"Error getting price range: {e}")

        return context


class TourDetailView(DetailView):
    """View to display details of a specific tour"""
    model = Tour
    template_name = 'tour/tour_detail.html'
    context_object_name = 'tour'

    def dispatch(self, request, *args, **kwargs):
        """Check if the tour_tour table exists before processing the request"""
        try:
            # Check if the Tour table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM tour_tour LIMIT 1")
                    tour_table_exists = True
                except Exception:
                    tour_table_exists = False

            if not tour_table_exists:
                # Redirect to home page if the table doesn't exist
                from django.shortcuts import redirect
                return redirect('core:home')

            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in TourDetailView: {e}")
            from django.shortcuts import redirect
            return redirect('core:home')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Increment view count
        self.object.increment_view_count()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour = self.get_object()

        # Get related tours (same destination or categories)
        related_tours = Tour.objects.filter(
            Q(destination=tour.destination) | Q(categories__in=tour.categories.all())
        ).exclude(id=tour.id).distinct()[:3]

        # Get participants from query parameters or set default to 1
        participants = self.request.GET.get('participants', '1')
        try:
            participants = int(participants)
            if participants < 1:
                participants = 1
        except (ValueError, TypeError):
            participants = 1

        # Add participants to context
        context['participants'] = participants

        # Get tour reviews - Show all reviews for now (remove is_approved filter temporarily)
        reviews_list = tour.tour_reviews.all().order_by('-created_at')

        # Paginate reviews
        paginator = Paginator(reviews_list, 5)  # Show 5 reviews per page
        page = self.request.GET.get('page')
        try:
            reviews = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            reviews = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results
            reviews = paginator.page(paginator.num_pages)

        # Get tour dates
        tour_dates = tour.dates.filter(is_active=True, available_seats__gt=0).order_by('start_date')

        # Check if user has already reviewed this tour - Corrected related name
        user_reviewed = False
        # Check if the tour is in the user's wishlist
        is_in_wishlist = False
        if self.request.user.is_authenticated:
            # Check if user has already reviewed this tour (regardless of approval status)
            user_reviewed = tour.tour_reviews.filter(user=self.request.user).exists()
            is_in_wishlist = WishlistItem.objects.filter(user=self.request.user, tour=tour).exists()

            # If the user has a review, make sure it's approved
            if user_reviewed:
                # Approve the user's review if it exists but is not approved
                user_review = tour.tour_reviews.filter(user=self.request.user).first()
                if user_review and not user_review.is_approved:
                    user_review.is_approved = True
                    user_review.save()

        # Add to context
        context['related_tours'] = related_tours
        context['reviews'] = reviews
        context['tour_dates'] = tour_dates
        context['user_reviewed'] = user_reviewed
        context['is_in_wishlist'] = is_in_wishlist # Add wishlist status to context
        context['review_form'] = ReviewForm() # Use ReviewForm from reviews.forms

        # Calculate rating percentages and counts
        # Check if reviews_list is a QuerySet or a list
        if hasattr(reviews_list, 'count') and callable(reviews_list.count) and not isinstance(reviews_list, list):
            # It's a QuerySet
            total_reviews = reviews_list.count()
            rating_counts_data = reviews_list.values('rating').annotate(count=Count('id')).order_by('-rating')
        else:
            # It's a list (sample reviews)
            total_reviews = len(reviews_list)
            # We can't use values() and annotate() on a list, so we'll count manually
            rating_counts = {}
            for review in reviews_list:
                rating = review.rating
                if rating not in rating_counts:
                    rating_counts[rating] = 0
                rating_counts[rating] += 1

            # Convert to a format similar to what values().annotate() would return
            rating_counts_data = [{'rating': rating, 'count': count} for rating, count in rating_counts.items()]
            # Sort by rating in descending order
            rating_counts_data = sorted(rating_counts_data, key=lambda x: x['rating'], reverse=True)

        # Initialize dictionaries for all ratings (1-5)
        rating_data = {i: (i, 0, 0) for i in range(1, 6)}  # (rating, percentage, count)

        # Process review data
        if total_reviews > 0:
            for item in rating_counts_data:
                rating = item['rating']
                count = item['count']
                percentage = round((count / total_reviews) * 100)
                rating_data[rating] = (rating, percentage, count)

        # Convert to list of tuples for easier template iteration [(5, perc, count), (4, perc, count), ...]
        context['rating_percentages'] = sorted(rating_data.values(), key=lambda x: x[0], reverse=True)
        context['total_reviews'] = total_reviews

        # Add debug info
        context['rating_data_debug'] = {
            'total_reviews': total_reviews,
            'rating_counts_data': list(rating_counts_data),
            'rating_data': rating_data,
        }

        # Calculate average rating
        context['avg_rating'] = tour.get_average_rating()

        # Prepare available dates for Flatpickr
        available_dates_list = []
        for date_obj in tour_dates:
            available_dates_list.append({
                'id': date_obj.id,
                'date': date_obj.start_date.strftime('%Y-%m-%d'), # Format needed by flatpickr
                'display': date_obj.start_date.strftime('%d %b %Y'), # Optional display format
                'seats': date_obj.available_seats
            })
        context['available_dates_json'] = json.dumps(available_dates_list)

        return context


class DestinationListView(ListView):
    """View to display all destinations"""
    model = Destination
    template_name = 'tour/destination_list.html'
    context_object_name = 'destinations'
    paginate_by = TOURS_PER_PAGE
    queryset = Destination.objects.filter(is_active=True)


class DestinationDetailView(DetailView):
    """View to display details of a specific destination"""
    model = Destination
    template_name = 'tour/destination_detail.html'
    context_object_name = 'destination'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination = self.get_object()

        # Get tours for this destination
        tours = destination.tours.filter(is_active=True)

        # Get categories for filter
        categories = Category.objects.filter(tours__destination=destination).distinct()

        # Add to context
        context['tours'] = tours
        context['categories'] = categories

        return context


class CategoryListView(ListView):
    """View to display all categories"""
    model = Category
    template_name = 'tour/category_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.filter(is_active=True)


class CategoryDetailView(DetailView):
    """View to display details of a specific category"""
    model = Category
    template_name = 'tour/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # Get tours in this category
        tours = category.tours.filter(is_active=True)

        # Get destinations for filter
        destinations = Destination.objects.filter(tours__categories=category).distinct()

        # Add to context
        context['tours'] = tours
        context['destinations'] = destinations

        return context


# Add this class to your views.py file
class TourSearchView(ListView):
    """View for searching tours"""
    model = Tour
    template_name = 'tour/tour_search.html'
    context_object_name = 'tours'
    paginate_by = 9  # Adjust as needed

    def get_queryset(self):
        """Check if the tour_tour table exists before querying"""
        try:
            # Check if the Tour table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM tour_tour LIMIT 1")
                    tour_table_exists = True
                except Exception:
                    tour_table_exists = False

            if not tour_table_exists:
                # Return an empty queryset if the table doesn't exist
                return Tour.objects.none()

            # If table exists, continue with normal query
            queryset = Tour.objects.filter(is_active=True)

            # Get the keyword from the request
            keyword = self.request.GET.get('keyword', '')

            # If keyword exists, filter the queryset
            if keyword:
                queryset = queryset.filter(
                    Q(name__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(short_description__icontains=keyword) |
                    Q(destination__name__icontains=keyword) |
                    Q(destination__country__icontains=keyword) |
                    Q(destination__city__icontains=keyword)
                )

            return queryset

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in TourSearchView: {e}")
            return Tour.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the search keyword to the context
        context['search_keyword'] = self.request.GET.get('keyword', '')
        return context


class TourFilterView(TemplateView):
    """View to filter tours with AJAX"""
    template_name = 'tour/tour_filter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filters
        destination_slug = self.request.GET.get('destination')
        category_slug = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        duration = self.request.GET.get('duration')
        sort_by = self.request.GET.get('sort', 'created_at')

        # Start with all active tours
        tours = Tour.objects.filter(is_active=True)

        # Apply filters
        if destination_slug:
            tours = tours.filter(destination__slug=destination_slug)

        if category_slug:
            tours = tours.filter(categories__slug=category_slug)

        if min_price:
            tours = tours.filter(price__gte=min_price)

        if max_price:
            tours = tours.filter(price__lte=max_price)

        if duration:
            try:
                duration_days = int(duration)
                # All duration values are treated as exact matches
                tours = tours.filter(duration_days=duration_days)
            except (ValueError, TypeError):
                pass

        # Apply sorting
        if sort_by == 'price_low':
            tours = tours.order_by('price')
        elif sort_by == 'price_high':
            tours = tours.order_by('-price')
        elif sort_by == 'name':
            tours = tours.order_by('name')
        elif sort_by == 'popularity':
            # Corrected related name for reviews
            tours = tours.annotate(avg_rating=Avg('tour_reviews__rating')).order_by('-avg_rating')
        else:
            tours = tours.order_by('-created_at')

        context['tours'] = tours.distinct()
        return context


class FeaturedToursView(ListView):
    """View to display featured tours"""
    model = Tour
    template_name = 'tour/featured_tours.html'
    context_object_name = 'tours'
    paginate_by = TOURS_PER_PAGE

    def get_queryset(self):
        """Check if the tour_tour table exists before querying"""
        try:
            # Check if the Tour table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM tour_tour LIMIT 1")
                    tour_table_exists = True
                except Exception:
                    tour_table_exists = False

            if not tour_table_exists:
                # Return an empty queryset if the table doesn't exist
                return Tour.objects.none()

            # If table exists, continue with normal query
            return Tour.objects.filter(is_active=True, is_featured=True)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in FeaturedToursView: {e}")
            return Tour.objects.none()


class PromotionsView(ListView):
    """View to display current promotions"""
    model = Promotion
    template_name = 'tour/promotions.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return Promotion.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )
