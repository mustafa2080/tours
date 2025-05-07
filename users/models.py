from django.conf import settings # Import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
# Remove this line to break the circular import:
# from tour.models import Tour # Import Tour model

class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        # Set username to email prefix
        user.username = email.split('@')[0]
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(  # Change from None to optional field
        _('username'),
        max_length=150,
        blank=True,
        null=True,
        unique=True  # Keep unique for compatibility
    )
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(_("Profile Picture"), upload_to='users/profile/', blank=True)
    phone_number = models.CharField(_("Phone Number"), max_length=20, blank=True)
    bio = models.TextField(_("Biography"), blank=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_initials(self):
        """Return the user's initials."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.last_name:
            return self.last_name[0].upper()
        else:
            return self.email[0].upper()


class WishlistItem(models.Model):
    """Model representing a tour added to a user's wishlist."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name=_("User"))
    # Use string reference to Tour model instead of direct import
    tour = models.ForeignKey('tour.Tour', on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name=_("Tour"))
    added_at = models.DateTimeField(_("Added At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Wishlist Item")
        verbose_name_plural = _("Wishlist Items")
        unique_together = ('user', 'tour') # Prevent duplicate entries
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.tour.name}"
