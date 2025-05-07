from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from payments.models import Payment
from booking.models import Booking
from payments.paypal import PayPalClient
from .serializers import PaymentSerializer
import logging

logger = logging.getLogger(__name__)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows payments to be viewed.
    (Typically payments are created via gateway interactions, not direct API POST)
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser] # Or custom permission for user to view own payments

    # Add filtering to show only payments related to the requesting user if needed
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:
    #         return Payment.objects.all()
    #     return Payment.objects.filter(booking__user=user)

class CreatePayPalOrderAPIView(APIView):
    """
    API endpoint to create a PayPal order and return the approval URL.
    This implements a backend-driven PayPal flow where the order is created on the server
    and the frontend simply redirects to the PayPal approval URL.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response(
                {"error": "Booking ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the booking and verify ownership
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
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
            
            # Extract the approval URL from the order response
            approval_url = None
            for link in order_data.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            if not approval_url:
                logger.error(f"No approval URL found in PayPal order response: {order_data}")
                return Response(
                    {"error": "Failed to get PayPal approval URL"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Return the approval URL
            return Response({
                "success": True,
                "order_id": order_data['id'],
                "approve_url": approval_url
            })
            
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating PayPal order: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
