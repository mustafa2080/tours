from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.db import models # Ensure models is imported directly
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Category(models.Model):
    """Blog category model - Refactored for django-modeltranslation"""

    # Translatable fields
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    seo_title = models.CharField(_('SEO Title'), max_length=70, blank=True)
    seo_description = models.CharField(_('SEO Description'), max_length=160, blank=True)

    # Basic fields (language neutral)
    slug = models.SlugField(max_length=100, unique=True, blank=True) # Allow blank for auto-generation
    image = models.ImageField(upload_to='blog/categories/', blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name'] # Order by translated name

    def __str__(self):
        return self.name or self.slug
    
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        # Generate slug from name (current language) if not provided
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def post_count(self):
        # Ensure related posts are accessible via the default related_name 'posts'
        return self.posts.filter(is_published=True).count()


# Removed CategoryTranslation class
