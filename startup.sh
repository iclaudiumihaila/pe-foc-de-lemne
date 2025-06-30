#!/bin/bash

# Get the PORT from environment variable, default to 8080
PORT=${PORT:-8080}

# Replace the port in nginx configuration
sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/sites-available/default

echo "Starting services on port $PORT..."

# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf