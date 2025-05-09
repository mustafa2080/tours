#!/usr/bin/env bash
# exit on error
set -o errexit

# Install frontend dependencies and build
npm install
npm run build

echo "Frontend assets built successfully!"
