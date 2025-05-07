from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking') # Use basename='booking'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
