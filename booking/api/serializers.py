from rest_framework import serializers
from booking.models import Booking
# from users.api.serializers import UserSerializer # Assuming a simple UserSerializer exists
# from tour.api.serializers import TourSerializer # Assuming a simple TourSerializer exists

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    """
    # user = UserSerializer(read_only=True) # Display nested user info, read-only
    # tour = TourSerializer(read_only=True) # Display nested tour info, read-only
    # user_id = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all(), source='user', write_only=True
    # ) # Allow setting user by ID on create/update
    # tour_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Tour.objects.all(), source='tour', write_only=True
    # ) # Allow setting tour by ID on create/update

    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            # 'user',
            # 'tour',
            # 'user_id', # Include if allowing setting user via API
            # 'tour_id', # Include if allowing setting tour via API
            'booking_date',
            'start_date',
            'end_date',
            'num_adults',
            'num_children',
            'total_price',
            'status',
            'status_display', # Human-readable status
            'special_requests',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('booking_date', 'created_at', 'updated_at', 'total_price', 'status') # Status might be updatable via specific actions

    # Add validation or custom logic if needed
    # def validate(self, data):
    #     """
    #     Check that the start date is before the end date.
    #     """
    #     if 'start_date' in data and 'end_date' in data and data['end_date'] < data['start_date']:
    #         raise serializers.ValidationError("End date cannot be before start date.")
    #     return data

    # def create(self, validated_data):
    #     # Custom logic for creation, e.g., calculating price
    #     # tour = validated_data.get('tour')
    #     # num_adults = validated_data.get('num_adults', 1)
    #     # validated_data['total_price'] = tour.price * num_adults # Example calculation
    #     booking = Booking.objects.create(**validated_data)
    #     return booking
