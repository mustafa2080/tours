from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Set up the default site domain'

    def handle(self, *args, **options):
        # Get the site URL from settings
        site_url = settings.SITE_URL
        
        # Remove protocol and trailing slash
        if site_url.startswith('http://'):
            domain = site_url[7:]
        elif site_url.startswith('https://'):
            domain = site_url[8:]
        else:
            domain = site_url
            
        if domain.endswith('/'):
            domain = domain[:-1]
            
        # Get or create the site with ID 1
        site, created = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={
                'domain': domain,
                'name': settings.SITE_NAME
            }
        )
        
        # If site already exists, update it
        if not created:
            site.domain = domain
            site.name = settings.SITE_NAME
            site.save()
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully set up site: {site.domain}')
        )
