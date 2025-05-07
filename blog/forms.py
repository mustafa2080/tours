from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comment

class CommentForm(forms.ModelForm):
    """Form for users to submit comments"""

    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'content', 'parent'] # Include parent for replies
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Your Name (required)'), 'class': 'form-input mt-1 block w-full'}),
            'email': forms.EmailInput(attrs={'placeholder': _('Your Email (required, not published)'), 'class': 'form-input mt-1 block w-full'}),
            'website': forms.URLInput(attrs={'placeholder': _('Your Website (optional)'), 'class': 'form-input mt-1 block w-full'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Your Comment...'), 'class': 'form-textarea mt-1 block w-full'}),
            'parent': forms.HiddenInput(), # Hidden field to store parent comment ID for replies
        }
        labels = {
            'name': _('Name'),
            'email': _('Email'),
            'website': _('Website'),
            'content': _('Comment'),
        }

    def __init__(self, *args, **kwargs):
        # If user is authenticated, prefill name/email and hide those fields
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['email'].widget = forms.HiddenInput()
            self.fields['website'].widget = forms.HiddenInput() # Can optionally allow logged-in users to add website

            self.fields['name'].required = False
            self.fields['email'].required = False
            self.fields['website'].required = False

            # Optionally prefill initial data if needed, though model handles author link
            # self.initial['name'] = user.get_full_name() or user.username
            # self.initial['email'] = user.email
        else:
            # Make name and email required for anonymous users
            self.fields['name'].required = True
            self.fields['email'].required = True
            self.fields['website'].required = False # Website is optional
