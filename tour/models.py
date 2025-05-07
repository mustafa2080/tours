from django.db import models
from django.urls import reverse  # Import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from users.models import CustomUser
from core.models import Currency
from django.core.validators import MinValueValidator, MaxValueValidator


class Destination(models.Model):
    """Model representing a tourism destination"""
    name = models.CharField(_("Destination Name"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=250, unique=True, blank=True)
    description = models.TextField(_("Description"))
    cover_image = models.ImageField(_("Cover Image"), upload_to='destinations/')
    country = models.CharField(_("Country"), max_length=100)
    city = models.CharField(_("City"), max_length=100)
    is_featured = models.BooleanField(_("Is Featured"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Destination")
        verbose_name_plural = _("Destinations")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DestinationImage(models.Model):
    """Additional images for a destination"""
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE,
                                    related_name='images', verbose_name=_("Destination"))
    image = models.ImageField(_("Image"), upload_to='destinations/gallery/')
    caption = models.CharField(_("Caption"), max_length=200, blank=True)
    is_main = models.BooleanField(_("Is Main Image"), default=False)

    class Meta:
        verbose_name = _("Destination Image")
        verbose_name_plural = _("Destination Images")

    def __str__(self):
        return f"{self.destination.name} - {self.caption or 'Image'}"


class Category(models.Model):
    """Categories for tours/activities"""
    name = models.CharField(_("Category Name"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=150, unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    icon = models.CharField(_("Icon Class"), max_length=100, blank=True,
                            help_text=_("Font Awesome or other icon class"))
    image = models.ImageField(_("Image"), upload_to='categories/', blank=True, null=True) # Added image field
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Activity(models.Model):
    """Model for different types of activities available in tours"""
    name = models.CharField(_("Activity Name"), max_length=100)
    icon = models.CharField(_("Icon Class"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ['name']

    def __str__(self):
        return self.name


class Tour(models.Model):
    """Model representing a tour package"""

    name = models.CharField(_("Tour Name"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=250, unique=True, blank=True)
    description = models.TextField(_("Description"))
    short_description = models.CharField(_("Short Description"), max_length=300)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE,
                                   related_name='tours', verbose_name=_("Destination"))
    categories = models.ManyToManyField(Category, related_name='tours', verbose_name=_("Categories"))
    activities = models.ManyToManyField(Activity, related_name='tours', verbose_name=_("Activities"))
    duration_days = models.PositiveIntegerField(_("Duration (Days)"))
    duration_nights = models.PositiveIntegerField(_("Duration (Nights)"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(_("Discount Price"), max_digits=10, decimal_places=2,
                                        blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True,
                                related_name='tours', verbose_name=_("Currency"))
    max_people = models.PositiveIntegerField(_("Maximum People"))
    min_age = models.PositiveIntegerField(_("Minimum Age"), default=0)
    included_services = models.TextField(_("Included Services"), blank=True)
    excluded_services = models.TextField(_("Excluded Services"), blank=True)
    meeting_point = models.CharField(_("Meeting Point"), max_length=255, blank=True)
    cover_image = models.ImageField(_("Cover Image"), upload_to='tours/')
    highlight_video = models.FileField(_("Highlight Video"), upload_to='tours/videos/',
                                      blank=True, null=True)
    map_location = models.URLField(_("Map Location"), blank=True)
    latitude = models.DecimalField(_("Latitude"), max_digits=9, decimal_places=6,
                                  blank=True, null=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=9, decimal_places=6,
                                   blank=True, null=True)
    is_featured = models.BooleanField(_("Is Featured"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    view_count = models.PositiveIntegerField(_("View Count"), default=0)

    class Meta:
        verbose_name = _("Tour")
        verbose_name_plural = _("Tours")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        """Check if tour has a discount"""
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.has_discount:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def discount_amount(self):
        """Calculate discount amount per person"""
        if self.has_discount:
            return self.price - self.discount_price
        return 0

    def get_review_count(self):
        return self.tour_reviews.filter(is_approved=True).count()

    def get_average_rating(self):
        reviews = self.tour_reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)

    def increment_view_count(self):
        """Increment the view count"""
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this tour."""
        return reverse('tour:tour_detail', kwargs={'slug': self.slug})


class TourImage(models.Model):
    """Additional images for a tour"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE,
                           related_name='images', verbose_name=_("Tour"))
    image = models.ImageField(_("Image"), upload_to='tours/gallery/')
    caption = models.CharField(_("Caption"), max_length=200, blank=True)
    is_main = models.BooleanField(_("Is Main Image"), default=False)

    class Meta:
        verbose_name = _("Tour Image")
        verbose_name_plural = _("Tour Images")

    def __str__(self):
        return f"{self.tour.name} - {self.caption or 'Image'}"


class TourDate(models.Model):
    """Available dates for tours"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE,
                           related_name='dates', verbose_name=_("Tour"))
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    available_seats = models.PositiveIntegerField(_("Available Seats"))
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Tour Date")
        verbose_name_plural = _("Tour Dates")
        ordering = ['start_date']

    def __str__(self):
        return f"{self.tour.name} - {self.start_date}"


class TourGuide(models.Model):
    """Model for tour guides"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                               related_name='guide_profile', verbose_name=_("User"))
    bio = models.TextField(_("Biography"))
    profile_image = models.ImageField(_("Profile Image"), upload_to='guides/')
    years_experience = models.PositiveIntegerField(_("Years of Experience"))
    languages = models.CharField(_("Languages Spoken"), max_length=200)
    speciality = models.ManyToManyField(Category, related_name='guides', verbose_name=_("Specialities"))
    rating = models.DecimalField(_("Average Rating"), max_digits=3, decimal_places=2, default=5.0)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Tour Guide")
        verbose_name_plural = _("Tour Guides")

    def __str__(self):
        return f"{self.user.get_full_name()}"


class TourItinerary(models.Model):
    """Daily itinerary for tours"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE,
                           related_name='itinerary', verbose_name=_("Tour"))
    day = models.PositiveIntegerField(_("Day"))
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"))
    meals = models.CharField(_("Meals"), max_length=100, blank=True,
                           help_text=_("E.g., Breakfast, Lunch, Dinner"))
    accommodation = models.CharField(_("Accommodation"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("Tour Itinerary")
        verbose_name_plural = _("Tour Itineraries")
        ordering = ['tour', 'day']

    def __str__(self):
        return f"{self.tour.name} - Day {self.day}: {self.title}"


class TourFAQ(models.Model):
    """Frequently asked questions for specific tours"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE,
                           related_name='faqs', verbose_name=_("Tour"))
    question = models.CharField(_("Question"), max_length=255)
    answer = models.TextField(_("Answer"))
    order = models.PositiveIntegerField(_("Display Order"), default=0)

    class Meta:
        verbose_name = _("Tour FAQ")
        verbose_name_plural = _("Tour FAQs")
        ordering = ['tour', 'order']

    def __str__(self):
        return f"{self.tour.name} - {self.question}"


class Promotion(models.Model):
    """Model for tour promotions and offers"""
    title = models.CharField(_("Title"), max_length=200)
    code = models.CharField(_("Promo Code"), max_length=20, unique=True)
    tours = models.ManyToManyField(Tour, related_name='promotions', verbose_name=_("Tours"))
    discount_percentage = models.PositiveIntegerField(_("Discount Percentage"))
    description = models.TextField(_("Description"), blank=True)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    usage_limit = models.PositiveIntegerField(_("Usage Limit"), blank=True, null=True)
    current_usage = models.PositiveIntegerField(_("Current Usage"), default=0)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotions")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} - {self.code}"

    @property
    def is_valid(self):
        """Check if promotion is currently valid"""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.is_active and
                self.start_date <= today <= self.end_date and
                (self.usage_limit is None or self.current_usage < self.usage_limit))

# In your Booking model, add this method if it doesn't exist already

def has_review(self):
    """Check if the user has already reviewed this tour"""
    from .models import Review  # Import here to avoid circular imports
    return Review.objects.filter(tour=self.tour, user=self.user).exists()
