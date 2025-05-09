from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from django.db import connection

class Command(BaseCommand):
    help = 'Set up the default site domain'

    def handle(self, *args, **options):
        # First, check if the django_site table exists
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT 1 FROM django_site LIMIT 1")
                table_exists = True
            except Exception:
                table_exists = False

        if not table_exists:
            self.stdout.write(self.style.WARNING('django_site table does not exist. Running migrations...'))
            from django.core.management import call_command
            call_command('migrate', 'sites', verbosity=2)

        # Get the site domain from settings
        domain = getattr(settings, 'SITE_DOMAIN', 'example.com')
        name = getattr(settings, 'SITE_NAME', 'Tourism Project')

        # Get or create the site with ID 1
        try:
            site = Site.objects.get(id=settings.SITE_ID)
            # Update the site
            site.domain = domain
            site.name = name
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Updated site: {site.domain}'))
        except Site.DoesNotExist:
            # Create the site
            site = Site.objects.create(
                id=settings.SITE_ID,
                domain=domain,
                name=name
            )
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))

        # Verify the site was created/updated
        try:
            site = Site.objects.get(id=settings.SITE_ID)
            self.stdout.write(self.style.SUCCESS(f'Site verification successful: {site.domain}'))
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Site verification failed: Site with ID {settings.SITE_ID} does not exist'))
