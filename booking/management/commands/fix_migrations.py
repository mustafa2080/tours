from django.core.management.base import BaseCommand
import os
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Fix booking app migrations for the new booking system'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration fix process...')
        
        # Setup paths
        migrations_dir = Path('booking/migrations')
        backup_dir = migrations_dir / 'backup'
        
        # Create backup directory
        backup_dir.mkdir(exist_ok=True)
        
        # Backup existing migrations
        for migration_file in migrations_dir.glob('*.py'):
            if migration_file.name != '__init__.py' and migration_file.name != 'new_0001_initial.py':
                try:
                    shutil.move(str(migration_file), str(backup_dir / migration_file.name))
                    self.stdout.write(f'Backed up {migration_file.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error backing up {migration_file.name}: {e}'))
        
        # Rename new migration
        old_path = migrations_dir / 'new_0001_initial.py'
        new_path = migrations_dir / '0001_initial.py'
        
        if old_path.exists():
            try:
                if new_path.exists():
                    new_path.unlink()
                old_path.rename(new_path)
                self.stdout.write(self.style.SUCCESS('Renamed new_0001_initial.py to 0001_initial.py'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error renaming migration: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\nMigration files updated. Now run:'))
        self.stdout.write('python manage.py makemigrations booking')
        self.stdout.write('python manage.py migrate')