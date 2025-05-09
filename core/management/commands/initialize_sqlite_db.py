import os
import sqlite3
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Initializes a new SQLite database with essential data'

    def handle(self, *args, **options):
        # Get the database path
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        
        # Check if the database already exists
        if os.path.exists(db_path):
            self.stdout.write(self.style.WARNING(f"Database already exists at {db_path}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Creating new SQLite database at {db_path}"))
        
        # Create an empty database file
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Run migrations
        self.stdout.write(self.style.SUCCESS("Running migrations..."))
        call_command('migrate', verbosity=2)
        
        # Load initial data
        self.stdout.write(self.style.SUCCESS("Loading initial data..."))
        
        # Load fixtures
        try:
            call_command('loaddata', 'core/fixtures/initial_data.json', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Loaded initial data from fixtures"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading fixtures: {str(e)}"))
        
        # Run setup commands
        try:
            call_command('fix_site_table', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Fixed site table"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fixing site table: {str(e)}"))
        
        try:
            call_command('setup_site', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Set up site"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up site: {str(e)}"))
        
        try:
            call_command('setup_currencies', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Set up currencies"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up currencies: {str(e)}"))
        
        try:
            call_command('setup_analytics', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Set up analytics"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up analytics: {str(e)}"))
        
        try:
            call_command('setup_tours', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Set up tours"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up tours: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Database initialization complete"))
