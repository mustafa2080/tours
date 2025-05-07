from rest_framework import serializers
from payments.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""
    # Add related fields if needed (e.g., booking details)
    # booking = BookingSerializer() # Example

    class Meta:
        model = Payment
        fields = '__all__' # Or specify fields explicitly
        read_only_fields = ('status', 'transaction_id', 'created_at', 'updated_at') # Fields set by system/gateway
