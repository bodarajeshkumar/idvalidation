# Multi-stage build for React frontend
# Stage 1: Build the React application
FROM registry.access.redhat.com/ubi9/nodejs-18:latest AS builder

# Switch to root for setup
USER 0

WORKDIR /opt/app-root/src

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/ .

# Build the application for production
# The .env.production file sets REACT_APP_API_URL to empty string for relative URLs
RUN npm run build

# Stage 2: Serve with nginx
FROM registry.access.redhat.com/ubi9/nginx-122:latest

# Switch to root for setup
USER 0

# Copy custom nginx configuration
COPY openshift/nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY openshift/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy built application from builder stage
COPY --from=builder /opt/app-root/src/build /opt/app-root/src

# Set proper permissions for OpenShift
RUN chown -R 1001:0 /opt/app-root/src && \
    chmod -R g+rwX /opt/app-root/src

# Switch back to non-root user
USER 1001

# Expose port 8080 (OpenShift default)
EXPOSE 8080

# Use entrypoint script to inject runtime config
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Made with Bob
