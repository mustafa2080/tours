from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from modeltranslation.admin import TranslationAdmin
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Post, PostImage, Category, Tag, Comment

# Ensure translation registration happens before admin classes are defined
import blog.translation


# Inline for Post Images (Keep as is)
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image', 'caption', 'position')

# Main Model Admins
@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at', 'view_count')
    list_filter = ('is_published', 'categories', 'tags', 'author', 'published_at')
    search_fields = ('title', 'content', 'slug', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags')
    inlines = [PostImageInline]
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    actions = ['publish_posts', 'unpublish_posts']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Apply CKEditor5Widget to all content fields (original and translations)
        for lang_code, lang_name in settings.LANGUAGES:
            content_field = 'content'
            if lang_code != settings.LANGUAGE_CODE:  # For additional languages
                content_field = f'content_{lang_code}'
            if content_field in form.base_fields:
                form.base_fields[content_field].widget = CKEditor5Widget(
                    config_name='extends',
                    attrs={'class': 'django_ckeditor_5'}
                )
        return form

    fieldsets = (
        (_('Post Info'), {'fields': ('slug', 'author', 'featured_image', 'categories', 'tags')}),
        (_('Publishing'), {'fields': ('is_published', 'published_at', 'allow_comments', 'featured')}),
        (_('Content'), {'fields': ('title', 'excerpt', 'content')}), # Add translated fields here
        (_('SEO'), {'fields': ('seo_title', 'seo_description'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('view_count', 'created_at', 'updated_at')

    # Remove helper methods for default lang title/slug

    def publish_posts(self, request, queryset):
        queryset.update(is_published=True)
        # Optionally set published_at if not already set
    publish_posts.short_description = _("Publish selected posts")

    def unpublish_posts(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_posts.short_description = _("Unpublish selected posts")


@admin.register(Category)
class CategoryAdmin(TranslationAdmin): # Inherit from TranslationAdmin
    list_display = ('name', 'slug', 'parent', 'order', 'post_count') # Use direct name field
    search_fields = ('name', 'slug') # Search direct name field
    prepopulated_fields = {'slug': ('name',)} # Prepopulate from name
    # inlines = [CategoryTranslationInline] # Remove inline
    ordering = ('order', 'name') # Order by direct name field

    # Remove helper methods


@admin.register(Tag)
class TagAdmin(TranslationAdmin): # Inherit from TranslationAdmin
    list_display = ('name', 'slug', 'post_count') # Use direct name field
    search_fields = ('name', 'slug') # Search direct name field
    prepopulated_fields = {'slug': ('name',)} # Prepopulate from name
    # inlines = [TagTranslationInline] # Remove inline
    ordering = ('name',) # Order by direct name field

    # Remove helper methods


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'get_author_name', 'content_preview', 'created_at', 'approved')
    list_filter = ('approved', 'created_at')
    search_fields = ('post__title', 'author__email', 'name', 'email', 'content') # Search direct post title
    readonly_fields = ('post', 'author', 'name', 'email', 'website', 'content', 'parent', 'created_at', 'updated_at')
    actions = ['approve_comments', 'unapprove_comments']

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.email
        return obj.name or _('(Anonymous)')
    get_author_name.short_description = _('Author')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Preview')

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = _("Approve selected comments")

    def unapprove_comments(self, request, queryset):
        queryset.update(approved=False)
    unapprove_comments.short_description = _("Unapprove selected comments")
