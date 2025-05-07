from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration merges the old and new booking system migrations.
    It sets up a fresh start for the new booking system.
    """

    dependencies = [
        ('booking', '0004_merge_20250424_2041'),
    ]

    operations = [
        # No operations needed - this migration just merges the two branches
    ]