from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
import json
from .models import ChatSession, ChatMessage

def get_bot_response(session, user_message):
    """Generates a bot response based on simple keyword matching."""
    lower_message = user_message.lower()
    response_text = _("Sorry, I didn't understand that. Can you please rephrase?") # Default response

    if 'hello' in lower_message or 'hi' in lower_message or 'hey' in lower_message:
        response_text = _("Hello! How can I help you with our tours today?")
    elif 'price' in lower_message or 'cost' in lower_message:
        response_text = _("You can find the price for each tour on its detail page. Would you like me to show you our tours?")
        # Potential enhancement: Link to the tour list page
    elif 'book' in lower_message or 'booking' in lower_message or 'reserve' in lower_message:
        response_text = _("To book a tour, please visit the tour's detail page and select an available date. Do you need help finding a specific tour?")
    elif 'contact' in lower_message or 'phone' in lower_message or 'email' in lower_message:
        response_text = _("You can find our contact information on the 'Contact Us' page.")
        # Potential enhancement: Link to the contact page
    elif 'thank' in lower_message:
        response_text = _("You're welcome! Is there anything else I can help you with?")

    return response_text

# Allow both authenticated and anonymous users
def chat_interface(request):
    """Renders the main chat interface page or returns session data as JSON."""
    # Get or create a chat session for the user
    if request.user.is_authenticated:
        session, created = ChatSession.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, create a new session each time or use one from cookie
        session_id = request.COOKIES.get('chat_session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=None)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(user=None)
        else:
            session = ChatSession.objects.create(user=None)
    
    # Load recent messages for this session to display initially
    recent_messages = session.messages.order_by('timestamp')[:20] # Load last 20 messages
    
    # Check if JSON is requested (for embedded widget)
    if request.headers.get('Accept') == 'application/json':
        # Prepare data for JSON response
        messages_data = []
        for msg in recent_messages:
            messages_data.append({
                'sender_type': msg.sender_type,
                'message_text': msg.message_text,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'session_id': str(session.id),
            'recent_messages': messages_data
        })
    
    # Standard template render
    context = {
        'session_id': session.id,
        'recent_messages': recent_messages, # Now ordered by timestamp ascending
    }
    response = render(request, 'chatbots/chat_interface.html', context)
    
    # Set cookie for anonymous users
    if not request.user.is_authenticated:
        response.set_cookie('chat_session_id', str(session.id), max_age=60*60*24*30)  # 30 days
    
    return response

# Removed @csrf_exempt as the frontend seems to send the token
# Removed login_required to allow anonymous users
def send_message(request):
    """Handles incoming user messages and returns bot response via JSON."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            session_id = data.get('session_id') # Get session ID from frontend

            if not user_message or not session_id:
                return JsonResponse({'error': 'Missing message or session_id'}, status=400)

            # Retrieve the session
            try:
                if request.user.is_authenticated:
                    # For authenticated users, ensure they own the session
                    session = ChatSession.objects.get(id=session_id, user=request.user)
                else:
                    # For anonymous users, just verify the session exists
                    # In production, add additional security checks
                    session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                return JsonResponse({'error': 'Chat session not found'}, status=404)

            # Save user message
            ChatMessage.objects.create(
                session=session,
                sender_type='user',
                message_text=user_message
            )

            # Get bot response from the service
            bot_message_text = get_bot_response(session, user_message) # Pass session if needed by service

            # Save bot message
            ChatMessage.objects.create(
                session=session,
                sender_type='bot',
                message_text=bot_message_text
            )

            return JsonResponse({'reply': bot_message_text})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Log the exception e
            return JsonResponse({'error': 'An internal error occurred'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
