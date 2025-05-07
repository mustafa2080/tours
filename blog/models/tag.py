from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.db import models # Ensure models is imported directly
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Tag(models.Model):
    """Blog tag model - Refactored for django-modeltranslation"""

    # Translatable fields
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)

    # Basic fields (language neutral)
    slug = models.SlugField(max_length=100, unique=True, blank=True) # Allow blank for auto-generation
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name'] # Order by translated name

    def __str__(self):
        return self.name or self.slug
    
    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        # Generate slug from name (current language) if not provided
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def post_count(self):
        return self.posts.filter(is_published=True).count()


# Removed TagTranslation class
