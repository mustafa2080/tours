from rest_framework import serializers
from blog.models import Post, Category, Tag, Comment
from users.api.serializers import UserSerializer # For author info

# Basic serializers for read operations
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description') # Add other fields if needed

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class CommentSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True) # Example nested serializer

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'author_details', 'name', 'content', 'parent', 'created_at')
        read_only_fields = ('created_at',)

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    # comments = CommentSerializer(many=True, read_only=True) # Can be heavy, consider separate endpoint

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'author', 'featured_image', 
            'categories', 'tags', 'excerpt', 'content', 
            'is_published', 'published_at', 'view_count', 'comments_count'
        )
        read_only_fields = ('published_at', 'view_count', 'comments_count')

# Add serializers for creating/updating comments if needed
class CommentCreateSerializer(serializers.ModelSerializer):
     class Meta:
        model = Comment
        fields = ('post', 'content', 'parent', 'name', 'email', 'website') # Name/email/website for anonymous

     def validate_post(self, value):
        # Ensure post allows comments
        if not value.allow_comments:
            raise serializers.ValidationError("Comments are disabled for this post.")
        return value
