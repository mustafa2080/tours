from django.core.management.base import BaseCommand
from django.utils import timezone
from tour.models import Tour, Destination, Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Set up initial tour data'

    def handle(self, *args, **options):
        # Create sample categories
        categories = [
            {
                'name': 'Adventure',
                'description': 'Adventure tours for thrill seekers',
            },
            {
                'name': 'Cultural',
                'description': 'Cultural tours to explore local traditions',
            },
            {
                'name': 'Beach',
                'description': 'Relaxing beach tours',
            },
        ]
        
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'slug': slugify(category_data['name']),
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create sample destinations
        destinations = [
            {
                'name': 'Cairo',
                'country': 'Egypt',
                'city': 'Cairo',
                'description': 'The capital of Egypt',
            },
            {
                'name': 'Luxor',
                'country': 'Egypt',
                'city': 'Luxor',
                'description': 'Ancient Egyptian city',
            },
        ]
        
        for destination_data in destinations:
            destination, created = Destination.objects.get_or_create(
                name=destination_data['name'],
                defaults={
                    'country': destination_data['country'],
                    'city': destination_data['city'],
                    'description': destination_data['description'],
                    'slug': slugify(destination_data['name']),
                    'is_active': True,
                    'is_featured': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created destination: {destination.name}'))
            else:
                self.stdout.write(f'Destination already exists: {destination.name}')
        
        # Create sample tours
        if Destination.objects.exists() and Category.objects.exists():
            # Get the first destination and category
            destination = Destination.objects.first()
            category = Category.objects.first()
            
            tour_data = {
                'name': 'Sample Tour',
                'slug': 'sample-tour',
                'description': 'This is a sample tour',
                'short_description': 'Sample tour description',
                'price': 100.00,
                'duration_days': 3,
                'max_participants': 20,
                'is_featured': True,
                'is_active': True,
            }
            
            tour, created = Tour.objects.get_or_create(
                name=tour_data['name'],
                defaults={
                    'slug': tour_data['slug'],
                    'description': tour_data['description'],
                    'short_description': tour_data['short_description'],
                    'price': tour_data['price'],
                    'duration_days': tour_data['duration_days'],
                    'max_participants': tour_data['max_participants'],
                    'is_featured': tour_data['is_featured'],
                    'is_active': tour_data['is_active'],
                    'destination': destination,
                }
            )
            
            if created:
                # Add category to the tour
                tour.categories.add(category)
                self.stdout.write(self.style.SUCCESS(f'Created tour: {tour.name}'))
            else:
                self.stdout.write(f'Tour already exists: {tour.name}')
        else:
            self.stdout.write(self.style.WARNING('No destinations or categories found. Skipping tour creation.'))
