from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from users.models import CustomUser
from .serializers import UserSerializer, UserProfileSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed (admins only).
    """
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for the logged-in user to view and update their profile.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the profile of the currently authenticated user
        return self.request.user

    # Optionally override update/partial_update for custom logic
    # def update(self, request, *args, **kwargs):
    #     ...
