from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ChatSession(models.Model):
    """Represents a single chat session, possibly linked to a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keep history even if user is deleted
        null=True,
        blank=True,
        related_name='chat_sessions',
        verbose_name=_("User")
    )
    # Add session ID from external service if needed (e.g., Dialogflow session ID)
    # external_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Chat Session")
        verbose_name_plural = _("Chat Sessions")
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Chat Session for {self.user} ({self.id})"
        return f"Anonymous Chat Session ({self.id})"

class ChatMessage(models.Model):
    """Represents a single message within a chat session."""
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_("Session")
    )
    SENDER_CHOICES = (
        ('user', _('User')),
        ('bot', _('Bot')),
    )
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
        verbose_name=_("Sender Type")
    )
    message_text = models.TextField(_("Message Text"))
    timestamp = models.DateTimeField(auto_now_add=True)
    # Add fields for metadata if needed (e.g., intent detected by bot)
    # intent = models.CharField(max_length=100, blank=True, null=True)
    # confidence = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_sender_type_display()}: {self.message_text[:50]}..."
