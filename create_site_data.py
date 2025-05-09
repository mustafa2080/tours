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
    from django.db import connection

    # First, check if the django_site table exists
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
        print("django_site table does not exist. Running migrations...")
        from django.core.management import call_command
        call_command('migrate', 'sites', verbosity=2)

    # Get domain and name from settings
    domain = getattr(settings, 'SITE_DOMAIN', 'example.com')
    name = getattr(settings, 'SITE_NAME', 'Tourism Project')

    print(f"Attempting to create/update site with domain: {domain}, name: {name}")

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

    # Verify the site was created/updated
    try:
        site = Site.objects.get(id=1)
        print(f"Site verification successful: {site.domain}")
    except Site.DoesNotExist:
        print(f"Site verification failed: Site with ID 1 does not exist")

if __name__ == "__main__":
    create_site_data()
    print("Site data creation/update completed successfully.")
