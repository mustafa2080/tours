from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import CustomUser
from .forms import UserProfileForm
from booking.models import Booking
from payments.models import Payment
from reviews.models import Review
from core.models import Notification
from tour.models import Tour
from .models import WishlistItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from allauth.account.views import SignupView, LoginView
from allauth.account.forms import SignupForm, LoginForm

# Safe versions of allauth views that don't depend on django_site table
class SafeSignupView(SignupView):
    """
    A safe version of the SignupView that doesn't depend on the django_site table.
    This is used as a fallback when the site table doesn't exist yet.
    """
    template_name = 'account/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        try:
            # Try to use the original SignupView
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            # If there's any error, log it and show a friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in SignupView: {str(e)}")

            # Show a friendly message
            messages.info(request, _("We're experiencing some technical difficulties. Please try again later."))
            return redirect('core:home')

class SafeLoginView(LoginView):
    """
    A safe version of the LoginView that doesn't depend on the django_site table.
    This is used as a fallback when the site table doesn't exist yet.
    """
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        try:
            # Try to use the original LoginView
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            # If there's any error, log it and show a friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in LoginView: {str(e)}")

            # Show a friendly message
            messages.info(request, _("We're experiencing some technical difficulties. Please try again later."))
            return redirect('core:home')


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """Displays the main user dashboard."""
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get current date for comparison
        today = timezone.now().date()

        # Get upcoming bookings (where booking end date is in the future)
        upcoming_bookings = Booking.objects.filter(
            user=user,
            end_date__gte=today,
            status__in=['confirmed', 'pending']
        ).order_by('start_date')

        # Get completed tours (where booking end date is in the past)
        completed_tours = Booking.objects.filter(
            user=user,
            end_date__lt=today,
            status='confirmed'
        ).order_by('-end_date')

        # Get user reviews count and recent reviews
        user_reviews = Review.objects.filter(user=user).order_by('-created_at')
        user_reviews_count = user_reviews.count()
        recent_reviews = user_reviews[:3]  # Get 3 most recent reviews

        # Get wishlist items count
        wishlist_items = WishlistItem.objects.filter(user=user)
        wishlist_count = wishlist_items.count()

        # Get active bookings count (upcoming and confirmed)
        active_bookings_count = Booking.objects.filter(
            user=user,
            end_date__gte=today,
            status='confirmed'
        ).count()

        # Get total bookings count
        total_bookings_count = Booking.objects.filter(user=user).count()

        # Get completed bookings count
        completed_bookings_count = completed_tours.count()

        # Add all context variables
        context.update({
            'upcoming_bookings': upcoming_bookings,
            'completed_tours': completed_tours,
            'today': today,
            'user_reviews_count': user_reviews_count,
            'recent_reviews': recent_reviews,
            'wishlist_count': wishlist_count,
            'wishlist_items': wishlist_items,
            'active_bookings_count': active_bookings_count,
            'total_bookings_count': total_bookings_count,
            'completed_bookings_count': completed_bookings_count,
            'recent_bookings': Booking.objects.filter(user=user).order_by('-created_at')[:5],
            'recent_payments': Payment.objects.filter(booking__user=user).order_by('-created_at')[:5],
            'unread_notifications': Notification.objects.filter(user=user, is_read=False).count(),
        })

        return context

class UserProfileView(LoginRequiredMixin, TemplateView):
    """Displays the user's profile information."""
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['page_title'] = _("My Profile")
        return context


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Allows users to update their profile information."""
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:user_profile') # Redirect back to profile page
    success_message = _("Your profile has been updated successfully.")

    def get_object(self, queryset=None):
        # Return the currently logged-in user
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Update Profile")
        return context

class UserBookingListView(LoginRequiredMixin, ListView):
    """Displays a list of the user's bookings."""
    model = Booking
    template_name = 'users/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')


class UserBookingDetailView(LoginRequiredMixin, DetailView):
    """Displays details of a specific booking."""
    model = Booking
    template_name = 'users/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only view their own bookings
        return Booking.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()

        # Add related payments
        context['payments'] = Payment.objects.filter(booking=booking).order_by('-created_at')

        # Check if the user has already reviewed this tour
        context['has_review'] = Review.objects.filter(
            user=self.request.user,
            tour=booking.tour
        ).exists()

        # Add today's date for comparison
        context['today'] = timezone.now().date()

        return context

class UserPaymentListView(LoginRequiredMixin, ListView):
    """Displays a list of the user's payments."""
    model = Payment
    template_name = 'users/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        # Assuming Payment model has a ForeignKey to Booking, which has a ForeignKey to User
        return Payment.objects.filter(booking__user=self.request.user).order_by('-created_at')

class UserReviewListView(LoginRequiredMixin, ListView):
    """Displays a list of the user's reviews."""
    model = Review
    template_name = 'users/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by('-created_at')

class UserNotificationListView(LoginRequiredMixin, ListView):
    """Displays a list of the user's notifications."""
    model = Notification
    template_name = 'users/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 15

    def get_queryset(self):
        # Mark notifications as read when viewed? Optional.
        # Notification.objects.filter(user=self.request.user, is_read=False).update(is_read=True)
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

# Add views for password change, email change etc. using django-allauth views or custom ones

@login_required
def toggle_wishlist(request, tour_id):
    """Add or remove a tour from the user's wishlist"""
    tour = get_object_or_404(Tour, id=tour_id)
    wishlist_item = WishlistItem.objects.filter(user=request.user, tour=tour).first()

    if wishlist_item:
        # Remove from wishlist
        wishlist_item.delete()
        messages.success(request, _("Tour removed from your wishlist."))
    else:
        # Add to wishlist
        WishlistItem.objects.create(user=request.user, tour=tour)
        messages.success(request, _("Tour added to your wishlist."))

    # Redirect back to the tour detail page
    return redirect('tour:tour_detail', slug=tour.slug)


class UserWishlistView(LoginRequiredMixin, ListView):
    """Display the user's wishlist"""
    model = WishlistItem
    template_name = 'users/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)


def user_dashboard(request):
    """User dashboard view showing upcoming bookings and completed tours"""
    if not request.user.is_authenticated:
        return redirect('account_login')

    # Get current date for comparison
    today = timezone.now().date()

    # Get upcoming bookings (where tour end date is in the future)
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        tour__end_date__gte=today,
        status__in=['confirmed', 'pending']
    ).order_by('tour__start_date')

    # Get completed tours (where tour end date is in the past)
    completed_tours = Booking.objects.filter(
        user=request.user,
        tour__end_date__lt=today,
        status='confirmed'
    ).order_by('-tour__end_date')

    # Get user reviews count and recent reviews
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    user_reviews_count = user_reviews.count()
    recent_reviews = user_reviews[:3]  # Get 3 most recent reviews

    # Get wishlist items count - use the correct related_name from the WishlistItem model
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    wishlist_count = wishlist_items.count()

    # Get active bookings count (upcoming and confirmed)
    active_bookings_count = Booking.objects.filter(
        user=request.user,
        tour__end_date__gte=today,
        status='confirmed'
    ).count()

    # Get total bookings count
    total_bookings_count = Booking.objects.filter(user=request.user).count()

    # Get completed bookings count
    completed_bookings_count = completed_tours.count()

    context = {
        'upcoming_bookings': upcoming_bookings,
        'completed_tours': completed_tours,
        'today': today,
        'user_reviews_count': user_reviews_count,
        'recent_reviews': recent_reviews,
        'wishlist_count': wishlist_count,
        'wishlist_items': wishlist_items,
        'active_bookings_count': active_bookings_count,
        'total_bookings_count': total_bookings_count,
        'completed_bookings_count': completed_bookings_count,
    }

    return render(request, 'users/dashboard.html', context)
