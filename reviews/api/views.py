from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Review.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        return queryset.select_related('user', 'tour')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
