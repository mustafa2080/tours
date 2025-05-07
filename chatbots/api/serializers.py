from rest_framework import serializers
from chatbots.models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'session', 'sender_type', 'message_text', 'timestamp')
        read_only_fields = ('id', 'session', 'sender_type', 'timestamp') # Usually set by backend

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True) # Optionally nest messages

    class Meta:
        model = ChatSession
        fields = ('id', 'user', 'created_at', 'updated_at', 'messages')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'messages')
