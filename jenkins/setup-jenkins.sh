#!/bin/bash

echo "🚀 Setting up Jenkins CI/CD Platform for Event Booking Platform..."

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
print_status "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop first."
    exit 1
fi
print_success "Docker is running"

# Check if kubectl is available
print_status "Checking kubectl availability..."
if ! command -v kubectl &> /dev/null; then
    print_warning "kubectl not found. Please install kubectl for Kubernetes deployment."
else
    print_success "kubectl is available"
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p ssl
mkdir -p logs
print_success "Directories created"

# Generate self-signed SSL certificate for local development
print_status "Generating SSL certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/nginx.key \
    -out ssl/nginx.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=event-booking.local" 2>/dev/null || {
    print_warning "Could not generate SSL certificate. Using HTTP only."
}

# Start Jenkins platform
print_status "Starting Jenkins CI/CD platform..."
docker-compose up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose ps

# Get Jenkins initial admin password
print_status "Getting Jenkins initial admin password..."
JENKINS_PASSWORD=$(docker exec jenkins-event-booking cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Password not available yet")

if [ "$JENKINS_PASSWORD" != "Password not available yet" ]; then
    print_success "Jenkins initial admin password: $JENKINS_PASSWORD"
else
    print_warning "Jenkins is still starting up. Please wait a few minutes and check again."
fi

# Add hosts entries
print_status "Adding hosts entries..."
echo "127.0.0.1 jenkins.event-booking.local" | sudo tee -a /etc/hosts > /dev/null 2>&1 || {
    print_warning "Could not add hosts entry. Please manually add: 127.0.0.1 jenkins.event-booking.local"
}
echo "127.0.0.1 registry.event-booking.local" | sudo tee -a /etc/hosts > /dev/null 2>&1 || {
    print_warning "Could not add hosts entry. Please manually add: 127.0.0.1 registry.event-booking.local"
}
echo "127.0.0.1 sonar.event-booking.local" | sudo tee -a /etc/hosts > /dev/null 2>&1 || {
    print_warning "Could not add hosts entry. Please manually add: 127.0.0.1 sonar.event-booking.local"
}

# Display access information
echo ""
print_success "🎉 Jenkins CI/CD Platform is now running!"
echo ""
echo "📋 Access Information:"
echo "   Jenkins Dashboard: http://jenkins.event-booking.local"
echo "   Docker Registry:   http://registry.event-booking.local"
echo "   SonarQube:        http://sonar.event-booking.local"
echo "   Health Check:     http://health.event-booking.local"
echo ""
echo "🔑 Jenkins Initial Admin Password: $JENKINS_PASSWORD"
echo ""
echo "📝 Next Steps:"
echo "   1. Open http://jenkins.event-booking.local in your browser"
echo "   2. Install suggested plugins"
echo "   3. Create admin user"
echo "   4. Import the Jenkinsfile from jenkins/Jenkinsfile"
echo "   5. Configure GitHub webhook: http://jenkins.event-booking.local/jenkins/github-webhook/"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"
echo ""

# Check if services are healthy
print_status "Performing health checks..."
sleep 10

# Check Jenkins
if curl -f http://jenkins.event-booking.local > /dev/null 2>&1; then
    print_success "Jenkins is responding"
else
    print_warning "Jenkins is not responding yet. Please wait a few more minutes."
fi

# Check Docker Registry
if curl -f http://registry.event-booking.local > /dev/null 2>&1; then
    print_success "Docker Registry is responding"
else
    print_warning "Docker Registry is not responding yet."
fi

# Check SonarQube
if curl -f http://sonar.event-booking.local > /dev/null 2>&1; then
    print_success "SonarQube is responding"
else
    print_warning "SonarQube is not responding yet."
fi

echo ""
print_success "Setup completed! 🚀"
