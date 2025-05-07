from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from reviews.models import Review
from tour.models import Tour
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample reviews for testing'

    def add_arguments(self, parser):
        parser.add_argument('--tour_slug', type=str, help='Slug of the tour to add reviews to')
        parser.add_argument('--count', type=int, default=10, help='Number of reviews to create')

    def handle(self, *args, **options):
        tour_slug = options.get('tour_slug')
        count = options.get('count', 10)
        
        # Get all active tours if no specific tour is provided
        if tour_slug:
            tours = Tour.objects.filter(slug=tour_slug)
            if not tours.exists():
                self.stdout.write(self.style.ERROR(f'Tour with slug "{tour_slug}" not found'))
                return
        else:
            tours = Tour.objects.filter(is_active=True)
            if not tours.exists():
                self.stdout.write(self.style.ERROR('No active tours found'))
                return
        
        # Get all users
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found'))
            return
        
        # Sample comments for different ratings
        comments = {
            5: [
                "Excellent tour! The guide was knowledgeable and friendly. Highly recommend!",
                "Amazing experience! The views were breathtaking and the tour was well organized.",
                "One of the best tours I've ever been on. Worth every penny!",
                "Fantastic tour with great attention to detail. Will definitely book again!",
                "Exceeded all expectations. The guide made the experience unforgettable."
            ],
            4: [
                "Great tour overall. A few minor issues but nothing significant.",
                "Very good experience. The guide was informative and helpful.",
                "Enjoyed the tour a lot. Would recommend with a few small suggestions.",
                "Good value for money. The tour was well-paced and interesting.",
                "Nice tour with beautiful sights. Just a bit rushed at times."
            ],
            3: [
                "Average tour. Some parts were interesting, others not so much.",
                "Decent experience but overpriced for what was offered.",
                "The tour was okay. The guide was knowledgeable but not very engaging.",
                "Mixed feelings about this tour. Some highlights but also some disappointments.",
                "Neither great nor terrible. Just an average experience."
            ],
            2: [
                "Below average experience. Too rushed and not enough information provided.",
                "Disappointing tour. Not worth the price at all.",
                "The tour was poorly organized and the guide seemed unprepared.",
                "Expected much more based on the description. Wouldn't recommend.",
                "Several issues with this tour. The transportation was uncomfortable and the stops were too short."
            ],
            1: [
                "Terrible experience. Complete waste of time and money.",
                "Avoid this tour at all costs. Nothing like what was advertised.",
                "The worst tour I've ever been on. Unprofessional guide and poor planning.",
                "Extremely disappointed. Will be asking for a refund.",
                "Absolutely horrible. The tour was delayed, rushed, and the guide was rude."
            ]
        }
        
        reviews_created = 0
        
        for tour in tours:
            self.stdout.write(f"Creating reviews for tour: {tour.name}")
            
            # Determine how many reviews to create for this tour
            tour_review_count = count if tour_slug else random.randint(5, count)
            
            # Create reviews with a distribution of ratings
            # More 4-5 star ratings than 1-3 star ratings for a positive bias
            ratings_distribution = [5] * 4 + [4] * 3 + [3] * 2 + [2] * 1 + [1] * 1
            
            for i in range(tour_review_count):
                # Select a random user
                user = random.choice(users)
                
                # Skip if this user already reviewed this tour
                if Review.objects.filter(tour=tour, user=user).exists():
                    continue
                
                # Select a random rating based on the distribution
                rating = random.choice(ratings_distribution)
                
                # Select a random comment for this rating
                comment = random.choice(comments[rating])
                
                # Create the review
                review = Review.objects.create(
                    tour=tour,
                    user=user,
                    rating=rating,
                    comment=comment,
                    is_approved=True  # Auto-approve for testing
                )
                
                reviews_created += 1
                
                self.stdout.write(f"  Created review #{i+1}: {rating} stars by {user.get_full_name()}")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {reviews_created} sample reviews'))
