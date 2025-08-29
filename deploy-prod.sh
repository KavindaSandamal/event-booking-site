#!/bin/bash

# 🚀 Event Booking Platform - Production Deployment Script
# This script deploys the complete production environment with CI/CD tools

set -e  # Exit on any error

echo "🚀 Starting Event Booking Platform Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if required files exist
check_files() {
    print_status "Checking required configuration files..."
    
    required_files=(
        "docker-compose.prod.yml"
        "env.prod"
        "nginx/nginx.conf"
        "nginx/conf.d/default.conf"
        "monitoring/prometheus.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All required files found"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p nginx/logs
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/provisioning
    mkdir -p monitoring/grafana/dashboards
    mkdir -p backups
    
    print_success "Directories created"
}

# Generate self-signed SSL certificate for testing
generate_ssl_cert() {
    print_status "Generating self-signed SSL certificate for testing..."
    
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        mkdir -p nginx/ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        print_success "SSL certificate generated"
    else
        print_status "SSL certificate already exists"
    fi
}

# Start production services
start_services() {
    print_status "Starting production services..."
    
    # Start infrastructure first
    print_status "Starting infrastructure services..."
    docker compose -f docker-compose.prod.yml up -d postgres redis rabbitmq zookeeper kafka
    
    # Wait for infrastructure to be ready
    print_status "Waiting for infrastructure services to be ready..."
    sleep 30
    
    # Start monitoring services
    print_status "Starting monitoring services..."
    docker compose -f docker-compose.prod.yml up -d prometheus grafana jaeger elasticsearch kibana
    
    # Wait for monitoring to be ready
    print_status "Waiting for monitoring services to be ready..."
    sleep 30
    
    # Start CI/CD tools
    print_status "Starting CI/CD tools..."
    docker compose -f docker-compose.prod.yml up -d jenkins sonarqube
    
    # Wait for CI/CD tools to be ready
    print_status "Waiting for CI/CD tools to be ready..."
    sleep 30
    
    # Start application services
    print_status "Starting application services..."
    docker compose -f docker-compose.prod.yml up -d auth catalog booking payment worker
    
    # Wait for application services to be ready
    print_status "Waiting for application services to be ready..."
    sleep 30
    
    # Start frontend and nginx
    print_status "Starting frontend and load balancer..."
    docker compose -f docker-compose.prod.yml up -d frontend nginx
    
    print_success "All services started"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    services=("auth" "catalog" "booking" "payment" "frontend")
    
    for service in "${services[@]}"; do
        print_status "Waiting for $service to be healthy..."
        timeout=120
        while [ $timeout -gt 0 ]; do
            if docker compose -f docker-compose.prod.yml ps $service | grep -q "healthy"; then
                print_success "$service is healthy"
                break
            fi
            sleep 5
            timeout=$((timeout - 5))
        done
        
        if [ $timeout -le 0 ]; then
            print_warning "$service health check timeout - continuing anyway"
        fi
    done
}

# Test services
test_services() {
    print_status "Testing services..."
    
    # Test Nginx health endpoint
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_success "Nginx load balancer is working"
    else
        print_warning "Nginx health check failed"
    fi
    
    # Test Kafka UI
    if curl -f http://localhost:8080 > /dev/null 2>&1; then
        print_success "Kafka UI is accessible"
    else
        print_warning "Kafka UI check failed"
    fi
    
    # Test Prometheus
    if curl -f http://localhost:9090 > /dev/null 2>&1; then
        print_success "Prometheus is accessible"
    else
        print_warning "Prometheus check failed"
    fi
    
    # Test Grafana
    if curl -f http://localhost:3001 > /dev/null 2>&1; then
        print_success "Grafana is accessible"
    else
        print_warning "Grafana check failed"
    fi
}

# Display service information
show_info() {
    echo ""
    echo "🎉 Event Booking Platform Production Environment Deployed Successfully!"
    echo ""
    echo "📱 Application Access Points:"
    echo "   • Frontend (via Nginx): http://localhost"
    echo "   • API Documentation: http://localhost/docs"
    echo "   • Health Check: http://localhost/health"
    echo ""
    echo "🔧 Admin Tools:"
    echo "   • pgAdmin: http://localhost:5050 (admin@admin.com / admin123)"
    echo "   • RabbitMQ: http://localhost:15672 (admin / admin123)"
    echo "   • Kafka UI: http://localhost:8080"
    echo ""
    echo "📊 Monitoring & Observability:"
    echo "   • Prometheus: http://localhost:9090"
    echo "   • Grafana: http://localhost:3001 (admin / admin123)"
    echo "   • Jaeger: http://localhost:16686"
    echo "   • Kibana: http://localhost:5601"
    echo ""
    echo "🚀 CI/CD Tools:"
    echo "   • Jenkins: http://localhost:8081"
    echo "   • SonarQube: http://localhost:9000"
    echo ""
    echo "🗄️ Infrastructure:"
    echo "   • PostgreSQL: localhost:5432"
    echo "   • Redis: localhost:6379"
    echo "   • Kafka: localhost:9092"
    echo ""
    echo "📋 Useful Commands:"
    echo "   • View all services: docker compose -f docker-compose.prod.yml ps"
    echo "   • View logs: docker compose -f docker-compose.prod.yml logs [service-name]"
    echo "   • Stop services: docker compose -f docker-compose.prod.yml down"
    echo "   • Restart services: docker compose -f docker-compose.prod.yml restart"
    echo ""
    echo "⚠️  Important Notes:"
    echo "   • This is a development setup with self-signed SSL certificates"
    echo "   • For production, replace SSL certificates and update domain names"
    echo "   • Update environment variables in env.prod for production use"
    echo "   • Consider using Kubernetes for production orchestration"
    echo ""
}

# Main deployment function
main() {
    echo "🚀 Event Booking Platform Production Deployment"
    echo "================================================"
    echo ""
    
    check_docker
    check_files
    create_directories
    generate_ssl_cert
    start_services
    wait_for_services
    test_services
    show_info
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"
