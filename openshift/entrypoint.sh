#!/bin/sh
# Entrypoint script to inject runtime configuration

# Replace placeholder in config.js with actual backend URL
if [ -n "$REACT_APP_API_URL" ]; then
    echo "Injecting backend URL: $REACT_APP_API_URL"
    sed -i "s|BACKEND_API_URL_PLACEHOLDER|$REACT_APP_API_URL|g" /opt/app-root/src/config.js
else
    echo "Warning: REACT_APP_API_URL not set, using placeholder"
fi

# Start nginx
exec nginx -g 'daemon off;'

# Made with Bob
