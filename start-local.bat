@echo off
echo 🚀 Starting Event Booking Platform - Local Development Environment
echo ================================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Create necessary directories
if not exist "nginx\logs" mkdir "nginx\logs"
if not exist "nginx\ssl" mkdir "nginx\ssl"
if not exist "monitoring\grafana\provisioning" mkdir "monitoring\grafana\provisioning"
if not exist "monitoring\grafana\dashboards" mkdir "monitoring\grafana\dashboards"
if not exist "backups" mkdir "backups"

echo ✅ Directories created
echo.

REM Start infrastructure services first
echo 🔧 Starting infrastructure services...
docker compose -f docker-compose.local.yml up -d postgres redis rabbitmq zookeeper kafka

REM Wait for infrastructure to be ready
echo ⏳ Waiting for infrastructure services to be ready...
timeout /t 30 /nobreak >nul

REM Start monitoring services
echo 📊 Starting monitoring services...
docker compose -f docker-compose.local.yml up -d prometheus grafana

REM Wait for monitoring to be ready
echo ⏳ Waiting for monitoring services to be ready...
timeout /t 20 /nobreak >nul

REM Start application services
echo 🚀 Starting application services...
docker compose -f docker-compose.local.yml up -d auth catalog booking payment

REM Wait for application services to be ready
echo ⏳ Waiting for application services to be ready...
timeout /t 30 /nobreak >nul

REM Start frontend
echo 🌐 Starting frontend...
docker compose -f docker-compose.local.yml up -d frontend

REM Wait for frontend to be ready
echo ⏳ Waiting for frontend to be ready...
timeout /t 20 /nobreak >nul

REM Start CI/CD tools
echo 🔧 Starting CI/CD tools...
docker compose -f docker-compose.local.yml up -d jenkins sonarqube registry

REM Wait for CI/CD tools to be ready
echo ⏳ Waiting for CI/CD tools to be ready...
timeout /t 30 /nobreak >nul

echo.
echo 🎉 Local Development Environment Started Successfully!
echo.
echo 📱 Application Access Points:
echo    • Frontend: http://localhost:3000
echo    • Auth API: http://localhost:8001/docs
echo    • Catalog API: http://localhost:8002/docs
echo    • Booking API: http://localhost:8003/docs
echo    • Payment API: http://localhost:8004/docs
echo.
echo 🔧 Admin Tools:
echo    • pgAdmin: http://localhost:5050 (admin@admin.com / admin)
echo    • RabbitMQ: http://localhost:15672 (admin / admin)
echo    • Kafka UI: http://localhost:8080
echo.
echo 🚀 CI/CD Tools:
echo    • Jenkins: http://localhost:8081 (admin / admin)
echo    • SonarQube: http://localhost:9000 (admin / admin)
echo    • Docker Registry: http://localhost:5000
echo.
echo 📊 Monitoring:
echo    • Prometheus: http://localhost:9090
echo    • Grafana: http://localhost:3001 (admin / admin)
echo.
echo 📋 Useful Commands:
echo    • View services: docker compose -f docker-compose.local.yml ps
echo    • View logs: docker compose -f docker-compose.local.yml logs [service-name]
echo    • Stop services: docker compose -f docker-compose.local.yml down
echo    • Restart services: docker compose -f docker-compose.local.yml restart
echo.
echo ⚠️  This is a development setup. For production, use docker-compose.prod.yml
echo.
pause
