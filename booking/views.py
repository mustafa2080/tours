from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json
import uuid
import requests
import logging
import traceback
from datetime import datetime, date, timedelta

from .models import Booking
from .forms import BookingForm
from tour.models import Tour
from payments.models import Payment
from payments.paypal import PayPalClient

logger = logging.getLogger(__name__)

# Basic CRUD views using Django's generic class-based views

class BookingListView(LoginRequiredMixin, ListView):
    """
    Displays a list of bookings for the currently logged-in user.
    """
    model = Booking
    template_name = 'booking/booking_list.html' # Needs to be created
    context_object_name = 'bookings'
    paginate_by = 10 # Optional pagination

    def get_queryset(self):
        # Filter bookings to show only those belonging to the logged-in user
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')
        # Placeholder removed

class BookingDetailView(LoginRequiredMixin, DetailView):
    """
    Displays details of a specific booking.
    Ensures the user viewing the booking is the one who made it.
    """
    model = Booking
    template_name = 'booking/booking_detail.html' # Needs to be created
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only see their own bookings
        return Booking.objects.filter(user=self.request.user)
        # Placeholder removed

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking/booking_form.html'

    def get_initial(self):
        initial = super().get_initial()
        # Get participants count from query parameters
        participants = self.request.GET.get('participants', '1')
        try:
            participants = int(participants)
            if participants < 1:
                participants = 1
        except (ValueError, TypeError):
            participants = 1

        initial['num_adults'] = participants
        return initial

    def form_valid(self, form):
        # Assign the logged-in user to the booking
        form.instance.user = self.request.user

        # Get the tour
        tour_id = self.kwargs.get('tour_id')
        if not tour_id:
            messages.error(self.request, _("Tour information is missing."))
            return self.form_invalid(form)

        tour = get_object_or_404(Tour, pk=tour_id)
        form.instance.tour = tour

        # Calculate prices
        num_adults = form.cleaned_data.get('num_adults', 1)
        num_children = form.cleaned_data.get('num_children', 0)

        # Calculate using tour prices
        regular_price = tour.price
        discounted_price = tour.discount_price if tour.has_discount else tour.price

        # Calculate subtotal (based on regular price)
        adult_subtotal = regular_price * num_adults
        child_subtotal = regular_price * Decimal('0.5') * num_children
        subtotal = adult_subtotal + child_subtotal

        # Calculate discount if applicable
        discount_amount = 0
        if tour.has_discount:
            discount_per_adult = regular_price - discounted_price
            discount_per_child = discount_per_adult * Decimal('0.5')
            discount_amount = (discount_per_adult * num_adults) + (discount_per_child * num_children)

        # Calculate total price
        total_price = subtotal - discount_amount

        # Set the calculated values
        form.instance.subtotal = subtotal
        form.instance.discount_amount = discount_amount
        form.instance.total_price = total_price

        # Save the booking
        self.object = form.save()

        # For AJAX requests (from the booking form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'booking_id': self.object.id,
                'total_price': str(total_price),
                'currency_code': self.request.session.get('currency_code', 'USD'),
                'message': _("Booking created successfully! Proceeding to payment...")
            })

        # For regular form submissions
        messages.success(self.request, _("Booking created successfully! Please proceed to payment."))
        return redirect('booking:booking_confirmation_steps', pk=self.object.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_id = self.kwargs.get('tour_id')

        if tour_id:
            tour = get_object_or_404(Tour, pk=tour_id)
            context['tour'] = tour
            context['tour_name'] = tour.name
            context['tour_price'] = float(tour.price)
            context['tour_discount_price'] = float(tour.discount_price) if tour.has_discount else float(tour.price)
            context['tour_has_discount'] = tour.has_discount
            context['tour_destination'] = str(tour.destination)
            context['tour_duration_days'] = tour.duration_days
            context['tour_duration_nights'] = tour.duration_nights

            # Get participants count from query parameters
            participants = self.request.GET.get('participants', '1')
            try:
                participants = int(participants)
                if participants < 1:
                    participants = 1
            except (ValueError, TypeError):
                participants = 1

            # Set initial values for the form
            self.initial['num_adults'] = participants

            # Add to context for display
            context['initial_participants'] = participants

            # Print debug information
            print(f"Received participants count: {participants}")
            print(f"Request GET parameters: {self.request.GET}")
            print(f"Setting initial num_adults to: {participants}")

            # Force the form to use this value
            if hasattr(self, 'object') and self.object:
                self.object.num_adults = participants

            # Add currency code
            context['currency_code'] = self.request.session.get('currency_code', 'USD')

            # Add PayPal settings
            context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID if hasattr(settings, 'PAYPAL_CLIENT_ID') else "sb"
            context['paypal_mode'] = settings.PAYPAL_MODE if hasattr(settings, 'PAYPAL_MODE') else "sandbox"

            # Add company information
            context['site_name'] = settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else "Tourism Company"
            context['company_address'] = settings.COMPANY_ADDRESS if hasattr(settings, 'COMPANY_ADDRESS') else "123 Tourism Street"
            context['company_email'] = settings.COMPANY_EMAIL if hasattr(settings, 'COMPANY_EMAIL') else "info@tourismcompany.com"
            context['company_phone'] = settings.COMPANY_PHONE if hasattr(settings, 'COMPANY_PHONE') else "+1 234 567 890"

            # Add today's date for date picker
            context['today'] = date.today()

            # Calculate child price (half of adult price)
            context['child_price'] = float(tour.discount_price) * 0.5 if tour.has_discount else float(tour.price) * 0.5

            # Calculate discount amount for display
            if tour.has_discount:
                # Get participants count from query parameters
                participants = self.request.GET.get('participants', '1')
                try:
                    participants = int(participants)
                    if participants < 1:
                        participants = 1
                except (ValueError, TypeError):
                    participants = 1

                # Calculate discount percentage
                discount_percentage = tour.discount_percentage

                # Calculate discount per person using the percentage
                discount_per_person = float(tour.price) * (discount_percentage / 100)

                # Calculate total discount for all participants
                total_discount = discount_per_person * participants

                # Log detailed discount calculation
                print('Discount calculation in BookingCreateView:', {
                    'tour_price': float(tour.price),
                    'discount_percentage': discount_percentage,
                    'discount_per_person': discount_per_person,
                    'participants': participants,
                    'total_discount': total_discount
                })

                # Store both the per-person discount and total discount
                context['discount_per_person'] = discount_per_person
                context['discount_amount'] = total_discount
                context['initial_participants'] = participants

        return context

class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """
    Handles updating an existing booking.
    Restricted to the user who made the booking.
    """
    model = Booking
    form_class = BookingForm
    template_name = 'booking/booking_confirmation_steps.html' # Using the steps template with invoice and payment
    success_url = reverse_lazy('booking:booking_list')
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only edit their own bookings
        return Booking.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Add tour information to context if creating booking from a tour page
            tour_id = self.kwargs.get('tour_id')
            if tour_id:
                # Get the tour with all related data
                tour = get_object_or_404(Tour.objects.select_related('destination'), pk=tour_id)
                context['tour'] = tour

                # Get currency code from session or default
                currency_code = self.request.session.get('currency_code', 'USD')

                # Calculate and add price information
                form = self.get_form()
                if form.is_valid():
                    num_adults = form.cleaned_data.get('num_adults', 1)
                    num_children = form.cleaned_data.get('num_children', 0)
                else:
                    num_adults = form.initial.get('num_adults', 1) if form.initial else 1
                    num_children = form.initial.get('num_children', 0) if form.initial else 0

                # Default values for safety
                tour_price = tour.price if hasattr(tour, 'price') and tour.price is not None else Decimal('0')
                tour_discount_price = tour.discount_price if hasattr(tour, 'discount_price') and tour.discount_price is not None else tour_price
                tour_has_discount = tour.has_discount if hasattr(tour, 'has_discount') else False
                tour_duration_days = tour.duration_days if hasattr(tour, 'duration_days') and tour.duration_days is not None else 7
                tour_duration_nights = tour.duration_nights if hasattr(tour, 'duration_nights') and tour.duration_nights is not None else 6

                # Calculate default dates
                from datetime import date, timedelta
                today = date.today()
                default_start_date = today + timedelta(days=30)
                default_end_date = default_start_date + timedelta(days=tour_duration_days)

                # Calculate prices
                adult_price = tour_discount_price if tour_has_discount else tour_price
                child_price = adult_price * Decimal('0.5')  # Children at half price

                adult_amount = adult_price * num_adults
                child_amount = child_price * num_children

                # Calculate subtotal (based on regular price)
                adult_subtotal = tour_price * num_adults
                child_subtotal = tour_price * Decimal('0.5') * num_children
                subtotal = adult_subtotal + child_subtotal

                # Calculate discount if applicable
                discount_amount = Decimal('0')
                if tour_has_discount and tour_discount_price is not None:
                    discount_per_adult = tour_price - tour_discount_price
                    discount_per_child = discount_per_adult * Decimal('0.5')
                    discount_amount = (discount_per_adult * num_adults) + (discount_per_child * num_children)

                # Calculate total price
                total_price = subtotal - discount_amount

                # Get tour destination name safely
                tour_destination = tour.destination.name if hasattr(tour, 'destination') and tour.destination else 'N/A'

                # Calculate discount percentage if applicable
                tour_discount_percent = None
                if tour_has_discount and tour_price > 0:
                    discount_diff = tour_price - tour_discount_price
                    tour_discount_percent = int((discount_diff / tour_price) * 100)

                # Add to context
                context.update({
                    'num_adults': num_adults,
                    'num_children': num_children,
                    'adult_amount': adult_amount,
                    'child_amount': child_amount,
                    'child_price': child_price,
                    'subtotal': subtotal,
                    'discount_amount': discount_amount,
                    'total_price': total_price,
                    'has_discount': discount_amount > 0,
                    'currency_code': currency_code,
                    'booking_date': today,
                    'start_date': default_start_date,
                    'end_date': default_end_date,
                    'booking_number': f"PREVIEW-{tour.id}",
                    # Add tour data directly to context for debugging and template use
                    'tour_name': tour.name,
                    'tour_price': tour_price,
                    'tour_discount_price': tour_discount_price,
                    'tour_has_discount': tour_has_discount,
                    'tour_discount_percent': tour_discount_percent,
                    'tour_destination': tour_destination,
                    'tour_duration_days': tour_duration_days,
                    'tour_duration_nights': tour_duration_nights,
                })

                # Print debug information
                print(f"Tour data: ID={tour.id}, Name={tour.name}, Price={tour_price}")
                print(f"Tour destination: {tour_destination}")
                print(f"Tour duration: {tour_duration_days} days / {tour_duration_nights} nights")
                print(f"Price calculations: Subtotal={subtotal}, Discount={discount_amount}, Total={total_price}")
                print(f"Context keys: {list(context.keys())}")

                # Print more detailed information about the tour object
                print(f"Tour object details:")
                print(f"  - ID: {tour.id}")
                print(f"  - Name: {tour.name}")
                print(f"  - Price: {tour.price}")
                print(f"  - Discount Price: {tour.discount_price}")
                print(f"  - Has Discount: {tour.has_discount}")
                print(f"  - Destination: {tour_destination}")
                print(f"  - Duration Days: {tour_duration_days}")
                print(f"  - Duration Nights: {tour_duration_nights}")

            # Add today's date for invoice
            context['today'] = date.today() if 'today' not in context else context['today']

            # Add currency code if not already set
            if 'currency_code' not in context:
                context['currency_code'] = self.request.session.get('currency_code', 'USD')

            # Add PayPal settings
            context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID if hasattr(settings, 'PAYPAL_CLIENT_ID') else "sb"
            context['paypal_mode'] = settings.PAYPAL_MODE if hasattr(settings, 'PAYPAL_MODE') else "sandbox"
            context['paypal_test_mode'] = settings.PAYPAL_TEST_MODE if hasattr(settings, 'PAYPAL_TEST_MODE') else True

            # Company information for invoice
            context['site_name'] = settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else "Tourism Company"
            context['company_address'] = settings.COMPANY_ADDRESS if hasattr(settings, 'COMPANY_ADDRESS') else "123 Tourism Street"
            context['company_email'] = settings.COMPANY_EMAIL if hasattr(settings, 'COMPANY_EMAIL') else "info@tourismcompany.com"
            context['company_phone'] = settings.COMPANY_PHONE if hasattr(settings, 'COMPANY_PHONE') else "+1 234 567 890"

            # Bank account details for bank transfer
            context['bank_name'] = settings.BANK_NAME if hasattr(settings, 'BANK_NAME') else "International Bank"
            context['account_name'] = settings.ACCOUNT_NAME if hasattr(settings, 'ACCOUNT_NAME') else "Tourism Company Ltd"
            context['account_number'] = settings.ACCOUNT_NUMBER if hasattr(settings, 'ACCOUNT_NUMBER') else "1234567890"
            context['iban'] = settings.IBAN if hasattr(settings, 'IBAN') else "GB29NWBK60161331926819"
            context['swift_code'] = settings.SWIFT_CODE if hasattr(settings, 'SWIFT_CODE') else "TOURISMBANK"

            # Flag to use payment component
            context['use_payment_component'] = True

            # Debug flag to show template variables
            context['debug_mode'] = True

            # Add page title
            context['page_title'] = _('Create Booking')

        except Exception as e:
            # Log the error
            print(f"Error in BookingCreateView.get_context_data: {str(e)}")
            import traceback
            traceback.print_exc()

            # Add error information to context
            context['error_message'] = str(e)
            context['debug_mode'] = True

        # Always enable debug mode to see what data is being passed
        context['debug_mode'] = True

        # Print context keys for debugging
        print("Context keys in BookingCreateView:", list(context.keys()))

        return context

class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """
    Handles updating an existing booking.
    Restricted to the user who made the booking.
    """
    model = Booking
    form_class = BookingForm
    template_name = 'booking/booking_confirmation_steps.html' # Using the steps template with invoice and payment
    success_url = reverse_lazy('booking:booking_list')
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only edit their own bookings
        return Booking.objects.filter(user=self.request.user)
        # Placeholder removed

    def form_valid(self, form):
        # Recalculate price if relevant fields changed?
        messages.success(self.request, _("Booking updated successfully."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the booking
        booking = self.get_object()
        tour = booking.tour

        # Calculate price details
        num_adults = booking.num_adults
        num_children = booking.num_children

        # Get prices
        regular_price = tour.price
        discounted_price = tour.discount_price if tour.has_discount else tour.price
        child_price = discounted_price * Decimal('0.5')  # Children at half price

        # Calculate amounts
        adult_amount = discounted_price * num_adults
        child_amount = discounted_price * Decimal('0.5') * num_children

        # Get subtotal, discount, and total from booking
        subtotal = booking.subtotal
        discount_amount = booking.discount_amount
        total_price = booking.total_price

        # Generate a booking number if not already set
        booking_number = f"BK-{booking.id:06d}"

        # Add to context
        context['num_adults'] = num_adults
        context['num_children'] = num_children
        context['adult_amount'] = adult_amount
        context['child_amount'] = child_amount
        context['child_price'] = child_price
        context['subtotal'] = subtotal
        context['discount_amount'] = discount_amount
        context['total_price'] = total_price
        context['booking_number'] = booking_number
        context['booking_date'] = booking.booking_date
        context['start_date'] = booking.start_date
        context['end_date'] = booking.end_date

        # Add currency code
        context['currency_code'] = self.request.session.get('currency_code', 'USD')

        # Add PayPal settings
        context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID if hasattr(settings, 'PAYPAL_CLIENT_ID') else ""
        context['paypal_mode'] = settings.PAYPAL_MODE if hasattr(settings, 'PAYPAL_MODE') else "sandbox"
        context['paypal_test_mode'] = settings.PAYPAL_TEST_MODE if hasattr(settings, 'PAYPAL_TEST_MODE') else True

        # Company information for invoice
        context['site_name'] = settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else "Tourism Company"
        context['company_address'] = settings.COMPANY_ADDRESS if hasattr(settings, 'COMPANY_ADDRESS') else "123 Tourism Street"
        context['company_email'] = settings.COMPANY_EMAIL if hasattr(settings, 'COMPANY_EMAIL') else "info@tourismcompany.com"
        context['company_phone'] = settings.COMPANY_PHONE if hasattr(settings, 'COMPANY_PHONE') else "+1 234 567 890"

        # Bank account details for bank transfer
        context['bank_name'] = settings.BANK_NAME if hasattr(settings, 'BANK_NAME') else "International Bank"
        context['account_name'] = settings.ACCOUNT_NAME if hasattr(settings, 'ACCOUNT_NAME') else "Tourism Company Ltd"
        context['account_number'] = settings.ACCOUNT_NUMBER if hasattr(settings, 'ACCOUNT_NUMBER') else "1234567890"
        context['iban'] = settings.IBAN if hasattr(settings, 'IBAN') else "GB29NWBK60161331926819"
        context['swift_code'] = settings.SWIFT_CODE if hasattr(settings, 'SWIFT_CODE') else "TOURISMBANK"

        # Flag to use payment component
        context['use_payment_component'] = True

        context['page_title'] = _('Update Booking')
        return context

# View for cancelling bookings
from django.contrib.auth.decorators import login_required

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user) # Ensure ownership

    if request.method == 'POST':
        # Check if booking is already cancelled
        if booking.status == 'cancelled':
            messages.info(request, _("This booking is already cancelled."))
            return redirect('booking:booking_detail', pk=pk)

        # Allow cancellation
        booking.status = 'cancelled'
        booking.save()

        # Log the cancellation
        logger.info(f"Booking {booking.booking_reference or f'BK-{booking.id:06d}'} cancelled by user {request.user.username}")

        messages.success(request, _("Booking cancelled successfully."))

        # Add refund logic trigger here if applicable
        # If payment was made, handle refund process
        if booking.payment_status == 'completed':
            # Set payment status to refund pending
            booking.payment_status = 'refunded'
            booking.save(update_fields=['payment_status'])

            # You could trigger an actual refund process here
            # For now, just log it
            logger.info(f"Refund process should be initiated for booking {booking.booking_reference or f'BK-{booking.id:06d}'}")

            messages.info(request, _("A refund will be processed for your payment."))

    return redirect('booking:booking_detail', pk=pk)

@login_required
def booking_confirmation(request, pk):
    """
    Display the booking confirmation page after successful payment.
    Redirects to booking_confirmation_steps to avoid duplication.
    """
    # Redirect to booking_confirmation_steps to avoid duplication
    return redirect('booking:booking_confirmation_steps', pk=pk)

@login_required
def booking_confirmation_steps(request, pk):
    """
    Display the booking confirmation steps page with review, payment, and confirmation steps.
    Uses the payment_component.html template for the payment section.
    """
    try:
        # Try to get the booking
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        # Ensure booking has all required data
        if not booking.tour or not booking.num_adults:
            messages.error(request, _("Invalid booking data. Please try creating your booking again."))
            return redirect('booking:booking_list')

        # Calculate price details
        tour = booking.tour
        num_adults = booking.num_adults
        num_children = booking.num_children or 0

        # Get prices
        regular_price = tour.price
        discounted_price = tour.discount_price if tour.has_discount else tour.price
        child_price = discounted_price * Decimal('0.5')  # Children at half price

        # Calculate amounts
        adult_amount = discounted_price * num_adults
        child_amount = child_price * num_children if num_children else Decimal('0')

        # Ensure price calculations
        if not booking.subtotal or not booking.total_price:
            booking.subtotal = (regular_price * num_adults) + (regular_price * Decimal('0.5') * num_children)
            booking.discount_amount = (regular_price - discounted_price) * num_adults
            if num_children:
                booking.discount_amount += (regular_price - child_price) * num_children
            booking.total_price = adult_amount + child_amount
            booking.save()

        # Generate a booking reference number if not set
        if not booking.booking_reference:
            booking.booking_reference = f"BK-{booking.id:06d}"
            booking.save()

        # Get currency code from session or default
        currency_code = request.session.get('currency_code', 'USD')

        # Calculate discount percentage if applicable
        tour_discount_percent = None
        if tour.has_discount and regular_price > 0:
            discount_diff = regular_price - discounted_price
            tour_discount_percent = int((discount_diff / regular_price) * 100)

        context = {
            'booking': booking,
            'tour': tour,
            'regular_price': regular_price,
            'discounted_price': discounted_price,
            'child_price': child_price,
            'adult_amount': adult_amount,
            'child_amount': child_amount,
            'subtotal': booking.subtotal,
            'discount_amount': booking.discount_amount,
            'total_price': booking.total_price,
            'currency_code': currency_code,
            'has_discount': tour.has_discount,
            'tour_discount_percent': tour_discount_percent,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID if hasattr(settings, 'PAYPAL_CLIENT_ID') else None,
            'bank_name': settings.BANK_NAME if hasattr(settings, 'BANK_NAME') else "International Bank",
            'account_name': settings.ACCOUNT_NAME if hasattr(settings, 'ACCOUNT_NAME') else "Tourism Company Ltd",
            'account_number': settings.ACCOUNT_NUMBER if hasattr(settings, 'ACCOUNT_NUMBER') else "1234567890",
            'iban': settings.IBAN if hasattr(settings, 'IBAN') else "GB29NWBK60161331926819",
            'swift_code': settings.SWIFT_CODE if hasattr(settings, 'SWIFT_CODE') else "TOURISMBANK",
            'use_payment_component': True,
            'today': datetime.now().date(),
            'page_title': _('Confirm Your Booking'),
            'company_phone': settings.COMPANY_PHONE if hasattr(settings, 'COMPANY_PHONE') else "+1 234 567 890",
        }

        return render(request, 'booking/booking_confirmation_steps.html', context)

    except Booking.DoesNotExist:
        messages.error(request, _("Booking not found. Please try again or contact support."))
        return redirect('booking:booking_list')
    except Exception as e:
        messages.error(request, _("An error occurred while processing your booking. Please try again or contact support."))
        return redirect('booking:booking_list')

@login_required
def booking_form(request, tour_id):
    """
    Display the booking form page with PayPal integration.
    This view handles both GET requests (displaying the form) and POST requests (processing form submission).
    """
    try:
        # Print request parameters for debugging
        print("Request method:", request.method)
        print("GET parameters:", request.GET)
        print("POST parameters:", request.POST)

        # Get parameters from query string
        participants = request.GET.get('participants', '1')
        subtotal_from_url = request.GET.get('subtotal', '')
        discount_from_url = request.GET.get('discount', '')
        total_from_url = request.GET.get('total', '')

        # Parse participants
        try:
            participants = int(participants)
            if participants < 1:
                participants = 1
        except (ValueError, TypeError):
            participants = 1

        # Parse other values
        try:
            subtotal_from_url = float(subtotal_from_url) if subtotal_from_url else None
            discount_from_url = float(discount_from_url) if discount_from_url else None
            total_from_url = float(total_from_url) if total_from_url else None
        except (ValueError, TypeError):
            subtotal_from_url = None
            discount_from_url = None
            total_from_url = None

        print(f"Received data in booking_form view:")
        print(f"- participants: {participants}")
        print(f"- subtotal: {subtotal_from_url}")
        print(f"- discount: {discount_from_url}")
        print(f"- total: {total_from_url}")

        tour = get_object_or_404(Tour.objects.select_related('destination'), pk=tour_id)
        currency_code = request.session.get('currency_code', 'USD')

        # Handle form submission
        if request.method == 'POST':
            # Extract form data
            start_date_str = request.POST.get('start_date')
            num_adults = int(request.POST.get('num_adults', 1))
            num_children = int(request.POST.get('num_children', 0))
            special_requests = request.POST.get('special_requests', '')

            # Validate data
            if not start_date_str:
                return JsonResponse({'error': 'Start date is required'}, status=400)

            if num_adults < 1:
                return JsonResponse({'error': 'At least one adult is required'}, status=400)

            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = start_date + timedelta(days=tour.duration_days)

            # Calculate prices
            regular_price = tour.price
            discounted_price = tour.discount_price if tour.has_discount else tour.price
            child_price = discounted_price * Decimal('0.5')  # Children at half price

            # Calculate subtotal (based on regular price)
            adult_subtotal = regular_price * num_adults
            child_subtotal = regular_price * Decimal('0.5') * num_children
            subtotal = adult_subtotal + child_subtotal

            # Calculate discount if applicable
            discount_amount = Decimal('0')
            if tour.has_discount:
                discount_per_adult = regular_price - discounted_price
                discount_per_child = discount_per_adult * Decimal('0.5')
                discount_amount = (discount_per_adult * num_adults) + (discount_per_child * num_children)

            # Calculate total price
            total_price = subtotal - discount_amount

            # Create booking
            booking = Booking(
                user=request.user,
                tour=tour,
                start_date=start_date,
                end_date=end_date,
                num_adults=num_adults,
                num_children=num_children,
                special_requests=special_requests,
                subtotal=subtotal,
                discount_amount=discount_amount,
                total_price=total_price,
                status='pending',
                payment_status='pending'
            )
            booking.save()

            # Generate booking reference
            booking.booking_reference = f"BK-{booking.id:06d}"
            booking.save(update_fields=['booking_reference'])

            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'booking_id': booking.id,
                    'booking_reference': booking.booking_reference,
                    'total_price': str(total_price),
                    'currency_code': currency_code,
                    'redirect_url': reverse('booking:booking_confirmation_steps', kwargs={'pk': booking.id})
                })

            # Redirect to confirmation page for non-AJAX requests
            messages.success(request, _("Booking created successfully! Please proceed to payment."))
            return redirect('booking:booking_confirmation_steps', pk=booking.id)

        # Handle GET request (display form)
        # Calculate prices for adults and children
        regular_price = tour.price
        discounted_price = tour.discount_price if tour.has_discount else tour.price
        child_price = discounted_price * Decimal('0.5')  # Children at half price

        # Use participants count from query parameters
        num_adults = participants  # This is already validated above
        print(f"Using participants count: {num_adults} (from query parameter)")
        num_children = 0

        # Calculate amounts
        adult_amount = discounted_price * num_adults
        child_amount = child_price * num_children

        # Use values from URL if available, otherwise calculate
        if subtotal_from_url is not None:
            subtotal = Decimal(str(subtotal_from_url))
            print(f"Using subtotal from URL: {subtotal}")
        else:
            # Calculate subtotal (based on regular price)
            adult_subtotal = regular_price * num_adults
            child_subtotal = regular_price * Decimal('0.5') * num_children
            subtotal = adult_subtotal + child_subtotal
            print(f"Calculated subtotal: {subtotal}")

        # Calculate discount if applicable
        if discount_from_url is not None and tour.has_discount:
            discount_amount = Decimal(str(discount_from_url))
            print(f"Using discount from URL: {discount_amount}")
        else:
            discount_amount = Decimal('0')
            if tour.has_discount:
                # Calculate discount using the discount percentage
                discount_percentage = tour.discount_percentage
                discount_per_person = float(tour.price) * (discount_percentage / 100)
                discount_amount = Decimal(str(discount_per_person)) * num_adults
                print(f"Calculated discount: {discount_amount}")

        # Calculate total price
        if total_from_url is not None:
            total_price = Decimal(str(total_from_url))
            print(f"Using total from URL: {total_price}")
        else:
            total_price = subtotal - discount_amount
            print(f"Calculated total: {total_price}")

        # Calculate default dates
        today = date.today()

        # Calculate discount percentage if applicable
        tour_discount_percent = None
        if tour.has_discount and tour.price > 0:
            discount_diff = tour.price - tour.discount_price
            tour_discount_percent = int((discount_diff / tour.price) * 100)

        # Calculate discount per person for JavaScript
        discount_per_person = 0
        if tour.has_discount:
            discount_percentage = tour.discount_percentage
            discount_per_person = float(tour.price) * (discount_percentage / 100)

        context = {
            'tour': tour,
            'currency_code': currency_code,
            'child_price': float(child_price),
            'discount_amount': float(discount_amount),
            'discount_per_person': discount_per_person,
            'subtotal': float(subtotal),
            'total_price': float(total_price),
            'today': today,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID if hasattr(settings, 'PAYPAL_CLIENT_ID') else "sb",
            'initial_participants': num_adults,
            'tour_price': float(regular_price),
            'tour_discount_price': float(discounted_price),
            'tour_discount_percent': tour_discount_percent,
            'adult_amount': float(adult_amount),
            'child_amount': float(child_amount),
            'has_discount': tour.has_discount,
            'from_tour_detail': True if subtotal_from_url is not None else False,
        }

        return render(request, 'booking/booking_form.html', context)

    except Tour.DoesNotExist:
        messages.error(request, _("Tour not found."))
        return redirect('tour:tour_list')
    except Exception as e:
        import traceback
        print(f"ERROR in booking_form view: {str(e)}")
        traceback.print_exc()
        messages.error(request, _("An error occurred while loading the booking form."))
        return redirect('tour:tour_list')


@login_required
@require_POST
def create_paypal_order(request, booking_id):
    """
    Create a PayPal order for a booking.
    """
    try:
        # Log the request for debugging
        logger.info(f"Creating PayPal order for booking ID: {booking_id}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        logger.info(f"Booking details: tour={booking.tour.name}, price={booking.total_price}, user={request.user.username}")

        # Create or get payment record
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_price,
                'payment_method': 'paypal',
                'status': 'pending'
            }
        )

        # If payment exists but failed, update it
        if not created and payment.status == 'failed':
            payment.status = 'pending'
            payment.save()

        # Initialize PayPal client
        from payments.paypal import PayPalClient
        paypal_client = PayPalClient()

        # Check if we should use test mode
        test_mode = getattr(settings, 'PAYPAL_TEST_MODE', False)
        logger.info(f"PayPal test mode: {test_mode}")

        if test_mode:
            # Use test mode
            logger.info("Using test mode for PayPal integration")
            import uuid
            fake_order_id = f"TEST-ORDER-{uuid.uuid4()}"

            # Store order ID in session for later verification
            request.session['paypal_order_id'] = fake_order_id
            request.session['booking_id'] = booking.id

            # Return a response that will work with PayPal SDK
            return JsonResponse({
                'id': fake_order_id,
                'status': 'CREATED',
                'test_mode': True,
                'links': [
                    {
                        'href': f"https://www.sandbox.paypal.com/checkoutnow?token={fake_order_id}",
                        'rel': 'approve',
                        'method': 'GET'
                    },
                    {
                        'href': f"https://api.sandbox.paypal.com/v2/checkout/orders/{fake_order_id}",
                        'rel': 'self',
                        'method': 'GET'
                    },
                    {
                        'href': f"https://api.sandbox.paypal.com/v2/checkout/orders/{fake_order_id}/capture",
                        'rel': 'capture',
                        'method': 'POST'
                    }
                ]
            })
        else:
            # Use real PayPal API
            logger.info("Using real PayPal API")

            try:
                # Create PayPal order
                order_data = paypal_client.create_order(booking)

                # Store order ID in session for later verification
                request.session['paypal_order_id'] = order_data['id']
                request.session['booking_id'] = booking.id

                logger.info(f"PayPal order created successfully: {order_data['id']}")

                # Return the order data
                return JsonResponse(order_data)
            except Exception as e:
                logger.error(f"Error creating PayPal order: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        logger.error(f"PayPal order creation failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def capture_paypal_payment(request, booking_id):
    """
    Capture payment for an approved PayPal order.
    """
    try:
        # Log the request for debugging
        logger.info(f"Capturing PayPal payment for booking ID: {booking_id}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")

        try:
            data = json.loads(request.body)
            logger.info(f"Request body: {data}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            logger.error(f"Raw request body: {request.body}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

        order_id = data.get('order_id')

        if not order_id:
            return JsonResponse({'error': 'Order ID is required'}, status=400)

        # Check if this is a test mode request
        test_mode = data.get('test_mode', False)

        # Only verify session order ID if not in test mode
        if not test_mode:
            # Verify order ID from session
            session_order_id = request.session.get('paypal_order_id')
            logger.info(f"Session order ID: {session_order_id}, Request order ID: {order_id}")

            if not session_order_id or session_order_id != order_id:
                # For development, we'll allow this to pass even if session doesn't match
                logger.warning("Session order ID doesn't match request order ID, but continuing anyway")
                # return JsonResponse({'error': 'Invalid order ID'}, status=400)

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        logger.info(f"Found booking: {booking.id}, tour: {booking.tour.name}")

        # Check if this is a test mode request
        test_mode = data.get('test_mode', False)

        if test_mode:
            # Create a fake capture response for testing
            import uuid
            capture_id = f"TEST-CAPTURE-{uuid.uuid4()}"

            # Update payment record
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_price,
                    'payment_method': 'paypal',
                    'status': 'completed',
                    'transaction_id': capture_id
                }
            )

            if not created:
                payment.transaction_id = capture_id
                payment.status = 'completed'
                payment.save()

            # Update booking status
            booking.status = 'confirmed'
            booking.payment_status = 'paid'
            booking.payment_date = datetime.now()
            booking.save()

            # Clear session data
            if 'paypal_order_id' in request.session:
                del request.session['paypal_order_id']
            if 'booking_id' in request.session:
                del request.session['booking_id']

            logger.info(f"Test mode: Payment captured successfully with ID: {capture_id}")

            return JsonResponse({
                'success': True,
                'test_mode': True,
                'capture_id': capture_id,
                'booking_reference': booking.booking_reference
            })

        try:
            # Initialize PayPal client
            from payments.paypal import PayPalClient
            paypal_client = PayPalClient()

            # Capture the payment
            logger.info(f"Capturing PayPal payment for order ID: {order_id}")
            capture_data = paypal_client.capture_order(order_id)

            # Update payment record
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_price,
                    'payment_method': 'paypal',
                    'status': 'completed',
                    'transaction_id': capture_data.get('id')
                }
            )

            if not created:
                payment.transaction_id = capture_data.get('id')
                payment.status = 'completed'
                payment.save()

            # Update booking status
            booking.status = 'confirmed'
            booking.payment_status = 'paid'
            booking.payment_date = datetime.now()
            booking.save()

            # Clear session data
            if 'paypal_order_id' in request.session:
                del request.session['paypal_order_id']
            if 'booking_id' in request.session:
                del request.session['booking_id']

            logger.info(f"Payment captured successfully with ID: {capture_data.get('id')}")

            return JsonResponse({
                'success': True,
                'capture_id': capture_data.get('id'),
                'booking_reference': booking.booking_reference
            })
        except Exception as e:
            logger.error(f"Error capturing PayPal payment: {str(e)}")
            logger.error(traceback.format_exc())

            # Return error response
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    except Exception as e:
        logger.error(f"PayPal payment capture failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def payment_success(request, booking_id):
    """
    Display success page after payment is completed.
    """
    try:
        # Log the request for debugging
        logger.info(f"Payment success page for booking ID: {booking_id}")
        logger.info(f"Request path: {request.path}")

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        logger.info(f"Found booking: {booking.id}, status: {booking.status}, payment_status: {booking.payment_status}")

        # For development, always show the success page
        # In production, uncomment the check below
        """
        # Check if booking is already paid
        if booking.payment_status != 'paid':
            messages.warning(request, _("This booking has not been paid for yet."))
            return redirect('booking:booking_form', tour_id=booking.tour.id)
        """

        return render(request, 'booking/payment_success.html', {'booking': booking})
    except Exception as e:
        logger.error(f"Error displaying payment success page: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        messages.error(request, _("An error occurred while displaying the payment success page."))
        return redirect('booking:booking_list')


@login_required
def payment_cancel(request):
    """
    Handle cancellation from PayPal.
    """
    try:
        # Log the request for debugging
        logger.info("Payment cancellation")
        logger.info(f"Request path: {request.path}")

        messages.warning(request, _("Payment was cancelled."))

        # Clear session data
        if 'paypal_order_id' in request.session:
            logger.info(f"Clearing session order ID: {request.session.get('paypal_order_id')}")
            del request.session['paypal_order_id']
        if 'booking_id' in request.session:
            booking_id = request.session.get('booking_id')
            logger.info(f"Clearing session booking ID: {booking_id}")
            del request.session['booking_id']

            # Optionally, update the booking status to 'cancelled' or 'pending'
            try:
                if booking_id:
                    booking = Booking.objects.get(id=booking_id, user=request.user)
                    booking.payment_status = 'pending'
                    booking.save(update_fields=['payment_status'])
                    logger.info(f"Updated booking {booking_id} status to pending")
            except Booking.DoesNotExist:
                logger.warning(f"Booking {booking_id} not found for user {request.user.username}")

        return redirect('booking:booking_list')
    except Exception as e:
        logger.error(f"Error handling payment cancellation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        messages.error(request, _("An error occurred while processing your cancellation."))
        return redirect('booking:booking_list')
