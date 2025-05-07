from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Destination, Category, Tour


class TourSearchForm(forms.Form):
    """Form for searching and filtering tours"""
    keyword = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Search tours...")})
    )
    
    destination = forms.ModelChoiceField(
        label=_("Destination"),
        queryset=Destination.objects.filter(is_active=True),
        required=False,
        empty_label=_("All Destinations"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ModelChoiceField(
        label=_("Category"),
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        label=_("Min Price"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _("Min")})
    )
    
    max_price = forms.DecimalField(
        label=_("Max Price"),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _("Max")})
    )
    
    duration = forms.IntegerField(
        label=_("Max Duration (Days)"),
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    SORT_CHOICES = [
        ('created_at', _("Newest")),
        ('price_low', _("Price (Low to High)")),
        ('price_high', _("Price (High to Low)")),
        ('name', _("Name (A-Z)")),
        ('popularity', _("Popularity")),
    ]
    
    sort = forms.ChoiceField(
        label=_("Sort By"),
        choices=SORT_CHOICES,
        required=False,
        initial='created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class TourImportForm(forms.Form):
    """Form for importing tours from CSV/Excel file with multilingual support"""
    file = forms.FileField(
        label=_("Select file"),
        help_text=_("Upload a CSV or Excel file containing tour data with translations."),
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    file_format = forms.ChoiceField(
        label=_("File format"),
        choices=[('xlsx', 'Excel'), ('csv', 'CSV')],
        initial='xlsx',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    create_missing_destinations = forms.BooleanField(
        label=_("Create missing destinations"),
        help_text=_("If checked, destinations that don't exist will be created automatically."),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    create_missing_categories = forms.BooleanField(
        label=_("Create missing categories"),
        help_text=_("If checked, categories that don't exist will be created automatically."),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    update_existing = forms.BooleanField(
        label=_("Update existing tours"),
        help_text=_("If checked, existing tours with the same name will be updated instead of creating duplicates."),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class CategoryImportForm(forms.Form):
    """Form for importing categories from CSV/Excel file"""
    file = forms.FileField(
        label=_("Select file"),
        help_text=_("Upload a CSV or Excel file containing category data."),
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    file_format = forms.ChoiceField(
        label=_("File format"),
        choices=[('xlsx', 'Excel'), ('csv', 'CSV')],
        initial='xlsx',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    update_existing = forms.BooleanField(
        label=_("Update existing categories"),
        help_text=_("If checked, existing categories with the same name will be updated."),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
