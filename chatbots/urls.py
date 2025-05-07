from django.urls import path
from . import views

app_name = 'chatbots'

urlpatterns = [
    # URL for the main chat interface page
    path('interface/', views.chat_interface, name='chat_interface'),

    # URL endpoint for sending/receiving messages (used by frontend JS)
    path('send/', views.send_message, name='send_message'),
]
