import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourism_project.settings')
django.setup()

def create_site_data():
    """
    Create or update the default site object.
    This is needed for django-allauth to work properly.
    """
    from django.contrib.sites.models import Site
    
    # Get domain and name from settings
    domain = getattr(settings, 'SITE_DOMAIN', 'example.com')
    name = getattr(settings, 'SITE_NAME', 'Tourism Project')
    
    # Check if we already have a site with ID 1
    try:
        site = Site.objects.get(id=1)
        # Update the existing site
        site.domain = domain
        site.name = name
        site.save()
        print(f"Updated default site: {name} ({domain})")
    except Site.DoesNotExist:
        # Create a default site
        Site.objects.create(
            id=1,
            domain=domain,
            name=name
        )
        print(f"Created default site: {name} ({domain})")

if __name__ == "__main__":
    create_site_data()
    print("Site data creation/update completed successfully.")
