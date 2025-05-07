from rest_framework import serializers
from ..models import Review
from tour.api.serializers import UserMinimalSerializer

class ReviewSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'tour', 'user', 'rating', 'comment', 'created_at',
            'is_approved'
        ]
        read_only_fields = ['user', 'is_approved']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
