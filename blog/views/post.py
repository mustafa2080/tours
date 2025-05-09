from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
# No longer need django.utils.translation here
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import models # Import models for Prefetch

from blog.models import Post, Category, Tag, Comment
from blog.forms import CommentForm

POSTS_PER_PAGE = 10

class PostListView(ListView):
    """Displays a list of published blog posts"""
    model = Post
    template_name = 'blog/post_list_redesign.html' # Using our new redesigned template
    context_object_name = 'posts'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        """Check if the blog_post table exists before querying"""
        try:
            # Check if the Post table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_post LIMIT 1")
                    post_table_exists = True
                except Exception:
                    post_table_exists = False

            if not post_table_exists:
                # Return an empty queryset if the table doesn't exist
                return Post.objects.none()

            # If table exists, continue with normal query
            # Filter only published posts
            # modeltranslation handles fetching the correct language fields automatically
            queryset = Post.objects.filter(is_published=True).select_related('author')

            # Add filtering by category or tag if needed
            category_slug = self.kwargs.get('category_slug')
            tag_slug = self.kwargs.get('tag_slug')
            if category_slug:
                try:
                    # Check if the Category table exists
                    cursor.execute("SELECT 1 FROM blog_category LIMIT 1")
                    category_table_exists = True
                except Exception:
                    category_table_exists = False

                if category_table_exists:
                    category = get_object_or_404(Category, slug=category_slug)
                    queryset = queryset.filter(categories=category)

            if tag_slug:
                try:
                    # Check if the Tag table exists
                    cursor.execute("SELECT 1 FROM blog_tag LIMIT 1")
                    tag_table_exists = True
                except Exception:
                    tag_table_exists = False

                if tag_table_exists:
                    tag = get_object_or_404(Tag, slug=tag_slug)
                    queryset = queryset.filter(tags=tag)

            # Add search functionality
            search_query = self.request.GET.get('search', '')
            if search_query:
                queryset = queryset.filter(
                    models.Q(title__icontains=search_query) |
                    models.Q(content__icontains=search_query) |
                    models.Q(excerpt__icontains=search_query)
                )

            return queryset

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostListView: {e}")
            return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Check if the Category and Tag tables exist
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_category LIMIT 1")
                    category_table_exists = True
                except Exception:
                    category_table_exists = False

                try:
                    cursor.execute("SELECT 1 FROM blog_tag LIMIT 1")
                    tag_table_exists = True
                except Exception:
                    tag_table_exists = False

            # Only query if tables exist
            if category_table_exists:
                # Use Category.objects.all() directly, modeltranslation handles name
                context['categories'] = Category.objects.all()
            else:
                context['categories'] = []

            if tag_table_exists:
                context['tags'] = Tag.objects.all()
            else:
                context['tags'] = []

            # Add category/tag object to context if filtering
            category_slug = self.kwargs.get('category_slug')
            tag_slug = self.kwargs.get('tag_slug')

            if category_slug and category_table_exists:
                context['category'] = get_object_or_404(Category, slug=category_slug)

            if tag_slug and tag_table_exists:
                context['tag'] = get_object_or_404(Tag, slug=tag_slug)

            # Add search query to context
            context['search_query'] = self.request.GET.get('search', '')

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostListView.get_context_data: {e}")

            # Set default values
            context['categories'] = []
            context['tags'] = []
            context['search_query'] = self.request.GET.get('search', '')

        return context


class PostDetailView(FormMixin, DetailView):
    """Displays a single blog post with comments"""
    model = Post
    template_name = 'blog/post_detail.html' # Needs creation
    context_object_name = 'post'
    form_class = CommentForm # For comment submission

    def dispatch(self, request, *args, **kwargs):
        """Check if the blog_post table exists before processing the request"""
        try:
            # Check if the Post table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_post LIMIT 1")
                    post_table_exists = True
                except Exception:
                    post_table_exists = False

            if not post_table_exists:
                # Redirect to home page if the table doesn't exist
                from django.shortcuts import redirect
                return redirect('core:home')

            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostDetailView: {e}")
            from django.shortcuts import redirect
            return redirect('core:home')

    def get_queryset(self):
        try:
            # Check if the Comment table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_comment LIMIT 1")
                    comment_table_exists = True
                except Exception:
                    comment_table_exists = False

            # Ensure we only show published posts, prefetch related data
            # modeltranslation handles fetching the correct language fields
            queryset = Post.objects.filter(is_published=True).select_related('author')

            if comment_table_exists:
                queryset = queryset.prefetch_related(
                    # No need to prefetch translations separately
                    models.Prefetch(
                        'comments',
                        queryset=Comment.objects.filter(approved=True, parent__isnull=True).select_related('author').prefetch_related('replies'), # Get top-level approved comments
                        to_attr='approved_comments'
                    )
                )

            return queryset

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostDetailView.get_queryset: {e}")
            return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        try:
            # Add view using the new unique view tracking system
            if hasattr(post, 'add_view'):
                post.add_view(self.request)
            else:
                # Fallback to legacy method if add_view doesn't exist
                if hasattr(post, 'increase_view_count'):
                    post.increase_view_count()

            # Add comment form to context
            context['comment_form'] = self.get_form()

            # Check if the Category table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_category LIMIT 1")
                    category_table_exists = True
                except Exception:
                    category_table_exists = False

            # Add related posts (example: same category)
            if category_table_exists and hasattr(post, 'categories'):
                context['related_posts'] = Post.objects.filter(
                    is_published=True, categories__in=post.categories.all()
                ).exclude(id=post.id).distinct()[:3]
            else:
                context['related_posts'] = []

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostDetailView.get_context_data: {e}")

            # Set default values
            context['comment_form'] = self.get_form()
            context['related_posts'] = []

        return context

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.object.slug}) + '#comments'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # Need the post object
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        if self.request.user.is_authenticated:
            comment.author = self.request.user
            comment.name = self.request.user.get_full_name() or self.request.user.email # Pre-fill name for display consistency
            comment.email = self.request.user.email
        # Set approved status based on settings (e.g., auto-approve logged-in users?)
        comment.approved = self.request.user.is_authenticated # Example: auto-approve logged-in users
        comment.save()
        messages.success(self.request, _('Your comment has been submitted.' if comment.approved else 'Your comment is awaiting moderation.'))
        return super().form_valid(form)

    def get_form_kwargs(self):
        # Pass the current user to the form's __init__
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

# Add views for CategoryListView, TagListView if needed (similar to PostListView but filtering differently)

class PostSearchView(ListView):
    """Search for blog posts"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        """Check if the blog_post table exists before querying"""
        try:
            # Check if the Post table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_post LIMIT 1")
                    post_table_exists = True
                except Exception:
                    post_table_exists = False

            if not post_table_exists:
                # Return an empty queryset if the table doesn't exist
                return Post.objects.none()

            # Get the search query from GET parameters
            query = self.request.GET.get('search', '')
            if query:
                # Search in title, content, and excerpt
                queryset = Post.objects.filter(
                    models.Q(title__icontains=query) |
                    models.Q(content__icontains=query) |
                    models.Q(excerpt__icontains=query),
                    is_published=True
                ).select_related('author')
            else:
                # If no query, return empty queryset
                queryset = Post.objects.none()
            return queryset

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostSearchView: {e}")
            return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Check if the Category and Tag tables exist
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM blog_category LIMIT 1")
                    category_table_exists = True
                except Exception:
                    category_table_exists = False

                try:
                    cursor.execute("SELECT 1 FROM blog_tag LIMIT 1")
                    tag_table_exists = True
                except Exception:
                    tag_table_exists = False

            # Only query if tables exist
            if category_table_exists:
                context['categories'] = Category.objects.all()
            else:
                context['categories'] = []

            if tag_table_exists:
                context['tags'] = Tag.objects.all()
            else:
                context['tags'] = []

            # Add search query to context
            context['search_query'] = self.request.GET.get('search', '')

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PostSearchView.get_context_data: {e}")

            # Set default values
            context['categories'] = []
            context['tags'] = []
            context['search_query'] = self.request.GET.get('search', '')

        return context
