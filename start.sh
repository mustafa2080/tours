#!/bin/bash

# Print environment information
echo "Environment information:"
echo "DATABASE_URL: $DATABASE_URL"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "DEBUG: $DEBUG"

# Check if we're running on Railway by checking if the /data directory exists
if [ -d "/data" ]; then
    # Restore SQLite database from persistent storage if available
    echo "Restoring SQLite database from persistent storage..."
    python manage.py restore_sqlite_db

    # If the database doesn't exist, initialize it
    if [ ! -f "db.sqlite3" ]; then
        echo "Database not found, initializing new database..."
        python manage.py initialize_sqlite_db
    else
        # Apply database migrations with verbose output
        echo "Applying database migrations..."
        python manage.py migrate --verbosity 2
    fi

    # Copy SQLite database to persistent storage
    echo "Copying SQLite database to persistent storage..."
    python manage.py copy_sqlite_db
else
    # Local development environment
    # Apply database migrations with verbose output
    echo "Applying database migrations..."
    # First, migrate the auth, contenttypes, and sites apps
    python manage.py migrate auth --verbosity 2
    python manage.py migrate contenttypes --verbosity 2
    python manage.py migrate sites --verbosity 2
    # Then migrate the core app
    python manage.py migrate core --verbosity 2
    # Then migrate the users app
    python manage.py migrate users --verbosity 2
    # Then migrate the tour app
    python manage.py migrate tour --verbosity 2
    # Then migrate the analytics app
    python manage.py migrate analytics --verbosity 2
    # Then migrate the remaining apps
    python manage.py migrate --verbosity 2
fi

# Check database tables
echo "Checking database tables..."
python manage.py inspectdb | grep -i "class Currency" || echo "Currency model not found in database"
python manage.py inspectdb | grep -i "class SiteVisit" || echo "SiteVisit model not found in database"

# Set up initial data only if not using the initialize_sqlite_db command
if [ ! -d "/data" ] || [ ! -f "db.sqlite3" ]; then
    echo "Setting up initial data..."
    # Create site data
    echo "Creating site data..."
    python create_site_data.py
    # Fix site table
    echo "Fixing site table..."
    python manage.py fix_site_table
    # Setup other initial data
    python manage.py setup_site
    python manage.py setup_currencies
    python manage.py setup_analytics
    python manage.py setup_tours
fi

# Start the server
echo "Starting server..."
gunicorn tourism_project.wsgi:application --bind 0.0.0.0:8080 --log-file -
