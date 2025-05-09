#!/bin/bash

# Print environment information
echo "Environment information:"
echo "DATABASE_URL: $DATABASE_URL"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "DEBUG: $DEBUG"

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

# Check database tables
echo "Checking database tables..."
python manage.py inspectdb | grep -i "class Currency" || echo "Currency model not found in database"
python manage.py inspectdb | grep -i "class SiteVisit" || echo "SiteVisit model not found in database"

# Set up initial data
echo "Setting up initial data..."
python manage.py setup_site
python manage.py setup_currencies
python manage.py setup_analytics
python manage.py setup_tours

# Start the server
echo "Starting server..."
gunicorn tourism_project.wsgi:application --bind 0.0.0.0:8080 --log-file -
