from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Fix the Site record for django.contrib.sites'

    def handle(self, *args, **options):
        site_id = settings.SITE_ID
        
        # Check if the Site with the specified ID exists
        try:
            site = Site.objects.get(id=site_id)
            self.stdout.write(f"Existing site found: {site.domain}")
            
            # Update the site domain if needed
            site.domain = 'localhost:8000'
            site.name = 'Tourism Project Development'
            site.save()
            self.stdout.write(self.style.SUCCESS(f"Updated site: {site.domain}"))
            
        except Site.DoesNotExist:
            # Create a new Site record
            site = Site.objects.create(
                id=site_id,
                domain='localhost:8000',
                name='Tourism Project Development'
            )
            self.stdout.write(self.style.SUCCESS(f"Created new site: {site.domain}"))
        
        # List all sites
        sites = Site.objects.all()
        self.stdout.write("All sites in database:")
        for s in sites:
            self.stdout.write(f"  - ID: {s.id}, Domain: {s.domain}, Name: {s.name}")
