from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re

class CustomAccountAdapter(DefaultAccountAdapter):
    def validate_email(self, email):
        """Basic email validation"""
        if not email:
            raise ValidationError(_("Email address is required."))

        # Normalize the email (lowercase)
        email = email.lower().strip()

        # Basic format validation
        if '@' not in email:
            raise ValidationError(_("Email must contain an '@' symbol."))

        # Split email into username and domain parts
        try:
            username, domain = email.split('@')
        except ValueError:
            raise ValidationError(_("Email must contain exactly one '@' symbol."))

        # Username validation
        if not username:
            raise ValidationError(_("Username part of email cannot be empty."))

        # Domain validation
        if not domain:
            raise ValidationError(_("Domain part of email cannot be empty."))

        if '.' not in domain:
            raise ValidationError(_("Domain must include a dot for the top-level domain."))

        # Validate email format using parent class validation for any additional checks
        try:
            email = super().validate_email(email)
        except ValidationError as e:
            raise ValidationError(_("Invalid email format: {}").format(str(e)))

        return email

    def validate_password(self, password, user=None):
        """Validate password with clear error messages"""
        min_length = 8

        if len(password) < min_length:
            raise ValidationError(
                _("Password must be at least {0} characters long.").format(min_length)
            )

        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter.")
            )

        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter.")
            )

        # Check for at least one digit
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("Password must contain at least one number.")
            )

        # Check for at least one special character
        special_chars = ['@', '#', '%', '!', '$', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']
        if not any(char in special_chars for char in password):
            raise ValidationError(
                _("Password must contain at least one special character (@, #, %, etc).")
            )

        return password

    def validate_username(self, username):
        """Validate username: alphanumeric + underscore, min 3 characters"""
        if not username:
            raise ValidationError(_("Username cannot be empty."))
        if len(username) < 3:
            raise ValidationError(_("Username must be at least 3 characters long."))
        # Allow letters, numbers, underscores, dots, and hyphens
        if not re.match(r'^[a-zA-Z0-9_.\-]+$', username):
            raise ValidationError(_("Username can only contain letters, numbers, underscores, dots, and hyphens."))

    def populate_username(self, request, user):
        """Generate a username from email"""
        email = user.email
        if email:
            username = email.split('@')[0]
            # Ensure username is valid
            self.validate_username(username)
            user.username = username

    def save_user(self, request, user, form):
        """Save user and ensure username is set"""
        user = super().save_user(request, user, form)
        if not user.username:
            username = user.email.split('@')[0]
            # Ensure username is valid
            self.validate_username(username)
            user.username = username
            user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_username(self, request, sociallogin):
        """Generate a username from email for social accounts"""
        email = sociallogin.account.extra_data.get('email')
        if email:
            username = email.split('@')[0]
            sociallogin.user.username = username

    def save_user(self, request, sociallogin, form=None):
        """Save social user and ensure username is set"""
        user = super().save_user(request, sociallogin, form)
        if not user.username:
            user.username = user.email.split('@')[0]
            user.save()
        return user
