from django.db import migrations
from django.conf import settings

def create_default_site(apps, schema_editor):
    """
    Create a default Site object for the application.
    This is needed for django-allauth to work properly.
    """
    # Get the Site model from the app registry
    Site = apps.get_model('sites', 'Site')
    
    # Check if we already have a site with ID 1
    if not Site.objects.filter(id=1).exists():
        # Create a default site
        domain = getattr(settings, 'SITE_DOMAIN', 'example.com')
        name = getattr(settings, 'SITE_NAME', 'Tourism Project')
        
        Site.objects.create(
            id=1,
            domain=domain,
            name=name
        )
        print(f"Created default site: {name} ({domain})")
    else:
        # Update the existing site
        site = Site.objects.get(id=1)
        domain = getattr(settings, 'SITE_DOMAIN', 'example.com')
        name = getattr(settings, 'SITE_NAME', 'Tourism Project')
        
        site.domain = domain
        site.name = name
        site.save()
        print(f"Updated default site: {name} ({domain})")

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),  # Make sure sites app migrations run first
    ]

    operations = [
        migrations.RunPython(create_default_site, migrations.RunPython.noop),
    ]
