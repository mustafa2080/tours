#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies and build
# Check if npm is available
if command -v npm &> /dev/null; then
    echo "Installing npm dependencies..."
    npm install
    npm run build
else
    echo "npm not found, skipping frontend build"
fi

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
