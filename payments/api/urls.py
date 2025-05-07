from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    # PayPal API endpoints
    path('create-paypal-order/', views.CreatePayPalOrderAPIView.as_view(), name='create_paypal_order'),
]
