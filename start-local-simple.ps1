# PowerShell script to start Event Booking Platform - Local Development Environment
Write-Host "Starting Event Booking Platform - Local Development Environment" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker is running" -ForegroundColor Green
    } else {
        throw "Docker not accessible"
    }
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host ""
    Write-Host "To start Docker Desktop:" -ForegroundColor Cyan
    Write-Host "   1. Open Docker Desktop application" -ForegroundColor White
    Write-Host "   2. Wait for it to fully start (green status)" -ForegroundColor White
    Write-Host "   3. Run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""

# Check Docker resources
Write-Host "Checking Docker resources..." -ForegroundColor Yellow
docker system df
Write-Host ""

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @(
    "nginx\logs",
    "nginx\ssl", 
    "monitoring\grafana\provisioning",
    "monitoring\grafana\dashboards",
    "backups",
    "jenkins"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   Created: $dir" -ForegroundColor Green
    }
}

Write-Host "Directories created" -ForegroundColor Green
Write-Host ""

# Check if custom Jenkins Dockerfile exists
if (!(Test-Path "jenkins\Dockerfile")) {
    Write-Host "Custom Jenkins Dockerfile not found!" -ForegroundColor Red
    Write-Host "Please ensure jenkins\Dockerfile exists before running this script." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "Custom Jenkins Dockerfile found" -ForegroundColor Green
Write-Host ""

# Start infrastructure services first
Write-Host "Starting infrastructure services..." -ForegroundColor Yellow
Write-Host "Starting: PostgreSQL, Redis, RabbitMQ, Zookeeper, Kafka..." -ForegroundColor White
docker compose -f docker-compose.local.yml up -d postgres redis rabbitmq zookeeper kafka

# Check if infrastructure services started successfully
Write-Host "Waiting for infrastructure services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Start monitoring services
Write-Host "Starting monitoring services..." -ForegroundColor Yellow
Write-Host "Starting: Prometheus, Grafana..." -ForegroundColor White
docker compose -f docker-compose.local.yml up -d prometheus grafana

# Wait for monitoring to be ready
Write-Host "Waiting for monitoring services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Start application services
Write-Host "Starting application services..." -ForegroundColor Yellow
Write-Host "Starting: Auth, Catalog, Booking, Payment services..." -ForegroundColor White
docker compose -f docker-compose.local.yml up -d auth catalog booking payment

# Wait for application services to be ready
Write-Host "Waiting for application services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml up -d frontend

# Wait for frontend to be ready
Write-Host "Waiting for frontend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Start CI/CD tools with custom Jenkins build
Write-Host "Starting CI/CD tools..." -ForegroundColor Yellow
Write-Host "Building and starting: Jenkins (with Docker CLI), SonarQube, Docker Registry..." -ForegroundColor White

# Build and start Jenkins with custom Dockerfile
Write-Host "Building custom Jenkins image with Docker CLI..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml up -d --build jenkins

# Start other CI/CD tools
docker compose -f docker-compose.local.yml up -d sonarqube registry

# Wait for CI/CD tools to be ready
Write-Host "Waiting for CI/CD tools to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Verify all services are running
Write-Host "Verifying all services are running..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml ps

Write-Host ""
Write-Host "Local Development Environment Started Successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Application Access Points:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Auth API: http://localhost:8001/docs" -ForegroundColor White
Write-Host "   Catalog API: http://localhost:8002/docs" -ForegroundColor White
Write-Host "   Booking API: http://localhost:8003/docs" -ForegroundColor White
Write-Host "   Payment API: http://localhost:8004/docs" -ForegroundColor White
Write-Host ""
Write-Host "Admin Tools:" -ForegroundColor Cyan
Write-Host "   pgAdmin: http://localhost:5050 (admin@admin.com / admin)" -ForegroundColor White
Write-Host "   RabbitMQ: http://localhost:15672 (admin / admin)" -ForegroundColor White
Write-Host "   Kafka UI: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "CI/CD Tools:" -ForegroundColor Cyan
Write-Host "   Jenkins: http://localhost:8081 (admin / admin) - WITH DOCKER CLI" -ForegroundColor White
Write-Host "   SonarQube: http://localhost:9000 (admin / admin)" -ForegroundColor White
Write-Host "   Docker Registry: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Monitoring:" -ForegroundColor Cyan
Write-Host "   Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "   Grafana: http://localhost:3001 (admin / admin)" -ForegroundColor White
Write-Host ""
Write-Host "Docker Information:" -ForegroundColor Cyan
Write-Host "   Jenkins now has Docker CLI installed" -ForegroundColor White
Write-Host "   Can build and push Docker images" -ForegroundColor White
Write-Host "   Access to host Docker daemon" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "   View services: docker compose -f docker-compose.local.yml ps" -ForegroundColor White
Write-Host "   View logs: docker compose -f docker-compose.local.yml logs [service-name]" -ForegroundColor White
Write-Host "   Stop services: docker compose -f docker-compose.local.yml down" -ForegroundColor White
Write-Host "   Restart services: docker compose -f docker-compose.local.yml restart" -ForegroundColor White
Write-Host "   Test Jenkins Docker: docker compose -f docker-compose.local.yml exec jenkins docker version" -ForegroundColor White
Write-Host ""
Write-Host "Jenkins Pipeline Setup:" -ForegroundColor Cyan
Write-Host "   1. Open Jenkins: http://localhost:8081" -ForegroundColor White
Write-Host "   2. Create new Pipeline job" -ForegroundColor White
Write-Host "   3. Use Pipeline script (not SCM) for local development" -ForegroundColor White
Write-Host "   4. Copy Jenkinsfile content from jenkins\Jenkinsfile.local" -ForegroundColor White
Write-Host ""
Write-Host "This is a development setup. For production, use docker-compose.prod.yml" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Test Jenkins Docker access" -ForegroundColor White
Write-Host "   2. Create and run your first pipeline" -ForegroundColor White
Write-Host "   3. Build and deploy your services" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
