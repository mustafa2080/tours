import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Copies the SQLite database file to a persistent location on Railway'

    def handle(self, *args, **options):
        # Get the source database path
        source_db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        
        # Check if the source database exists
        if not os.path.exists(source_db_path):
            self.stdout.write(self.style.ERROR(f"Source database not found at {source_db_path}"))
            return
        
        # Get the destination directory (persistent storage on Railway)
        # Railway provides a /data directory for persistent storage
        railway_data_dir = '/data'
        
        # Check if we're running on Railway by checking if the /data directory exists
        if os.path.exists(railway_data_dir) and os.path.isdir(railway_data_dir):
            # Create a destination path
            dest_db_path = os.path.join(railway_data_dir, 'db.sqlite3')
            
            # Copy the database file
            try:
                shutil.copy2(source_db_path, dest_db_path)
                self.stdout.write(self.style.SUCCESS(f"Database copied from {source_db_path} to {dest_db_path}"))
                
                # Create a symbolic link back to the original location
                if os.path.exists(source_db_path):
                    os.remove(source_db_path)
                os.symlink(dest_db_path, source_db_path)
                self.stdout.write(self.style.SUCCESS(f"Created symbolic link from {dest_db_path} to {source_db_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error copying database: {str(e)}"))
        else:
            self.stdout.write(self.style.WARNING("Not running on Railway or /data directory not found. Skipping database copy."))
