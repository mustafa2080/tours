from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
# Assuming 'tour' app has a 'Tour' model and 'users' app has 'CustomUser'
from tour.models import Tour # Uncommented
from users.models import CustomUser # Uncommented

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
        ('pending_payment', _('Pending Payment')),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )

    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('credit_card', _('Credit Card')),
        ('bank_transfer', _('Bank Transfer')),
    )

    # Booking Details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    tour = models.ForeignKey('tour.Tour', on_delete=models.PROTECT, related_name='bookings')
    booking_reference = models.CharField(max_length=20, unique=True, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField()
    num_adults = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    num_children = models.PositiveIntegerField(default=0)
    special_requests = models.TextField(blank=True)

    # Price Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency_code = models.CharField(max_length=3, default='USD')

    # Status and Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f"{self.booking_reference or f'BK-{self.id:06d}'} - {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        # Calculate prices if not set
        if not self.subtotal or not self.total_price:
            self.calculate_price()

        # First save to get an ID if this is a new booking
        super().save(*args, **kwargs)

        # Generate booking reference if not set
        if not self.booking_reference:
            self.booking_reference = f"BK-{self.id:06d}"
            # Save again to store the booking reference
            super().save(update_fields=['booking_reference'])

    def calculate_price(self):
        """Calculate booking prices based on tour prices and number of participants"""
        if not self.tour:
            return Decimal('0.00'), Decimal('0.00'), Decimal('0.00')

        # Get prices
        regular_price = self.tour.price
        discounted_price = self.tour.discount_price if self.tour.has_discount else regular_price
        child_price = discounted_price * Decimal('0.5')  # Children at half price

        # Calculate subtotal (based on regular price)
        adult_subtotal = regular_price * self.num_adults
        child_subtotal = regular_price * Decimal('0.5') * (self.num_children or 0)
        subtotal = adult_subtotal + child_subtotal

        # Calculate discount
        discount_amount = Decimal('0.00')
        if self.tour.has_discount:
            discount_per_adult = regular_price - discounted_price
            discount_per_child = discount_per_adult * Decimal('0.5')
            discount_amount = (discount_per_adult * self.num_adults) + \
                            (discount_per_child * (self.num_children or 0))

        # Calculate total price
        total_price = (discounted_price * self.num_adults) + \
                     (child_price * (self.num_children or 0))

        # Update instance attributes
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.total_price = total_price

        return subtotal, discount_amount, total_price

# Add related models if needed, e.g., Passenger details
# class Passenger(models.Model):
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
#     full_name = models.CharField(max_length=255)
#     date_of_birth = models.DateField()
#     # ... other relevant fields
