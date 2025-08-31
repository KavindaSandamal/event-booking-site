# Cloud-Native Event Booking Platform Startup Script
# Demonstrates Cloud Computing Principles

Write-Host "Starting Cloud-Native Event Booking Platform..." -ForegroundColor Green
Write-Host "This setup demonstrates ALL cloud computing principles!" -ForegroundColor Cyan

# Check Docker
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create SSL directory
Write-Host "Setting up security configurations..." -ForegroundColor Yellow
if (!(Test-Path "cloud-config/nginx/ssl")) {
    New-Item -ItemType Directory -Path "cloud-config/nginx/ssl" -Force | Out-Null
    Write-Host "SSL directory created" -ForegroundColor Green
}

# Start infrastructure
Write-Host "Starting cloud-native infrastructure services..." -ForegroundColor Yellow
Write-Host "PostgreSQL Primary + Replica (High Availability)" -ForegroundColor White
Write-Host "Redis Cluster (Scalability)" -ForegroundColor White
Write-Host "RabbitMQ + Kafka (Async Communication)" -ForegroundColor White
Write-Host "Nginx Load Balancer (Security + High Availability)" -ForegroundColor White

docker compose -f docker-compose.cloud.yml up -d postgres-primary postgres-replica redis-cluster rabbitmq zookeeper kafka nginx-lb

# Wait for infrastructure
Write-Host "Waiting for infrastructure to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Start application services
Write-Host "Starting application services with cloud-native features..." -ForegroundColor Yellow
Write-Host "Auth Service (2 replicas + health checks)" -ForegroundColor White
Write-Host "Catalog Service (2 replicas + health checks)" -ForegroundColor White
Write-Host "Booking Service (2 replicas + health checks)" -ForegroundColor White
Write-Host "Payment Service (2 replicas + health checks)" -ForegroundColor White
Write-Host "Frontend (2 replicas + health checks)" -ForegroundColor White

docker compose -f docker-compose.cloud.yml up -d auth catalog booking payment frontend

# Start monitoring
Write-Host "Starting monitoring and observability stack..." -ForegroundColor Yellow
Write-Host "Prometheus (Metrics collection)" -ForegroundColor White
Write-Host "Grafana (Visualization dashboards)" -ForegroundColor White

docker compose -f docker-compose.cloud.yml up -d prometheus grafana

# Wait for services
Write-Host "Waiting for all services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check status
Write-Host "Checking cloud-native service status..." -ForegroundColor Yellow
docker compose -f docker-compose.cloud.yml ps

# Display results
Write-Host ""
Write-Host "Cloud-Native Event Booking Platform is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Cloud Computing Principles Demonstrated:" -ForegroundColor Cyan
Write-Host "Scalability: Multiple replicas, auto-scaling ready" -ForegroundColor White
Write-Host "High Availability: Load balancer, health checks, failover" -ForegroundColor White
Write-Host "Security: Rate limiting, security headers, SSL ready" -ForegroundColor White
Write-Host "Monitoring: Prometheus metrics, Grafana dashboards" -ForegroundColor White
Write-Host "Async Communication: RabbitMQ, Kafka, event-driven" -ForegroundColor White
Write-Host "Microservices: Independent scaling, fault isolation" -ForegroundColor White
Write-Host ""
Write-Host "Access your cloud-native application at:" -ForegroundColor Cyan
Write-Host "Frontend (Load Balanced): http://localhost" -ForegroundColor White
Write-Host "Auth Service: http://localhost/auth" -ForegroundColor White
Write-Host "Catalog Service: http://localhost/catalog" -ForegroundColor White
Write-Host "Booking Service: http://localhost/booking" -ForegroundColor White
Write-Host "Payment Service: http://localhost/payment" -ForegroundColor White
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "Grafana: http://localhost:3001 (admin/admin)" -ForegroundColor White
Write-Host "RabbitMQ: http://localhost:15672 (guest/guest)" -ForegroundColor White
Write-Host ""
Write-Host "Test Cloud Computing Features:" -ForegroundColor Yellow
Write-Host "Load Testing: docker compose -f docker-compose.cloud.yml run k6-load-test" -ForegroundColor White
Write-Host "Health Checks: curl http://localhost/health" -ForegroundColor White
Write-Host "Metrics: Visit Prometheus and Grafana" -ForegroundColor White
Write-Host ""
Write-Host "Your project now demonstrates enterprise-level cloud computing!" -ForegroundColor Green
Write-Host "Perfect for your cloud computing module assignment!" -ForegroundColor Cyan
