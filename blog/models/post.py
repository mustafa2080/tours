from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field # Updated to use CKEditor5

# Import related models from the main models module now
from blog.models.category import Category
from blog.models.tag import Tag

class Post(models.Model):
    """Blog post model - Refactored for django-modeltranslation"""

    # Translatable fields (will be handled by modeltranslation)
    title = models.CharField(_('Title'), max_length=255)
    excerpt = models.TextField(_('Excerpt'), max_length=500)
    content = models.TextField(_('Content'))
    seo_title = models.CharField(_('SEO Title'), max_length=70, blank=True)
    seo_description = models.CharField(_('SEO Description'), max_length=160, blank=True)

    # Basic fields (language neutral)
    slug = models.SlugField(max_length=255, unique=True, blank=True) # Allow blank for auto-generation
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    featured_image = models.ImageField(upload_to='blog/posts/', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

    # Publishing fields
    is_published = models.BooleanField(_('Published'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    # Additional settings
    allow_comments = models.BooleanField(_('Allow comments'), default=True)
    featured = models.BooleanField(_('Featured'), default=False)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        # modeltranslation provides access to current language field directly
        return self.title or self.slug

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Generate slug from title (current language) if not provided
        if not self.slug and self.title:
             # Use the title attribute directly, modeltranslation handles language context
            self.slug = slugify(self.title)
            # Ensure slug uniqueness if needed (e.g., add pk or timestamp)
            # Might need more robust slug generation logic here
        super().save(*args, **kwargs)

    @property
    def comments_count(self):
        return self.comments.filter(approved=True).count()

    def increase_view_count(self):
        """Increase post view count by 1 (legacy method)"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def add_view(self, request):
        """Add a unique view to the post based on user or IP address"""
        # Get the IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Get or create session key if user is not authenticated
        session_key = None
        if not request.user.is_authenticated:
            # Use the session key if available
            if not request.session.session_key:
                request.session.save()
            session_key = request.session.session_key

        # Try to get an existing view
        view, created = PostView.objects.get_or_create(
            post=self,
            ip_address=ip_address,
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            defaults={'viewed_at': timezone.now()}
        )

        # If this is a new view, increment the view count
        if created:
            self.view_count += 1
            self.save(update_fields=['view_count'])

        return view

    @property
    def unique_views_count(self):
        """Get the count of unique views"""
        return self.views.count()


# Removed PostTranslation class


class PostView(models.Model):
    """Tracks unique views for blog posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='post_views')
    session_key = models.CharField(max_length=40, blank=True, null=True)
    viewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('Post View')
        verbose_name_plural = _('Post Views')
        # Ensure a user/IP can only view a post once per day
        unique_together = [
            ('post', 'ip_address', 'user', 'session_key')
        ]

    def __str__(self):
        if self.user:
            return f"{self.post.title} viewed by {self.user.username}"
        return f"{self.post.title} viewed from {self.ip_address or self.session_key}"


class PostImage(models.Model):
    """Additional images for blog posts"""
    # Keep this model as is

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog/posts/')
    caption = models.CharField(_('Caption'), max_length=255, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _('Post Image')
        verbose_name_plural = _('Post Images')
        ordering = ['position']

    def __str__(self):
        return f"Image {self.position} for {self.post}"
