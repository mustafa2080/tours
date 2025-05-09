from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, FormView
from django.db.models import Avg, Count
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta

from tour.models import Tour, Category as TourCategory, Destination
from blog.models import Post
from reviews.models import Review
from ..models import FAQ, ContactMessage, Newsletter, SiteSetting, Currency
from ..forms import ContactForm, NewsletterForm


class HomeView(TemplateView):
    """View for home page"""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if database tables exist before querying
        try:
            # Check if the Tour table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM tour_tour LIMIT 1")
                    tour_table_exists = True
                except Exception:
                    tour_table_exists = False

            # Only query Tour model if the table exists
            if tour_table_exists:
                context['featured_tours'] = Tour.objects.filter(is_active=True, is_featured=True)[:6]
                context['popular_tours'] = Tour.objects.filter(is_active=True).order_by('-view_count')[:6]

                # Get top reviews for testimonials section
                context['testimonials'] = Review.objects.filter(
                    is_approved=True,
                    rating__gte=4  # Only show reviews with 4 or 5 stars
                ).select_related('user', 'tour').order_by('-created_at')[:3]
            else:
                context['featured_tours'] = []
                context['popular_tours'] = []
                context['testimonials'] = []

            # Check if the Category table exists
            try:
                cursor.execute("SELECT 1 FROM tour_category LIMIT 1")
                category_table_exists = True
            except Exception:
                category_table_exists = False

            if category_table_exists:
                context['tour_categories'] = TourCategory.objects.filter(is_active=True)[:6]
            else:
                context['tour_categories'] = []

            # Check if the Destination table exists
            try:
                cursor.execute("SELECT 1 FROM tour_destination LIMIT 1")
                destination_table_exists = True
            except Exception:
                destination_table_exists = False

            if destination_table_exists:
                context['featured_destinations'] = Destination.objects.filter(is_active=True, is_featured=True)[:6]
            else:
                context['featured_destinations'] = []

            # Check if the Post table exists
            try:
                cursor.execute("SELECT 1 FROM blog_post LIMIT 1")
                post_table_exists = True
            except Exception:
                post_table_exists = False

            if post_table_exists:
                context['latest_posts'] = Post.objects.filter(is_published=True).order_by('-published_at')[:3]
            else:
                context['latest_posts'] = []

        except Exception as e:
            # If any error occurs, set empty lists for all context variables
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in HomeView: {e}")

            context['featured_tours'] = []
            context['popular_tours'] = []
            context['tour_categories'] = []
            context['latest_posts'] = []
            context['featured_destinations'] = []
            context['testimonials'] = []

        return context


class AboutView(TemplateView):
    """View for about us page"""
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Check if the SiteSetting table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM core_sitesetting LIMIT 1")
                    sitesetting_table_exists = True
                except Exception:
                    sitesetting_table_exists = False

            if sitesetting_table_exists:
                try:
                    context['site_settings'] = SiteSetting.objects.first()
                except SiteSetting.DoesNotExist:
                    context['site_settings'] = None
            else:
                context['site_settings'] = None

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in AboutView: {e}")
            context['site_settings'] = None

        return context


class FAQListView(ListView):
    """View for FAQ page"""
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        """Check if the core_faq table exists before querying"""
        try:
            # Check if the FAQ table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM core_faq LIMIT 1")
                    faq_table_exists = True
                except Exception:
                    faq_table_exists = False

            if not faq_table_exists:
                # Return an empty queryset if the table doesn't exist
                return FAQ.objects.none()

            # If table exists, continue with normal query
            return FAQ.objects.filter(is_active=True)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in FAQListView: {e}")
            return FAQ.objects.none()


class ContactView(FormView):
    """View for contact page"""
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        # Create the contact message
        contact_message = ContactMessage(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        contact_message.save()

        messages.success(self.request, _('Your message has been sent successfully. We will contact you soon!'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Check if the SiteSetting table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM core_sitesetting LIMIT 1")
                    sitesetting_table_exists = True
                except Exception:
                    sitesetting_table_exists = False

            if sitesetting_table_exists:
                try:
                    context['site_settings'] = SiteSetting.objects.first()
                except SiteSetting.DoesNotExist:
                    context['site_settings'] = None
            else:
                context['site_settings'] = None

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ContactView.get_context_data: {e}")
            context['site_settings'] = None

        return context


def subscribe_newsletter(request):
    """View to handle newsletter subscription"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if already subscribed
            if not Newsletter.objects.filter(email=email).exists():
                Newsletter.objects.create(email=email)
                messages.success(request, _('You have successfully subscribed to our newsletter!'))
            else:
                messages.info(request, _('You are already subscribed to our newsletter.'))

    # Redirect back to previous page
    return redirect(request.META.get('HTTP_REFERER', 'home'))


class TermsConditionsView(TemplateView):
    """View for terms and conditions page"""
    template_name = 'core/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Check if the SiteSetting table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM core_sitesetting LIMIT 1")
                    sitesetting_table_exists = True
                except Exception:
                    sitesetting_table_exists = False

            if sitesetting_table_exists:
                try:
                    context['site_settings'] = SiteSetting.objects.first()
                except SiteSetting.DoesNotExist:
                    context['site_settings'] = None
            else:
                context['site_settings'] = None

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in TermsConditionsView: {e}")
            context['site_settings'] = None

        return context


class PrivacyPolicyView(TemplateView):
    """View for privacy policy page"""
    template_name = 'core/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Check if the SiteSetting table exists
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM core_sitesetting LIMIT 1")
                    sitesetting_table_exists = True
                except Exception:
                    sitesetting_table_exists = False

            if sitesetting_table_exists:
                try:
                    context['site_settings'] = SiteSetting.objects.first()
                except SiteSetting.DoesNotExist:
                    context['site_settings'] = None
            else:
                context['site_settings'] = None

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in PrivacyPolicyView: {e}")
            context['site_settings'] = None

        return context

@require_POST
def set_currency(request):
    """Sets the selected currency code in the session."""
    currency_code = request.POST.get('currency_code')
    next_url = request.POST.get('next', '/') # Default redirect to home

    try:
        # Check if the Currency table exists
        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT 1 FROM core_currency LIMIT 1")
                currency_table_exists = True
            except Exception:
                currency_table_exists = False

        # Validate if the currency code exists
        if currency_table_exists and currency_code and Currency.objects.filter(code=currency_code).exists():
            request.session['currency_code'] = currency_code
            messages.success(request, _(f"Currency set to {currency_code}."))
        else:
            # If table doesn't exist or currency not found, set USD as default
            request.session['currency_code'] = 'USD'
            if not currency_table_exists:
                messages.info(request, _("Currency system is being set up. Using USD for now."))
            else:
                messages.error(request, _("Invalid currency selected. Using USD."))

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in set_currency: {e}")
        # Set USD as default in case of error
        request.session['currency_code'] = 'USD'
        messages.error(request, _("Error setting currency. Using USD."))

    # Redirect back to the 'next' URL or the default
    return redirect(next_url)

def get_exchange_rates(request):
    """API endpoint to get current exchange rates for JavaScript"""
    try:
        # Check if the Currency table exists
        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT 1 FROM core_currency LIMIT 1")
                currency_table_exists = True
            except Exception:
                currency_table_exists = False

        if not currency_table_exists:
            # Return default USD only if table doesn't exist
            return JsonResponse({
                'base_currency': 'USD',
                'rates': {
                    'USD': {
                        'code': 'USD',
                        'name': 'US Dollar',
                        'symbol': '$',
                        'rate': 1.0
                    }
                },
                'last_updated': timezone.now().isoformat()
            })

        # Get all active currencies
        currencies = Currency.objects.filter(is_active=True)

        # Check if rates need updating (older than 24 hours)
        oldest_update = currencies.order_by('last_updated').first()
        if oldest_update and (timezone.now() - oldest_update.last_updated) > timedelta(hours=24):
            # Rates are stale, but we'll still return them
            # The management command should be run separately
            pass

        # Format the response
        rates = {
            currency.code: {
                'code': currency.code,
                'name': currency.name,
                'symbol': currency.symbol,
                'rate': float(currency.exchange_rate)
            } for currency in currencies
        }

        # Make sure USD is always included
        if 'USD' not in rates:
            rates['USD'] = {
                'code': 'USD',
                'name': 'US Dollar',
                'symbol': '$',
                'rate': 1.0
            }

        return JsonResponse({
            'base_currency': 'USD',
            'rates': rates,
            'last_updated': oldest_update.last_updated.isoformat() if oldest_update else timezone.now().isoformat()
        })

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_exchange_rates: {e}")

        # Return default USD in case of error
        return JsonResponse({
            'base_currency': 'USD',
            'rates': {
                'USD': {
                    'code': 'USD',
                    'name': 'US Dollar',
                    'symbol': '$',
                    'rate': 1.0
                }
            },
            'last_updated': timezone.now().isoformat(),
            'error': str(e)
        }, status=200)  # Still return 200 to not break the client


def csrf_failure(request, reason=""):
    """
    Custom view for CSRF failures that redirects to home page with a message
    instead of showing the default 403 Forbidden page.
    """
    messages.error(request, _("For security reasons, your form submission could not be processed. Please try again."))

    # If the request is AJAX, return a JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': _("CSRF verification failed. Please refresh the page and try again.")
        }, status=403)

    # For logout specifically, redirect to home
    if 'logout' in request.path:
        # Clear session manually
        request.session.flush()
        return redirect('core:home')

    # For other requests, redirect back or to home
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))
