from django import forms
from .models import Booking
from django.utils.translation import gettext_lazy as _

class BookingForm(forms.ModelForm):
    """
    Form for creating or updating a booking.
    """
    class Meta:
        model = Booking
        fields = [
            # 'user', # Typically set automatically based on logged-in user
            # 'tour', # Typically set based on the tour being viewed
            'start_date',
            'end_date',
            'num_adults',
            'num_children',
            'special_requests',
            # 'total_price', # Usually calculated, not set directly by user
            # 'status', # Usually managed internally, not by user
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'num_adults': forms.NumberInput(attrs={'min': '1', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'num_children': forms.NumberInput(attrs={'min': '0', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Any special requirements?'), 'class': 'form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        }
        labels = {
            'start_date': _('Check-in Date'),
            'end_date': _('Check-out Date'),
            'num_adults': _('Adults'),
            'num_children': _('Children'),
            'special_requests': _('Special Requests'),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(_("End date cannot be before start date."))

        # Add more validation logic as needed (e.g., check availability)

        return cleaned_data

# You might add other forms, e.g., a form for filtering bookings
# class BookingFilterForm(forms.Form):
#     status = forms.ChoiceField(choices=[('', _('All Statuses'))] + Booking.status.field.choices, required=False)
#     start_date_after = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
#     # ... other filter fields
