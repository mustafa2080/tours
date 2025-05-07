from django.urls import path
from . import views
from reviews.views import TourReviewCreateView

app_name = 'tour'

urlpatterns = [
    # Tour list and detail views
    path('', views.TourListView.as_view(), name='tour_list'),
    
    # Search and filter views - MOVED BEFORE detail view
    path('search/', views.TourSearchView.as_view(), name='tour_search'),
    path('filter/', views.TourFilterView.as_view(), name='tour_filter'),
    
    # Tour detail view - MOVED AFTER search view
    path('<slug:slug>/', views.TourDetailView.as_view(), name='tour_detail'),
    
    # Destination views
    path('destinations/', views.DestinationListView.as_view(), name='destination_list'),
    path('destinations/<slug:slug>/', views.DestinationDetailView.as_view(), name='destination_detail'),
    
    # Category view
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Tour reviews
    path('<slug:slug>/review/', TourReviewCreateView.as_view(), name='tour_review_create'),
    
    # Featured/Special tours
    path('featured/', views.FeaturedToursView.as_view(), name='featured_tours'),
    path('promotions/', views.PromotionsView.as_view(), name='promotions'),
]
