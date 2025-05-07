from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie # Import vary_on_cookie
from .views import post as post_views # Import views from the post submodule

app_name = 'blog'

# Cache duration (15 minutes)
CACHE_TTL = 60 * 15

urlpatterns = [
    # Post list and detail
    # Apply caching and vary_on_cookie decorators
    path('', vary_on_cookie(cache_page(CACHE_TTL)(post_views.PostListView.as_view())), name='post_list'),
    path('<slug:slug>/', post_views.PostDetailView.as_view(), name='post_detail'),

    # Category and Tag archives (using the same list view but passing kwargs)
    # Note: Caching these might be desirable too, but the request was specific to /en/blog/
    path('category/<slug:category_slug>/', post_views.PostListView.as_view(), name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', post_views.PostListView.as_view(), name='post_list_by_tag'),
    
    # Search feature
    path('search/', post_views.PostSearchView.as_view(), name='post_search'),

    # Add URLs for comment submission if handled separately (currently handled in PostDetailView)
    # path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
]
