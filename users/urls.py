from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('bookings/', views.UserBookingListView.as_view(), name='user_booking_list'),
    path('bookings/<int:pk>/', views.UserBookingDetailView.as_view(), name='user_booking_detail'),
    path('payments/', views.UserPaymentListView.as_view(), name='user_payment_list'),
    path('reviews/', views.UserReviewListView.as_view(), name='user_review_list'),
    path('notifications/', views.UserNotificationListView.as_view(), name='user_notification_list'),
    path('wishlist/', views.UserWishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:tour_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
