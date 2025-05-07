from rest_framework import serializers
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model (basic info)."""
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'profile_picture', 'date_joined')
        read_only_fields = ('email', 'date_joined') # Email shouldn't be changed via basic profile update

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_picture', 'phone_number', 'address', 'date_of_birth')
        # Add extra validation if needed
