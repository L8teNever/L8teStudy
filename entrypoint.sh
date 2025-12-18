#!/bin/bash
# Entrypoint script for L8teStudy Docker container

set -e

echo "Starting L8teStudy..."

# Ensure data directory exists
mkdir -p /data/uploads

# Set proper permissions
chmod -R 755 /data

# Check if database exists
if [ ! -f /data/l8testudy.db ]; then
    echo "Database not found. It will be created on first run..."
fi

# Start the application
# The database tables will be created automatically by app/__init__.py
# Note: Removed --preload to avoid race conditions with multiple workers
exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
