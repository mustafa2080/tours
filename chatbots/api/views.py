from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from chatbots.models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
# from ..services import get_bot_response # Import your bot service

class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing chat sessions (admin/staff)."""
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAdminUser]

class ChatMessageViewSet(viewsets.ModelViewSet):
    """API endpoint for chat messages (primarily for sending)."""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated] # User must be logged in

    def get_queryset(self):
        # Users should only see messages in their own sessions
        return ChatMessage.objects.filter(session__user=self.request.user)

    def perform_create(self, serializer):
        # Expect 'session' and 'message_text' in request data
        session_id = self.request.data.get('session')
        message_text = self.request.data.get('message_text')

        if not session_id or not message_text:
             raise serializers.ValidationError("Session ID and message text are required.")

        try:
            # Ensure the session belongs to the user
            session = ChatSession.objects.get(id=session_id, user=self.request.user)
        except ChatSession.DoesNotExist:
             raise serializers.ValidationError("Invalid session ID or session does not belong to user.")

        # Save the user's message
        user_message = serializer.save(session=session, sender_type='user', message_text=message_text)

        # Get and save the bot's response (replace with actual service call)
        # bot_response_text = get_bot_response(session, message_text)
        bot_response_text = f"API received: '{message_text}'. Integration pending."
        ChatMessage.objects.create(session=session, sender_type='bot', message_text=bot_response_text)

        # We might only return the user message or confirmation,
        # as the bot response might be handled differently by the frontend
        # Or return both user and bot message if needed

    # Consider a custom action instead of standard POST if preferred
    # @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    # def send_message(self, request):
    #     session_id = request.data.get('session_id')
    #     message_text = request.data.get('message')
    #     # ... validation ...
    #     # ... save user message ...
    #     # ... get bot response ...
    #     # ... save bot message ...
    #     return Response({'reply': bot_response_text}, status=status.HTTP_201_CREATED)
