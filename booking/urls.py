from django.urls import path
from . import views

app_name = 'booking' # Define the namespace

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    # Path for creating a booking, linked from a specific tour
    path('new/tour/<int:tour_id>/', views.BookingCreateView.as_view(), name='booking_create'),
    # Booking form with direct payment integration (redirects to booking_create)
    path('form/tour/<int:tour_id>/', views.booking_form, name='booking_form'),
    path('<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('<int:pk>/cancel/', views.cancel_booking, name='booking_cancel'),
    path('<int:pk>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    # Path for booking confirmation with steps
    path('<int:pk>/steps/', views.booking_confirmation_steps, name='booking_confirmation_steps'),

    # Payment processing endpoints
    path('<int:booking_id>/payment/paypal/create/', views.create_paypal_order, name='create_paypal_order'),
    path('<int:booking_id>/payment/paypal/capture/', views.capture_paypal_payment, name='capture_paypal_payment'),
    path('<int:booking_id>/payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
]
