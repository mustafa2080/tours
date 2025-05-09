#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the server
echo "Starting server..."
gunicorn tourism_project.wsgi:application --bind 0.0.0.0:8080 --log-file -
