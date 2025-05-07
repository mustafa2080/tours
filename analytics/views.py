import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, F, Q, Case, When, Value, IntegerField
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek, ExtractMonth
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from booking.models import Booking
from payments.models import Payment
from tour.models import Tour, Destination, Category
from reviews.models import Review
from users.models import CustomUser
from .models import SiteVisit, TourView


@staff_member_required
def analytics_dashboard(request):
    """Main analytics dashboard view"""
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)

    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()

    # Revenue statistics
    total_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Booking statistics
    total_bookings = Booking.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()

    confirmed_bookings = Booking.objects.filter(
        status='confirmed',
        created_at__date__range=[start_date, end_date]
    ).count()

    # User statistics
    new_users = CustomUser.objects.filter(
        date_joined__date__range=[start_date, end_date]
    ).count()

    # Tour statistics
    popular_tours = Tour.objects.annotate(
        booking_count=Count('bookings', filter=Q(
            bookings__created_at__date__range=[start_date, end_date]
        ))
    ).order_by('-booking_count')[:5]

    # Review statistics
    review_count = Review.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()

    avg_rating = Review.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    # Visit statistics
    visit_count = SiteVisit.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).count()

    # Country statistics
    country_visits = SiteVisit.objects.filter(
        timestamp__date__range=[start_date, end_date],
        country__isnull=False
    ).values('country').annotate(count=Count('id')).order_by('-count')[:10]

    # Daily revenue chart data
    daily_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('amount')
    ).order_by('date')

    revenue_chart_data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in daily_revenue],
        'data': [float(item['total']) for item in daily_revenue]
    }

    # Daily bookings chart data
    daily_bookings = Booking.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    bookings_chart_data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in daily_bookings],
        'data': [item['count'] for item in daily_bookings]
    }

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'new_users': new_users,
        'popular_tours': popular_tours,
        'review_count': review_count,
        'avg_rating': avg_rating,
        'visit_count': visit_count,
        'country_visits': country_visits,
        'revenue_chart_data': json.dumps(revenue_chart_data),
        'bookings_chart_data': json.dumps(bookings_chart_data),
        'report_type': 'dashboard',
    }

    return render(request, 'analytics/dashboard.html', context)


@staff_member_required
def revenue_analytics(request):
    """Revenue analytics view"""
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)

    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()

    # Revenue by payment method
    revenue_by_method = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Revenue by tour
    revenue_by_tour = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).values(
        'booking__tour__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]

    # Revenue by destination
    revenue_by_destination = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).values(
        'booking__tour__destination__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]

    # Monthly revenue trend
    monthly_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date - timedelta(days=365), end_date]
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_chart_data = {
        'labels': [item['month'].strftime('%b %Y') for item in monthly_revenue],
        'data': [float(item['total']) for item in monthly_revenue]
    }

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'revenue_by_method': revenue_by_method,
        'revenue_by_tour': revenue_by_tour,
        'revenue_by_destination': revenue_by_destination,
        'monthly_chart_data': json.dumps(monthly_chart_data),
        'report_type': 'revenue',
    }

    return render(request, 'analytics/revenue.html', context)


@staff_member_required
def tour_analytics(request):
    """Tour analytics view"""
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)

    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()

    # Most booked tours
    most_booked_tours = Tour.objects.annotate(
        booking_count=Count('bookings', filter=Q(
            bookings__created_at__date__range=[start_date, end_date]
        ))
    ).order_by('-booking_count')[:10]

    # Most viewed tours
    most_viewed_tours = Tour.objects.annotate(
        analytics_view_count=Count('analytics_views', filter=Q(
            analytics_views__timestamp__date__range=[start_date, end_date]
        ))
    ).order_by('-analytics_view_count')[:10]

    # Best rated tours
    best_rated_tours = Tour.objects.annotate(
        avg_rating=Avg('tour_reviews__rating', filter=Q(
            tour_reviews__created_at__date__range=[start_date, end_date]
        ))
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]

    # Popular destinations
    popular_destinations = Destination.objects.annotate(
        booking_count=Count('tours__bookings', filter=Q(
            tours__bookings__created_at__date__range=[start_date, end_date]
        ))
    ).order_by('-booking_count')[:10]

    # Popular categories
    popular_categories = Category.objects.annotate(
        booking_count=Count('tours__bookings', filter=Q(
            tours__bookings__created_at__date__range=[start_date, end_date]
        ))
    ).order_by('-booking_count')[:10]

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'most_booked_tours': most_booked_tours,
        'most_viewed_tours': most_viewed_tours,
        'best_rated_tours': best_rated_tours,
        'popular_destinations': popular_destinations,
        'popular_categories': popular_categories,
        'report_type': 'tours',
    }

    return render(request, 'analytics/tours.html', context)


@staff_member_required
def user_analytics(request):
    """User analytics view"""
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)

    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()

    # New users over time
    new_users_by_day = CustomUser.objects.filter(
        date_joined__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    new_users_chart_data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in new_users_by_day],
        'data': [item['count'] for item in new_users_by_day]
    }

    # Top customers by booking count
    top_customers_by_bookings = CustomUser.objects.annotate(
        booking_count=Count('bookings', filter=Q(
            bookings__created_at__date__range=[start_date, end_date]
        ))
    ).filter(booking_count__gt=0).order_by('-booking_count')[:10]

    # Top customers by spending
    top_customers_by_spending = CustomUser.objects.annotate(
        total_spent=Sum('bookings__payment__amount', filter=Q(
            bookings__payment__status='completed',
            bookings__payment__created_at__date__range=[start_date, end_date]
        ))
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:10]

    # Most active reviewers
    most_active_reviewers = CustomUser.objects.annotate(
        review_count=Count('tour_reviews', filter=Q(
            tour_reviews__created_at__date__range=[start_date, end_date]
        ))
    ).filter(review_count__gt=0).order_by('-review_count')[:10]

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'new_users_chart_data': json.dumps(new_users_chart_data),
        'top_customers_by_bookings': top_customers_by_bookings,
        'top_customers_by_spending': top_customers_by_spending,
        'most_active_reviewers': most_active_reviewers,
        'report_type': 'users',
    }

    return render(request, 'analytics/users.html', context)


@staff_member_required
def review_analytics(request):
    """Review analytics view"""
    # Get date range from request or use default (last 30 days)
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=30)

    if end_date_param:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()

    # Rating distribution
    rating_distribution = Review.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('rating').annotate(
        count=Count('id')
    ).order_by('rating')

    rating_chart_data = {
        'labels': [f"{item['rating']} Stars" for item in rating_distribution],
        'data': [item['count'] for item in rating_distribution]
    }

    # Positive reviews (4-5 stars)
    positive_reviews = Review.objects.filter(
        created_at__date__range=[start_date, end_date],
        rating__gte=4
    ).order_by('-created_at')[:10]

    # Negative reviews (1-2 stars)
    negative_reviews = Review.objects.filter(
        created_at__date__range=[start_date, end_date],
        rating__lte=2
    ).order_by('-created_at')[:10]

    # Average rating over time
    avg_rating_by_week = Review.objects.filter(
        created_at__date__range=[start_date - timedelta(days=90), end_date]
    ).annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        avg_rating=Avg('rating')
    ).order_by('week')

    rating_trend_data = {
        'labels': [item['week'].strftime('%b %d, %Y') for item in avg_rating_by_week],
        'data': [float(item['avg_rating']) for item in avg_rating_by_week]
    }

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'rating_chart_data': json.dumps(rating_chart_data),
        'rating_trend_data': json.dumps(rating_trend_data),
        'positive_reviews': positive_reviews,
        'negative_reviews': negative_reviews,
        'report_type': 'reviews',
    }

    return render(request, 'analytics/reviews.html', context)


@staff_member_required
def export_csv(request, report_type):
    """Export analytics data as CSV"""
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().strftime("%Y%m%d")}.csv"'

        # Set CSV writer to handle UTF-8 characters properly
        response.write('\ufeff'.encode('utf8'))  # BOM (Byte Order Mark)
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)

        # Get date range from request or use default (last 30 days)
        end_date = timezone.now().date()
        start_date = request.GET.get('start_date')
        end_date_param = request.GET.get('end_date')

        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start_date = end_date - timedelta(days=30)

            if end_date_param:
                end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format
            start_date = end_date - timedelta(days=30)

        if report_type == 'revenue':
            # Revenue report
            writer.writerow(['Date', 'Total Revenue', 'Number of Bookings', 'Average Booking Value'])

            try:
                daily_revenue = Payment.objects.filter(
                    status='completed',
                    created_at__date__range=[start_date, end_date]
                ).annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(
                    total=Sum('amount'),
                    booking_count=Count('booking', distinct=True)
                ).order_by('date')

                for item in daily_revenue:
                    try:
                        avg_value = item['total'] / item['booking_count'] if item['booking_count'] > 0 else 0
                        writer.writerow([
                            item['date'].strftime('%Y-%m-%d'),
                            float(item['total']),
                            item['booking_count'],
                            float(avg_value)
                        ])
                    except (TypeError, ValueError, ZeroDivisionError) as e:
                        # Handle calculation errors
                        writer.writerow([
                            item['date'].strftime('%Y-%m-%d') if item.get('date') else 'N/A',
                            float(item.get('total', 0) or 0),
                            item.get('booking_count', 0) or 0,
                            0
                        ])
            except Exception as e:
                # Fallback if query fails
                writer.writerow(['Error generating revenue report', str(e)])

        elif report_type == 'tours':
            # Tour performance report
            writer.writerow(['Tour Name', 'Bookings', 'Revenue', 'Views', 'Average Rating'])

            try:
                tours = Tour.objects.annotate(
                    booking_count=Count('bookings', filter=Q(
                        bookings__created_at__date__range=[start_date, end_date]
                    )),
                    revenue=Sum('bookings__payment__amount', filter=Q(
                        bookings__payment__status='completed',
                        bookings__payment__created_at__date__range=[start_date, end_date]
                    )),
                    analytics_view_count=Count('analytics_views', filter=Q(
                        analytics_views__timestamp__date__range=[start_date, end_date]
                    )),
                    avg_rating=Avg('tour_reviews__rating', filter=Q(
                        tour_reviews__created_at__date__range=[start_date, end_date]
                    ))
                ).order_by('-booking_count')

                for tour in tours:
                    try:
                        writer.writerow([
                            str(tour.name),
                            int(tour.booking_count),
                            float(tour.revenue or 0),
                            int(tour.analytics_view_count),
                            float(tour.avg_rating or 0)
                        ])
                    except (AttributeError, TypeError, ValueError) as e:
                        # Handle missing attributes or conversion errors
                        writer.writerow([
                            str(getattr(tour, 'name', 'Unknown')),
                            int(getattr(tour, 'booking_count', 0) or 0),
                            float(getattr(tour, 'revenue', 0) or 0),
                            int(getattr(tour, 'analytics_view_count', 0) or 0),
                            float(getattr(tour, 'avg_rating', 0) or 0)
                        ])
            except Exception as e:
                # Fallback if query fails
                writer.writerow(['Error generating tours report', str(e)])

        elif report_type == 'users':
            # User activity report
            writer.writerow(['Username', 'Email', 'Date Joined', 'Bookings', 'Total Spent', 'Reviews'])

            try:
                users = CustomUser.objects.annotate(
                    booking_count=Count('bookings', filter=Q(
                        bookings__created_at__date__range=[start_date, end_date]
                    )),
                    total_spent=Sum('bookings__payment__amount', filter=Q(
                        bookings__payment__status='completed',
                        bookings__payment__created_at__date__range=[start_date, end_date]
                    )),
                    review_count=Count('tour_reviews', filter=Q(
                        tour_reviews__created_at__date__range=[start_date, end_date]
                    ))
                ).filter(
                    Q(booking_count__gt=0) | Q(review_count__gt=0)
                ).order_by('-booking_count')

                for user in users:
                    try:
                        writer.writerow([
                            str(user.username),
                            str(user.email),
                            user.date_joined.strftime('%Y-%m-%d'),
                            int(user.booking_count),
                            float(user.total_spent or 0),
                            int(user.review_count)
                        ])
                    except (AttributeError, TypeError, ValueError) as e:
                        # Handle missing attributes or conversion errors
                        writer.writerow([
                            str(getattr(user, 'username', 'Unknown')),
                            str(getattr(user, 'email', 'Unknown')),
                            getattr(user, 'date_joined', timezone.now()).strftime('%Y-%m-%d'),
                            int(getattr(user, 'booking_count', 0) or 0),
                            float(getattr(user, 'total_spent', 0) or 0),
                            int(getattr(user, 'review_count', 0) or 0)
                        ])
            except Exception as e:
                # Fallback if query fails
                writer.writerow(['Error generating users report', str(e)])

        elif report_type == 'reviews':
            # Reviews report
            writer.writerow(['Tour', 'User', 'Rating', 'Date', 'Comment'])

            try:
                reviews = Review.objects.filter(
                    created_at__date__range=[start_date, end_date]
                ).select_related('tour', 'user').order_by('-created_at')

                for review in reviews:
                    try:
                        writer.writerow([
                            str(review.tour.name),
                            str(review.user.username),
                            int(review.rating),
                            review.created_at.strftime('%Y-%m-%d'),
                            str(review.comment)
                        ])
                    except (AttributeError, TypeError, ValueError) as e:
                        # Handle missing attributes or conversion errors
                        writer.writerow([
                            str(getattr(review.tour, 'name', 'Unknown Tour')),
                            str(getattr(review.user, 'username', 'Unknown User')),
                            int(getattr(review, 'rating', 0) or 0),
                            getattr(review, 'created_at', timezone.now()).strftime('%Y-%m-%d'),
                            str(getattr(review, 'comment', ''))
                        ])
            except Exception as e:
                # Fallback if query fails
                writer.writerow(['Error generating reviews report', str(e)])

        elif report_type == 'dashboard':
            # Dashboard summary report
            writer.writerow(['Metric', 'Value', 'Period'])

            try:
                # Revenue
                total_revenue = Payment.objects.filter(
                    status='completed',
                    created_at__date__range=[start_date, end_date]
                ).aggregate(total=Sum('amount'))['total'] or 0

                # Bookings
                total_bookings = Booking.objects.filter(
                    created_at__date__range=[start_date, end_date]
                ).count()

                confirmed_bookings = Booking.objects.filter(
                    status='confirmed',
                    created_at__date__range=[start_date, end_date]
                ).count()

                # Users
                new_users = CustomUser.objects.filter(
                    date_joined__date__range=[start_date, end_date]
                ).count()

                # Reviews
                review_count = Review.objects.filter(
                    created_at__date__range=[start_date, end_date]
                ).count()

                avg_rating = Review.objects.filter(
                    created_at__date__range=[start_date, end_date]
                ).aggregate(avg=Avg('rating'))['avg'] or 0

                # Write summary data
                period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                writer.writerow(['Total Revenue', float(total_revenue), period])
                writer.writerow(['Total Bookings', total_bookings, period])
                writer.writerow(['Confirmed Bookings', confirmed_bookings, period])
                writer.writerow(['New Users', new_users, period])
                writer.writerow(['Review Count', review_count, period])
                writer.writerow(['Average Rating', float(avg_rating), period])

            except Exception as e:
                # Fallback if query fails
                writer.writerow(['Error generating dashboard report', str(e)])

        return response

    except Exception as e:
        # If any error occurs, return a CSV with error information
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="error_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Error Type', 'Error Message'])
        writer.writerow([type(e).__name__, str(e)])
        return response
