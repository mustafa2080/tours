from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.ChatSessionViewSet, basename='chatsession')
router.register(r'messages', views.ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    path('', include(router.urls)),
    # If using custom action:
    # path('send_message/', views.ChatMessageViewSet.as_view({'post': 'send_message'}), name='send_chat_message'),
]
