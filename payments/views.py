from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from decimal import Decimal
import json
import logging
from datetime import datetime

from booking.models import Booking
from .models import Payment
from .paypal import PayPalClient

logger = logging.getLogger(__name__)

@login_required
def process_payment(request, booking_id):
    """
    Process payment for a booking.
    Displays payment options and initiates payment process.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check if booking is already paid
    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, _("This booking has already been paid for."))
        return redirect('booking:booking_detail', pk=booking.id)

    # Get payment method from request
    payment_method = request.GET.get('method', 'paypal')  # Default to PayPal

    # Get the regular price from the tour
    regular_price = booking.tour.price

    # Calculate subtotal (regular price for all participants)
    adult_subtotal = regular_price * booking.num_adults
    child_subtotal = regular_price * Decimal('0.5') * booking.num_children  # Children at half price
    subtotal = adult_subtotal + child_subtotal

    # Calculate discount if applicable
    discount = 0
    if booking.tour.has_discount and booking.tour.discount_price is not None:
        # Calculate the discount per person
        discount_per_adult = regular_price - booking.tour.discount_price
        discount_per_child = discount_per_adult * Decimal('0.5')  # Same discount ratio for children
        discount = (discount_per_adult * booking.num_adults) + (discount_per_child * booking.num_children)

    # Calculate total price
    total_price = subtotal - discount

    # Get currency code from session or default to USD
    currency_code = request.session.get('currency_code', 'USD')

    # Create or update payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': total_price,
            'payment_method': payment_method,
            'status': 'pending'
        }
    )

    if not created and payment.status == 'failed':
        payment.status = 'pending'
        payment.amount = total_price
        payment.save()

    # Initialize context with ALL necessary data
    context = {
        'booking': booking,
        'payment': payment,
        'payment_method': payment_method,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'subtotal': subtotal,
        'discount': discount,
        'total_price': total_price,
        'has_discount': discount > 0,
        'currency_code': currency_code,
        'adult_price': regular_price,
        'child_price': regular_price * Decimal('0.5'),
        'num_adults': booking.num_adults,
        'num_children': booking.num_children,
        'adult_subtotal': adult_subtotal,
        'child_subtotal': child_subtotal,
        'tour': booking.tour,
        'booking_date': booking.booking_date,
        'start_date': booking.start_date,
        'end_date': booking.end_date,
        'booking_number': f"BK-{booking.id:06d}"
    }

    # Log the values for debugging
    logger.info(f"Payment page for booking {booking_id}: subtotal={subtotal}, discount={discount}, total={total_price}")

    return render(request, 'payments/process.html', context)

@login_required
def create_paypal_order(request, booking_id):
    """
    Create a PayPal order for a booking.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    try:
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

        # Create PayPal order
        paypal_client = PayPalClient()
        order_data = paypal_client.create_order(booking)

        # Store order ID in session for later verification
        request.session['paypal_order_id'] = order_data['id']
        request.session['booking_id'] = booking.id

        return JsonResponse({
            'id': order_data['id'],
            'links': {link['rel']: link['href'] for link in order_data['links']}
        })

    except Exception as e:
        logger.error(f"PayPal order creation failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def capture_paypal_payment(request):
    """
    Capture payment for an approved PayPal order.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        order_id = data.get('orderID')

        # Verify order ID from session
        session_order_id = request.session.get('paypal_order_id')
        if not session_order_id or session_order_id != order_id:
            return JsonResponse({'error': 'Invalid order ID'}, status=400)

        booking_id = request.session.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        # Capture the payment
        paypal_client = PayPalClient()
        capture_data = paypal_client.capture_order(order_id)

        # Update payment record
        payment = Payment.objects.get(booking=booking)
        payment.transaction_id = capture_data['id']
        payment.status = 'completed'
        payment.save()

        # Update booking status
        booking.status = 'confirmed'
        booking.save()

        # Clear session data
        if 'paypal_order_id' in request.session:
            del request.session['paypal_order_id']
        if 'booking_id' in request.session:
            del request.session['booking_id']

        # Construct the confirmation URL using the booking ID
        confirmation_url = reverse('booking:booking_confirmation', kwargs={'pk': booking.id})

        return JsonResponse({
            'status': 'success',
            'capture_id': capture_data['id'],
            'redirect_url': confirmation_url # Redirect to the specific booking confirmation
        })

    except Exception as e:
        logger.error(f"PayPal payment capture failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def paypal_return(request):
    """
    Handle return from PayPal after payment approval.
    """
    order_id = request.GET.get('token')

    if not order_id:
        messages.error(request, _("Payment process was interrupted. Please try again."))
        return redirect('booking:booking_list')

    try:
        # Get order details
        paypal_client = PayPalClient()
        order_details = paypal_client.get_order_details(order_id)

        # Check if payment is completed
        if order_details['status'] == 'COMPLETED':
            messages.success(request, _("Payment completed successfully!"))
            return redirect('payments:success')
        else:
            # Payment approved but not captured yet
            context = {
                'order_id': order_id,
                'order_status': order_details['status']
            }
            return render(request, 'payments/capture.html', context)

    except Exception as e:
        logger.error(f"Error processing PayPal return: {str(e)}")
        messages.error(request, _("An error occurred while processing your payment. Please contact support."))
        return redirect('payments:failed')

@login_required
def paypal_cancel(request):
    """
    Handle cancellation from PayPal.
    """
    messages.warning(request, _("Payment was cancelled."))
    return redirect('booking:booking_list')

@login_required
def payment_success(request):
    """
    Display success page after payment is completed.
    """
    return render(request, 'payments/success.html')

@login_required
def payment_failed(request):
    """
    Display failure page if payment fails.
    """
    return render(request, 'payments/failed.html')

@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    """
    return HttpResponse(status=200)

@csrf_exempt
def paypal_webhook(request):
    """
    Handle PayPal webhook events.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        event_data = json.loads(request.body)
        event_type = event_data.get('event_type')

        # Log the event
        logger.info(f"Received PayPal webhook: {event_type}")

        # Process different event types
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Payment capture completed
            resource = event_data.get('resource', {})
            transaction_id = resource.get('id')

            # Find the payment by transaction ID
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                payment.status = 'completed'
                payment.save()

                # Update booking status
                booking = payment.booking
                booking.status = 'confirmed'
                booking.save()
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for transaction ID: {transaction_id}")

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {str(e)}")
        return HttpResponse(status=500)

# Direct Payment Implementation (from views_direct.py)

@login_required
def payment_page(request, booking_id):
    """
    Simplified payment page that displays booking details and a PayPal button.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check if booking is already paid
    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, _("This booking has already been paid for."))
        return redirect('booking:booking_detail', pk=booking.id)

    # Calculate prices if not already set
    if not booking.subtotal or not booking.total_price:
        booking.subtotal, booking.discount_amount, booking.total_price = booking.calculate_price()
        booking.save()

    # Ensure we have valid price values
    subtotal = booking.subtotal or Decimal('0.00')
    discount_amount = booking.discount_amount or Decimal('0.00')
    total_price = booking.total_price or Decimal('0.00')

    # Get currency code
    currency_code = request.session.get('currency_code', 'USD')

    # Initialize context with all necessary data
    context = {
        'booking': booking,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_price': total_price,
        'has_discount': discount_amount > 0,
        'currency_code': currency_code,
        'tour': booking.tour,
    }

    # Log the values for debugging
    logger.info(f"Payment page for booking {booking_id}: subtotal={subtotal}, discount={discount_amount}, total={total_price}")

    return render(request, 'payments/payment_direct.html', context)

@login_required
@require_POST
def create_paypal_order_direct(request, booking_id):
    """
    Direct API endpoint to create a PayPal order and return the approval URL.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Ensure booking has valid price
    if not booking.total_price or booking.total_price <= 0:
        booking.subtotal, booking.discount_amount, booking.total_price = booking.calculate_price()
        booking.save()

    try:
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

        # Create PayPal order
        paypal_client = PayPalClient()
        order_data = paypal_client.create_order(booking)

        # Store order ID in session for later verification
        request.session['paypal_order_id'] = order_data['id']
        request.session['booking_id'] = booking.id

        # Find the approval URL
        approve_url = None
        for link in order_data.get('links', []):
            if link.get('rel') == 'approve':
                approve_url = link.get('href')
                break

        if not approve_url:
            logger.error(f"No approval URL found in PayPal order response: {order_data}")
            return JsonResponse({
                'success': False,
                'error': 'No approval URL found in PayPal response'
            }, status=500)

        return JsonResponse({
            'success': True,
            'order_id': order_data['id'],
            'approve_url': approve_url
        })
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def payment_confirm(request):
    """
    Handle return from PayPal after payment approval.
    Captures the payment and updates the booking status.
    """
    # Get the token (order ID) from the query parameters
    order_id = request.GET.get('token')

    if not order_id:
        messages.error(request, _("Payment process was interrupted. No order ID found."))
        return redirect('booking:booking_list')

    # Verify that this order ID matches what we have in session
    session_order_id = request.session.get('paypal_order_id')
    if session_order_id != order_id:
        logger.warning(f"Order ID mismatch: session={session_order_id}, request={order_id}")
        messages.error(request, _("Payment verification failed. Order ID mismatch."))
        return redirect('booking:booking_list')

    booking_id = request.session.get('booking_id')
    if not booking_id:
        messages.error(request, _("Payment process was interrupted. No booking ID found."))
        return redirect('booking:booking_list')

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    try:
        # Capture the payment
        paypal_client = PayPalClient()
        capture_data = paypal_client.capture_order(order_id)

        # Update payment record
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_price,
                'payment_method': 'paypal',
                'status': 'completed',
                'transaction_id': capture_data['id']
            }
        )

        if not created:
            payment.transaction_id = capture_data['id']
            payment.status = 'completed'
            payment.save()

        # Update booking status
        booking.status = 'confirmed'
        booking.save()

        # Clear session data
        if 'paypal_order_id' in request.session:
            del request.session['paypal_order_id']
        if 'booking_id' in request.session:
            del request.session['booking_id']

        messages.success(request, _("Payment completed successfully! Your booking is now confirmed."))

        # Render confirmation page
        return render(request, 'payments/confirmation.html', {
            'booking': booking,
            'payment': payment,
            'transaction_id': payment.transaction_id
        })

    except Exception as e:
        logger.error(f"Error capturing PayPal payment: {str(e)}")
        messages.error(request, _("An error occurred while processing your payment. Please contact support."))
        return redirect('payments:payment_failed')

@login_required
def payment_cancel(request):
    """
    Handle cancellation from PayPal.
    """
    messages.warning(request, _("Payment was cancelled."))

    # Clear session data
    if 'paypal_order_id' in request.session:
        del request.session['paypal_order_id']
    if 'booking_id' in request.session:
        del request.session['booking_id']

    return redirect('booking:booking_list')

# Simple Payment Implementation (from views_simple.py)

@login_required
def simple_payment_page(request, booking_id):
    """
    Very simple payment page that displays booking details and a PayPal button.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check if booking is already paid
    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, _("This booking has already been paid for."))
        return redirect('booking:booking_detail', pk=booking.id)

    # Calculate prices if not already set
    if not booking.subtotal or not booking.total_price:
        booking.subtotal, booking.discount_amount, booking.total_price = booking.calculate_price()
        booking.save()

    # Ensure we have valid price values
    subtotal = booking.subtotal or Decimal('0.00')
    discount_amount = booking.discount_amount or Decimal('0.00')
    total_price = booking.total_price or Decimal('0.00')

    # Get currency code
    currency_code = request.session.get('currency_code', 'USD')

    # Initialize context with all necessary data
    context = {
        'booking': booking,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_price': total_price,
        'has_discount': discount_amount > 0,
        'currency_code': currency_code,
        'tour': booking.tour,
    }

    # Log the values for debugging
    logger.info(f"Simple payment page for booking {booking_id}: subtotal={subtotal}, discount={discount_amount}, total={total_price}")

    return render(request, 'payments/simple_payment.html', context)

@login_required
@require_POST
def create_paypal_order_simple(request, booking_id):
    """
    Simple API endpoint to create a PayPal order and return the approval URL.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Ensure booking has valid price
    if not booking.total_price or booking.total_price <= 0:
        booking.subtotal, booking.discount_amount, booking.total_price = booking.calculate_price()
        booking.save()

    try:
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

        # Create a simple PayPal redirect URL (for testing)
        # In a real implementation, you would call the PayPal API here
        approve_url = f"https://www.sandbox.paypal.com/checkoutnow?token=TEST-{booking_id}"

        # Store booking ID in session for later verification
        request.session['booking_id'] = booking.id

        return JsonResponse({
            'success': True,
            'approve_url': approve_url
        })
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def payment_success_simple(request):
    """
    Simple payment success page.
    """
    # Get the booking ID from session
    booking_id = request.session.get('booking_id')
    if not booking_id:
        messages.error(request, _("Payment process was interrupted. No booking ID found."))
        return redirect('booking:booking_list')

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Update payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_price,
            'payment_method': 'paypal',
            'status': 'completed',
            'transaction_id': f"TEST-TRANS-{booking_id}"
        }
    )

    if not created:
        payment.transaction_id = f"TEST-TRANS-{booking_id}"
        payment.status = 'completed'
        payment.save()

    # Update booking status
    booking.status = 'confirmed'
    booking.save()

    # Clear session data
    if 'booking_id' in request.session:
        del request.session['booking_id']

    messages.success(request, _("Payment completed successfully! Your booking is now confirmed."))

    # Render confirmation page
    return render(request, 'payments/simple_success.html', {
        'booking': booking,
        'payment': payment,
        'transaction_id': payment.transaction_id
    })

@login_required
def payment_cancel_simple(request):
    """
    Simple payment cancel page.
    """
    messages.warning(request, _("Payment was cancelled."))

    # Clear session data
    if 'booking_id' in request.session:
        del request.session['booking_id']

    return redirect('booking:booking_list')
