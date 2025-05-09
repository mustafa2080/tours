#!/usr/bin/env bash
# exit on error
set -o errexit

# Build frontend assets first
echo "Building frontend assets..."
chmod +x ./build-frontend.sh
./build-frontend.sh

# Build Docker image
echo "Building Docker image..."
docker build -t tourism-project .

echo "Docker image built successfully!"
echo "Run with: docker run -p 8000:8000 tourism-project"
