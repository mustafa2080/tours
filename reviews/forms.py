from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Review  # Corrected model name


class ReviewForm(forms.ModelForm):  # Renamed form for clarity
    """Form for users to add tour reviews"""

    class Meta:
        model = Review
        # Updated fields to match the Review model
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, str(i)) for i in range(1, 6)],
                # Added class for CSS styling
                attrs={'class': 'star-rating'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
