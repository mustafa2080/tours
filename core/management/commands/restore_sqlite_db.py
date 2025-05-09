import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Restores the SQLite database file from a persistent location on Railway'

    def handle(self, *args, **options):
        # Get the destination database path
        dest_db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        
        # Get the source directory (persistent storage on Railway)
        railway_data_dir = '/data'
        source_db_path = os.path.join(railway_data_dir, 'db.sqlite3')
        
        # Check if we're running on Railway by checking if the /data directory exists
        if os.path.exists(railway_data_dir) and os.path.isdir(railway_data_dir):
            # Check if the source database exists
            if os.path.exists(source_db_path):
                # Copy the database file
                try:
                    # If the destination already exists, remove it first
                    if os.path.exists(dest_db_path):
                        if os.path.islink(dest_db_path):
                            os.unlink(dest_db_path)
                        else:
                            os.remove(dest_db_path)
                    
                    # Create a symbolic link
                    os.symlink(source_db_path, dest_db_path)
                    self.stdout.write(self.style.SUCCESS(f"Created symbolic link from {source_db_path} to {dest_db_path}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error restoring database: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f"Source database not found at {source_db_path}"))
        else:
            self.stdout.write(self.style.WARNING("Not running on Railway or /data directory not found. Skipping database restore."))
