from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from blog.models import Post, Category, Tag, Comment
from .serializers import PostSerializer, CategorySerializer, TagSerializer, CommentSerializer, CommentCreateSerializer

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing blog posts."""
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to read posts
    lookup_field = 'slug' # Use slug for detail view lookup

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing blog categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing blog tags."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

class CommentViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and creating blog comments."""
    queryset = Comment.objects.filter(approved=True) # Only show approved comments
    permission_classes = [IsAuthenticatedOrReadOnly] # Allow read, require auth for create

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        # Automatically set the author if user is authenticated
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            # Requires name/email from anonymous user (handled by serializer)
            serializer.save()

    # Optionally filter comments by post
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     post_id = self.request.query_params.get('post_id')
    #     if post_id:
    #         queryset = queryset.filter(post_id=post_id)
    #     return queryset
