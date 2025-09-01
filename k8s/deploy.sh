#!/bin/bash

# Event Booking Platform - Kubernetes Deployment Script
# This script demonstrates production-grade deployment practices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="event-booking"
ENVIRONMENT=${1:-dev}

echo -e "${BLUE}🚀 Event Booking Platform - Kubernetes Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo ""

# Function to check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed. Please install kubectl first.${NC}"
        exit 1
    fi
}

# Function to check if minikube is running
check_minikube() {
    if ! minikube status | grep -q "Running"; then
        echo -e "${YELLOW}⚠️  Minikube is not running. Starting minikube...${NC}"
        minikube start --cpus=4 --memory=8192 --disk-size=20g
        echo -e "${GREEN}✅ Minikube started successfully${NC}"
    else
        echo -e "${GREEN}✅ Minikube is running${NC}"
    fi
}

# Function to create namespace
create_namespace() {
    echo -e "${BLUE}📦 Creating namespace: ${NAMESPACE}${NC}"
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    echo -e "${GREEN}✅ Namespace created${NC}"
}

# Function to deploy base resources
deploy_base() {
    echo -e "${BLUE}🏗️  Deploying base infrastructure...${NC}"
    
    # Apply base manifests
    kubectl apply -f base/namespace.yaml
    kubectl apply -f base/configmap.yaml
    kubectl apply -f base/postgres.yaml
    kubectl apply -f base/redis.yaml
    
    echo -e "${GREEN}✅ Base infrastructure deployed${NC}"
}

# Function to deploy services
deploy_services() {
    echo -e "${BLUE}🔧 Deploying microservices...${NC}"
    
    # Apply service manifests
    kubectl apply -f base/auth-service.yaml
    kubectl apply -f base/catalog-service.yaml
    kubectl apply -f base/booking-service.yaml
    kubectl apply -f base/payment-service.yaml
    kubectl apply -f base/frontend-service.yaml
    
    echo -e "${GREEN}✅ Microservices deployed${NC}"
}

# Function to deploy monitoring
deploy_monitoring() {
    echo -e "${BLUE}📊 Deploying monitoring stack...${NC}"
    
    kubectl apply -f base/monitoring.yaml
    
    echo -e "${GREEN}✅ Monitoring stack deployed${NC}"
}

# Function to deploy ingress
deploy_ingress() {
    echo -e "${BLUE}🌐 Deploying ingress controller...${NC}"
    
    # Install NGINX Ingress Controller if not exists
    if ! kubectl get namespace ingress-nginx &> /dev/null; then
        echo -e "${YELLOW}⚠️  Installing NGINX Ingress Controller...${NC}"
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
        kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s
    fi
    
    kubectl apply -f base/ingress.yaml
    
    echo -e "${GREEN}✅ Ingress deployed${NC}"
}

# Function to check deployment status
check_status() {
    echo -e "${BLUE}🔍 Checking deployment status...${NC}"
    
    echo -e "${YELLOW}Pods:${NC}"
    kubectl get pods -n ${NAMESPACE}
    
    echo -e "${YELLOW}Services:${NC}"
    kubectl get services -n ${NAMESPACE}
    
    echo -e "${YELLOW}Deployments:${NC}"
    kubectl get deployments -n ${NAMESPACE}
    
    echo -e "${YELLOW}HPA:${NC}"
    kubectl get hpa -n ${NAMESPACE}
    
    echo -e "${YELLOW}Ingress:${NC}"
    kubectl get ingress -n ${NAMESPACE}
}

# Function to scale services
scale_services() {
    echo -e "${BLUE}📈 Scaling services...${NC}"
    
    # Scale auth service to 5 replicas
    kubectl scale deployment auth-service --replicas=5 -n ${NAMESPACE}
    
    # Scale catalog service to 3 replicas
    kubectl scale deployment catalog-service --replicas=3 -n ${NAMESPACE}
    
    # Scale booking service to 4 replicas
    kubectl scale deployment booking-service --replicas=4 -n ${NAMESPACE}
    
    echo -e "${GREEN}✅ Services scaled${NC}"
}

# Function to show access information
show_access_info() {
    echo -e "${BLUE}🌍 Access Information:${NC}"
    
    # Get minikube IP
    MINIKUBE_IP=$(minikube ip)
    
    echo -e "${GREEN}Frontend:${NC} http://${MINIKUBE_IP}"
    echo -e "${GREEN}Prometheus:${NC} http://${MINIKUBE_IP}:30000"
    echo -e "${GREEN}Grafana:${NC} http://${MINIKUBE_IP}:30001"
    
    echo ""
    echo -e "${YELLOW}To access the application, add this to your /etc/hosts:${NC}"
    echo -e "${YELLOW}${MINIKUBE_IP} event-booking.local${NC}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    check_kubectl
    check_minikube
    
    echo -e "${BLUE}🚀 Starting deployment...${NC}"
    create_namespace
    deploy_base
    
    echo -e "${BLUE}⏳ Waiting for infrastructure to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=postgres-primary -n ${NAMESPACE} --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis-cluster -n ${NAMESPACE} --timeout=300s
    
    deploy_services
    deploy_monitoring
    deploy_ingress
    
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    kubectl wait --for=condition=available deployment --all -n ${NAMESPACE} --timeout=300s
    
    scale_services
    
    echo -e "${BLUE}⏳ Waiting for scaling to complete...${NC}"
    sleep 30
    
    check_status
    show_access_info
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "${YELLOW}1. Add the host entry to your /etc/hosts file${NC}"
    echo -e "${YELLOW}2. Access the application at http://event-booking.local${NC}"
    echo -e "${YELLOW}3. Monitor with: kubectl get pods -n ${NAMESPACE} -w${NC}"
}

# Run main function
main "$@"
