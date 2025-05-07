from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user') # Admin view

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'), # User's own profile
    # Add other user API specific URLs here (e.g., password change API)
]
