from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Original payment process
    path('process/<int:booking_id>/', views.process_payment, name='process'),
    path('success/', views.payment_success, name='success'),
    path('failed/', views.payment_failed, name='failed'),

    # PayPal specific (original)
    path('paypal/create/<int:booking_id>/', views.create_paypal_order, name='create_paypal_order'),
    path('paypal/capture/', views.capture_paypal_payment, name='capture_paypal_payment'),
    path('paypal/return/', views.paypal_return, name='paypal_return'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),

    # Webhooks
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/paypal/', views.paypal_webhook, name='paypal_webhook'),

    # Direct payment process (new implementation)
    path('direct/<int:booking_id>/', views.payment_page, name='payment_direct'),
    path('create-paypal-order/<int:booking_id>/', views.create_paypal_order_direct, name='create_paypal_order_direct'),
    path('confirm/', views.payment_confirm, name='payment_confirm'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    # Simple payment process (simplified implementation)
    path('simple/<int:booking_id>/', views.simple_payment_page, name='simple_payment'),
    path('simple/create-order/<int:booking_id>/', views.create_paypal_order_simple, name='create_paypal_order_simple'),
    path('simple/success/', views.payment_success_simple, name='simple_success'),
    path('simple/cancel/', views.payment_cancel_simple, name='simple_cancel'),
]
