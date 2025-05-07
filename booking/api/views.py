from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from booking.models import Booking
from .serializers import BookingSerializer
# from .permissions import IsOwnerOrReadOnly # Custom permission if needed

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    Provides standard CRUD operations.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access

    def get_queryset(self):
        """
        This view should return a list of all the bookings
        for the currently authenticated user.
        """
        # user = self.request.user
        # return Booking.objects.filter(user=user)
        # Placeholder until user relation is added and permissions refined
        return Booking.objects.all()

    def perform_create(self, serializer):
        """
        Associate the booking with the requesting user upon creation.
        Calculate price or perform other actions.
        """
        # serializer.save(user=self.request.user)
        # Add price calculation logic here if needed
        serializer.save() # Placeholder

    # Example custom action to confirm a booking (adjust logic as needed)
    # @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser]) # Example: Only admin can confirm
    # def confirm(self, request, pk=None):
    #     booking = self.get_object()
    #     if booking.status == 'pending':
    #         booking.status = 'confirmed'
    #         booking.save()
    #         # Trigger notification or payment capture here
    #         return Response({'status': 'booking confirmed'}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'status': 'booking cannot be confirmed'}, status=status.HTTP_400_BAD_REQUEST)

    # Example custom action to cancel a booking
    # @action(detail=True, methods=['post'])
    # def cancel(self, request, pk=None):
    #     booking = self.get_object()
    #     # Add permission check: only owner or admin can cancel
    #     if booking.user != request.user and not request.user.is_staff:
    #          return Response({'detail': 'Not authorized to cancel this booking.'}, status=status.HTTP_403_FORBIDDEN)

    #     if booking.status in ['pending', 'confirmed']:
    #         booking.status = 'cancelled'
    #         booking.save()
    #         # Trigger refund process if applicable
    #         return Response({'status': 'booking cancelled'}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'status': 'booking cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
