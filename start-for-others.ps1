# 🚀 Event Booking Platform - Quick Start Script
# For other developers to get the project running quickly

Write-Host "🚀 Starting Event Booking Platform..." -ForegroundColor Green
Write-Host "📋 This script will set up your complete development environment" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "🔍 Checking Docker status..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host "💡 Download Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Start infrastructure services
Write-Host "🏗️ Starting infrastructure services..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml up -d postgres redis rabbitmq kafka zookeeper

# Wait for infrastructure to be ready
Write-Host "⏳ Waiting for infrastructure to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Start application services
Write-Host "🚀 Starting application services..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml up -d auth catalog booking payment frontend worker

# Start CI/CD tools
Write-Host "🔧 Starting CI/CD tools..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml up -d jenkins registry sonarqube prometheus grafana

# Wait for all services to start
Write-Host "⏳ Waiting for all services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Yellow
docker compose -f docker-compose.local.yml ps

Write-Host ""
Write-Host "🎉 Event Booking Platform is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access your application at:" -ForegroundColor Cyan
Write-Host "   Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "   Auth Service: http://localhost:8001" -ForegroundColor White
Write-Host "   Catalog:      http://localhost:8002" -ForegroundColor White
Write-Host "   Booking:      http://localhost:8003" -ForegroundColor White
Write-Host "   Payment:      http://localhost:8004" -ForegroundColor White
Write-Host "   Jenkins:      http://localhost:8081" -ForegroundColor White
Write-Host "   Registry:     http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "💡 Check SETUP_GUIDE.md for detailed information" -ForegroundColor Yellow
Write-Host "🚀 Happy coding!" -ForegroundColor Green
