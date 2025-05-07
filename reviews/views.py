from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Review
from tour.models import Tour
from .forms import ReviewForm  # Corrected import


class TourReviewCreateView(LoginRequiredMixin, CreateView):
    """View to create a tour review"""
    model = Review
    form_class = ReviewForm  # Corrected form class
    
    def form_valid(self, form):
        tour = get_object_or_404(Tour, slug=self.kwargs['slug'])
        
        # Check if user has already reviewed this tour
        if Review.objects.filter(tour=tour, user=self.request.user).exists():
            messages.error(self.request, _("You have already reviewed this tour."))
            return redirect('tour:tour_detail', slug=tour.slug)
        
        form.instance.tour = tour
        form.instance.user = self.request.user
        
        response = super().form_valid(form)
        messages.success(self.request, _("Your review has been submitted and is pending approval."))
        return response
    
    def get_success_url(self):
        return reverse_lazy('tour:tour_detail', kwargs={'slug': self.kwargs['slug']})
