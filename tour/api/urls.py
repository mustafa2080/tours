from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tours', views.TourViewSet, basename='tour')
router.register(r'destinations', views.DestinationViewSet, basename='destination')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'activities', views.ActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
]
