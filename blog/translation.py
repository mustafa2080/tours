from modeltranslation.translator import register, TranslationOptions
from .models import Post, Category, Tag # Import refactored models

@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'seo_title', 'seo_description')
    # Note: 'content' uses RichTextField, modeltranslation should handle it.

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'seo_title', 'seo_description')

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

# Comment model typically doesn't need translation registration
# PostImage caption could be registered if needed:
# from .models import PostImage
# @register(PostImage)
# class PostImageTranslationOptions(TranslationOptions):
#     fields = ('caption',)
