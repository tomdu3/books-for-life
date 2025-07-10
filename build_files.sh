#!/bin/bash

# Build script for Vercel deployment with Django and Cloudinary

echo "----- Starting build process -----"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt --no-cache-dir

# Validate Cloudinary configuration
if [ -z "$CLOUDINARY_URL" ]; then
    echo "ERROR: CLOUDINARY_URL environment variable not set"
    exit 1
fi

# Extract Cloudinary name from URL for verification
CLOUD_NAME=$(echo $CLOUDINARY_URL | awk -F'[@]' '{print $1}' | awk -F'[:]' '{print $3}')
if [ -z "$CLOUD_NAME" ]; then
    echo "ERROR: Could not extract Cloudinary cloud name from CLOUDINARY_URL"
    exit 1
fi

# Run database migrations (if needed)
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Verify static files were collected
if [ ! -d "staticfiles" ]; then
    echo "ERROR: staticfiles directory not created"
    exit 1
fi

echo "----- Build completed successfully -----"