from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.models import SiteVisit
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial analytics data'

    def handle(self, *args, **options):
        # Create a sample site visit
        try:
            # Get or create a superuser for the sample visit
            admin_user = None
            if User.objects.filter(is_superuser=True).exists():
                admin_user = User.objects.filter(is_superuser=True).first()
            
            # Create a sample site visit
            SiteVisit.objects.get_or_create(
                path='/',
                defaults={
                    'user': admin_user,
                    'ip_address': '127.0.0.1',
                    'user_agent': 'Sample User Agent',
                    'timestamp': timezone.now(),
                    'country': 'Sample Country',
                    'city': 'Sample City',
                    'region': 'Sample Region',
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS('Successfully set up analytics data')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up analytics data: {e}')
            )
