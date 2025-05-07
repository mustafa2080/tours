from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Comment(models.Model):
    """Comments for blog posts"""
    
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='blog_comments'
    )
    
    # For non-logged in users
    name = models.CharField(_('Name'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    
    # Content and moderation
    content = models.TextField(_('Content'))
    approved = models.BooleanField(_('Approved'), default=False)
    
    # Parent comment for threading
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        if self.author:
            return f"Comment by {self.author.get_full_name() or self.author.username} on {self.post}"
        return f"Comment by {self.name} on {self.post}"
    
    @property
    def is_parent(self):
        return self.parent is None
    
    @property
    def get_children(self):
        return Comment.objects.filter(parent=self, approved=True)
