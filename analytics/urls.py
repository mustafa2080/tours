from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('revenue/', views.revenue_analytics, name='revenue'),
    path('tours/', views.tour_analytics, name='tours'),
    path('users/', views.user_analytics, name='users'),
    path('reviews/', views.review_analytics, name='reviews'),
    path('export/csv/<str:report_type>/', views.export_csv, name='export_csv'),
]
