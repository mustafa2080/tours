#!/bin/bash

# Print environment information
echo "Environment information:"
echo "DATABASE_URL: $DATABASE_URL"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "DEBUG: $DEBUG"

# Apply database migrations with verbose output
echo "Applying database migrations..."
python manage.py migrate --verbosity 2

# Check database tables
echo "Checking database tables..."
python manage.py inspectdb | grep -i "class Currency" || echo "Currency model not found in database"
python manage.py inspectdb | grep -i "class SiteVisit" || echo "SiteVisit model not found in database"

# Set up initial data
echo "Setting up initial data..."
python manage.py setup_currencies
python manage.py setup_analytics

# Start the server
echo "Starting server..."
gunicorn tourism_project.wsgi:application --bind 0.0.0.0:8080 --log-file -
