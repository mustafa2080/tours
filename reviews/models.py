from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from tour.models import Tour
from users.models import CustomUser


class Review(models.Model):
    """Model representing a review for a tour"""
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='tour_reviews',  # Changed from 'reviews' to avoid conflicts
        verbose_name=_("Tour")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tour_reviews',
        verbose_name=_("User")
    )
    rating = models.IntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_("Comment"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    is_approved = models.BooleanField(_("Is Approved"), default=True)  # Changed default to True

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ['-created_at']
        unique_together = ['tour', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.tour.name} - {self.rating}"