from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Fixes the django_site table by ensuring it exists and has the correct data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting site table fix...'))
        
        # Check if the django_site table exists
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='django_site'")
                table_exists = cursor.fetchone() is not None
            except Exception:
                # For PostgreSQL or other databases
                try:
                    cursor.execute("SELECT to_regclass('django_site')")
                    table_exists = cursor.fetchone()[0] is not None
                except Exception:
                    table_exists = False
        
        if not table_exists:
            self.stdout.write(self.style.WARNING('django_site table does not exist. Running migrations...'))
            from django.core.management import call_command
            call_command('migrate', 'sites', verbosity=2)
        
        # Get domain and name from settings
        domain = getattr(settings, 'SITE_DOMAIN', 'example.com')
        name = getattr(settings, 'SITE_NAME', 'Tourism Project')
        
        self.stdout.write(f"Attempting to create/update site with domain: {domain}, name: {name}")
        
        # Check if we already have a site with ID 1
        try:
            site = Site.objects.get(id=1)
            # Update the existing site
            site.domain = domain
            site.name = name
            site.save()
            self.stdout.write(self.style.SUCCESS(f"Updated default site: {name} ({domain})"))
        except Site.DoesNotExist:
            # Create a default site
            Site.objects.create(
                id=1,
                domain=domain,
                name=name
            )
            self.stdout.write(self.style.SUCCESS(f"Created default site: {name} ({domain})"))
        
        # Verify the site was created/updated
        try:
            site = Site.objects.get(id=1)
            self.stdout.write(self.style.SUCCESS(f"Site verification successful: {site.domain}"))
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Site verification failed: Site with ID 1 does not exist"))
        
        # List all sites for debugging
        self.stdout.write("All sites in database:")
        for site in Site.objects.all():
            self.stdout.write(f"  - ID: {site.id}, Domain: {site.domain}, Name: {site.name}")
