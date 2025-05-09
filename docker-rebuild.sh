#!/bin/bash
# Script to rebuild the Docker environment with a fresh database

# Stop any running containers
echo "Stopping running containers..."
docker-compose down -v

# Build and start with database rebuild flag
echo "Building and starting containers with database rebuild..."
REBUILD_DB=true docker-compose up --build

echo "Done! Your application should now be running with a fresh database."
