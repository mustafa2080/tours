"""
This file is a simple helper script to manually run migrations.
To use, run `python booking/migrations/make_migrations.py`
"""

import os
import sys
import django
import shutil
from pathlib import Path
from django.core.management import execute_from_command_line

# Add the project directory to the sys.path
sys.path.append('D:\\projects\\tourism_project')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourism_project.settings')

# Initialize Django
django.setup()

def backup_migrations():
    """Backup existing migration files"""
    migrations_dir = Path('booking/migrations')
    backup_dir = migrations_dir / 'backup'
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)
    
    # Move all existing migration files to backup except __init__.py
    for migration_file in migrations_dir.glob('*.py'):
        if migration_file.name != '__init__.py' and migration_file.name != 'new_0001_initial.py':
            shutil.move(str(migration_file), str(backup_dir / migration_file.name))
    
    print("Existing migrations backed up to booking/migrations/backup/")

def rename_new_migration():
    """Rename new_0001_initial.py to 0001_initial.py"""
    migrations_dir = Path('booking/migrations')
    old_path = migrations_dir / 'new_0001_initial.py'
    new_path = migrations_dir / '0001_initial.py'
    
    if old_path.exists():
        # If 0001_initial.py exists, remove it first
        if new_path.exists():
            new_path.unlink()
        
        # Rename new_0001_initial.py to 0001_initial.py
        old_path.rename(new_path)
        print("Renamed new_0001_initial.py to 0001_initial.py")

def main():
    """
    Fix the migration issue by:
    1. Backing up existing migrations
    2. Renaming new migration to be the initial migration
    3. Making fresh migrations
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tourism_project.settings')
    
    print("Starting migration fix process...")
    
    # Backup existing migrations
    backup_migrations()
    
    # Rename new migration
    rename_new_migration()
    
    print("\nCreating new migrations...")
    
    # Make migrations for booking app
    sys.argv = ['manage.py', 'makemigrations', 'booking']
    execute_from_command_line(sys.argv)
    
    print("\nMigration files updated. Now run:")
    print("python manage.py migrate")

if __name__ == "__main__":
    main()
