#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies and build
npm install
npm run build

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
