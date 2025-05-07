from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from booking.models import Booking # Uncommented

class Payment(models.Model):
    """
    Represents a payment transaction for a booking.
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', verbose_name=_("Booking")) # Uncommented
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('stripe', _('Stripe')),
            ('paypal', _('PayPal')),
            # Add other methods as needed
        ],
        verbose_name=_("Payment Method")
    )
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name=_("Transaction ID")) # Provided by gateway
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('completed', _('Completed')),
            ('failed', _('Failed')),
            ('refunded', _('Refunded')),
        ],
        default='pending',
        verbose_name=_("Status")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at']

    def __str__(self):
        try:
            return f"Payment for Booking {self.booking.id} - {self.get_status_display()}"
        except Booking.DoesNotExist:
            return f"Payment ID: {self.id} - Status: {self.get_status_display()}"

# Consider adding a PaymentAttempt model if you need to track multiple attempts for a single payment/booking.
