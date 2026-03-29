# Backend Dockerfile for OpenShift deployment
FROM registry.access.redhat.com/ubi9/python-311:latest

# Switch to root for installations
USER 0

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY backend/requirements.txt backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY api_client.py .
COPY orchestrator.py .
COPY backend/ backend/

# Create necessary directories with proper permissions
RUN mkdir -p output && \
    chmod -R 777 output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py

# Expose port
EXPOSE 5001

# Set proper permissions for OpenShift
RUN chown -R 1001:0 /app && \
    chmod -R g+rwX /app

# Switch back to non-root user
USER 1001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/api/health')"

# Start the Flask application
CMD ["python", "backend/app.py"]

# Made with Bob
