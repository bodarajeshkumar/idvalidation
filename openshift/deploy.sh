#!/bin/bash

# OpenShift Deployment Script for Data Retrieval System
# This script automates the deployment process to OpenShift

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="${OPENSHIFT_PROJECT:-data-retrieval}"
REGISTRY="image-registry.openshift-image-registry.svc:5000"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Data Retrieval System - OpenShift Deploy${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if oc CLI is installed
if ! command -v oc &> /dev/null; then
    print_error "OpenShift CLI (oc) is not installed. Please install it first."
    exit 1
fi

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    print_error "Not logged in to OpenShift. Please run 'oc login' first."
    exit 1
fi

print_info "Logged in as: $(oc whoami)"
print_info "Current server: $(oc whoami --show-server)"
echo ""

# Create or switch to project
print_info "Creating/switching to project: ${PROJECT_NAME}"
if oc get project ${PROJECT_NAME} &> /dev/null; then
    oc project ${PROJECT_NAME}
    print_info "Switched to existing project: ${PROJECT_NAME}"
else
    oc new-project ${PROJECT_NAME} --display-name="Data Retrieval System"
    print_info "Created new project: ${PROJECT_NAME}"
fi
echo ""

# Create secrets
print_info "Creating secrets..."
if oc get secret cloudant-credentials &> /dev/null; then
    print_warning "Secret 'cloudant-credentials' already exists. Skipping..."
else
    print_warning "Please update openshift/secrets.yaml with your actual credentials before deploying!"
    read -p "Have you updated the secrets.yaml file? (yes/no): " confirm
    if [[ $confirm != "yes" ]]; then
        print_error "Please update secrets.yaml and run this script again."
        exit 1
    fi
    oc apply -f openshift/secrets.yaml
    print_info "Secrets created successfully"
fi
echo ""

# Note: Using emptyDir volumes instead of PVCs
print_info "Using emptyDir volumes for storage (data stored within pods)"
echo ""

# Create ImageStreams
print_info "Creating ImageStreams..."
if ! oc get is backend &> /dev/null; then
    oc create imagestream backend
    print_info "Backend ImageStream created"
else
    print_warning "Backend ImageStream already exists"
fi

if ! oc get is frontend &> /dev/null; then
    oc create imagestream frontend
    print_info "Frontend ImageStream created"
else
    print_warning "Frontend ImageStream already exists"
fi
echo ""

# Create BuildConfigs
print_info "Creating BuildConfigs..."
oc apply -f openshift/backend-buildconfig.yaml
oc apply -f openshift/frontend-buildconfig.yaml
print_info "BuildConfigs created successfully"
echo ""

# Build backend image from GitHub
print_info "Building backend image from GitHub..."
print_info "This may take a few minutes..."
oc start-build backend --follow --build-loglevel=5
if [ $? -eq 0 ]; then
    print_info "Backend image built successfully"
else
    print_error "Backend build failed. Check logs with: oc logs -f bc/backend"
    exit 1
fi
echo ""

# Build frontend image from GitHub
print_info "Building frontend image from GitHub..."
print_info "This may take several minutes (building React app)..."
oc start-build frontend --follow --build-loglevel=5
if [ $? -eq 0 ]; then
    print_info "Frontend image built successfully"
else
    print_error "Frontend build failed. Check logs with: oc logs -f bc/frontend"
    exit 1
fi
echo ""

# Get backend route URL
print_info "Getting backend route URL..."
BACKEND_ROUTE_URL=$(oc get route backend-route -o jsonpath='{.spec.host}' 2>/dev/null || echo "")

if [ -z "$BACKEND_ROUTE_URL" ]; then
    print_warning "Backend route not found yet, will be created later"
    BACKEND_API_URL="https://backend-route-${PROJECT_NAME}.apps.cluster.example.com"
else
    BACKEND_API_URL="https://${BACKEND_ROUTE_URL}"
fi

print_info "Backend API URL will be: ${BACKEND_API_URL}"
echo ""

# Update deployment files with correct image references and API URL
print_info "Updating deployment configurations..."
sed -i.bak "s|YOUR_PROJECT|${PROJECT_NAME}|g" openshift/backend-deployment.yaml
sed -i.bak "s|YOUR_PROJECT|${PROJECT_NAME}|g" openshift/frontend-deployment.yaml
sed -i.bak "s|BACKEND_API_URL_PLACEHOLDER|${BACKEND_API_URL}|g" openshift/frontend-deployment.yaml
echo ""

# Deploy services
print_info "Creating services..."
oc apply -f openshift/services.yaml
print_info "Services created successfully"
echo ""

# Create routes first to get backend URL
print_info "Creating routes..."
oc apply -f openshift/routes.yaml
print_info "Routes created successfully"
echo ""

# Wait a moment for routes to be ready
sleep 3

# Get actual backend route URL
BACKEND_ROUTE_URL=$(oc get route backend-route -o jsonpath='{.spec.host}')
BACKEND_API_URL="https://${BACKEND_ROUTE_URL}"
print_info "Backend API URL: ${BACKEND_API_URL}"

# Update frontend deployment with actual backend URL
sed -i.bak2 "s|BACKEND_API_URL_PLACEHOLDER|${BACKEND_API_URL}|g" openshift/frontend-deployment.yaml
echo ""

# Deploy backend
print_info "Deploying backend..."
oc apply -f openshift/backend-deployment.yaml
print_info "Backend deployment created"
echo ""

# Deploy frontend
print_info "Deploying frontend..."
oc apply -f openshift/frontend-deployment.yaml
print_info "Frontend deployment created"
echo ""

# Wait for deployments to be ready
print_info "Waiting for deployments to be ready..."
oc rollout status deployment/backend --timeout=5m
oc rollout status deployment/frontend --timeout=5m
echo ""

# Get route URLs
FRONTEND_URL=$(oc get route frontend-route -o jsonpath='{.spec.host}')
BACKEND_URL=$(oc get route backend-route -o jsonpath='{.spec.host}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Frontend URL:${NC} https://${FRONTEND_URL}"
echo -e "${GREEN}Backend URL:${NC} https://${BACKEND_URL}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Access the frontend at: https://${FRONTEND_URL}"
echo "2. Check pod status: oc get pods"
echo "3. View logs: oc logs -f deployment/backend"
echo "4. Scale deployment: oc scale deployment/backend --replicas=2"
echo ""
echo -e "${GREEN}Deployment successful!${NC}"

# Made with Bob
