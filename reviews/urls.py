from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('tour/<slug:slug>/review/', views.TourReviewCreateView.as_view(), name='tour_review'),
]