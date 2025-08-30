@echo off
echo 🚀 Starting Event Booking Platform - Local Development Environment
echo ================================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo.
    echo 💡 To start Docker Desktop:
    echo    1. Open Docker Desktop application
    echo    2. Wait for it to fully start (green status)
    echo    3. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Check Docker resources
echo 🔍 Checking Docker resources...
docker system df
echo.

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "nginx\logs" mkdir "nginx\logs"
if not exist "nginx\ssl" mkdir "nginx\ssl"
if not exist "monitoring\grafana\provisioning" mkdir "monitoring\grafana\provisioning"
if not exist "monitoring\grafana\dashboards" mkdir "monitoring\grafana\dashboards"
if not exist "backups" mkdir "backups"
if not exist "jenkins" mkdir "jenkins"

echo ✅ Directories created
echo.

REM Check if custom Jenkins Dockerfile exists
if not exist "jenkins\Dockerfile" (
    echo ❌ Custom Jenkins Dockerfile not found!
    echo Please ensure jenkins\Dockerfile exists before running this script.
    pause
    exit /b 1
)

echo ✅ Custom Jenkins Dockerfile found
echo.

REM Start infrastructure services first
echo 🔧 Starting infrastructure services...
echo Starting: PostgreSQL, Redis, RabbitMQ, Zookeeper, Kafka...
docker compose -f docker-compose.local.yml up -d postgres redis rabbitmq zookeeper kafka

REM Check if infrastructure services started successfully
docker compose -f docker-compose.local.yml ps postgres redis rabbitmq zookeeper kafka | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo ❌ Some infrastructure services failed to start. Check logs:
    docker compose -f docker-compose.local.yml logs postgres redis rabbitmq zookeeper kafka
    pause
    exit /b 1
)

REM Wait for infrastructure to be ready
echo ⏳ Waiting for infrastructure services to be ready...
timeout /t 30 /nobreak >nul

REM Start monitoring services
echo 📊 Starting monitoring services...
echo Starting: Prometheus, Grafana...
docker compose -f docker-compose.local.yml up -d prometheus grafana

REM Wait for monitoring to be ready
echo ⏳ Waiting for monitoring services to be ready...
timeout /t 20 /nobreak >nul

REM Start application services
echo 🚀 Starting application services...
echo Starting: Auth, Catalog, Booking, Payment services...
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

REM Start CI/CD tools with custom Jenkins build
echo 🔧 Starting CI/CD tools...
echo Building and starting: Jenkins (with Docker CLI), SonarQube, Docker Registry...

REM Build and start Jenkins with custom Dockerfile
echo 🔨 Building custom Jenkins image with Docker CLI...
docker compose -f docker-compose.local.yml up -d --build jenkins

REM Start other CI/CD tools
docker compose -f docker-compose.local.yml up -d sonarqube registry

REM Wait for CI/CD tools to be ready
echo ⏳ Waiting for CI/CD tools to be ready...
timeout /t 45 /nobreak >nul

REM Verify all services are running
echo 🔍 Verifying all services are running...
docker compose -f docker-compose.local.yml ps

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
echo    • Jenkins: http://localhost:8081 (admin / admin) - WITH DOCKER CLI
echo    • SonarQube: http://localhost:9000 (admin / admin)
echo    • Docker Registry: http://localhost:5000
echo.
echo 📊 Monitoring:
echo    • Prometheus: http://localhost:9090
echo    • Grafana: http://localhost:3001 (admin / admin)
echo.
echo 🐳 Docker Information:
echo    • Jenkins now has Docker CLI installed
echo    • Can build and push Docker images
echo    • Access to host Docker daemon
echo.
echo 📋 Useful Commands:
echo    • View services: docker compose -f docker-compose.local.yml ps
echo    • View logs: docker compose -f docker-compose.local.yml logs [service-name]
echo    • Stop services: docker compose -f docker-compose.local.yml down
echo    • Restart services: docker compose -f docker-compose.local.yml restart
echo    • Test Jenkins Docker: docker compose -f docker-compose.local.yml exec jenkins docker version
echo.
echo 🔧 Jenkins Pipeline Setup:
echo    1. Open Jenkins: http://localhost:8081
echo    2. Create new Pipeline job
echo    3. Use "Pipeline script" (not SCM) for local development
echo    4. Copy Jenkinsfile content from jenkins\Jenkinsfile.local
echo.
echo ⚠️  This is a development setup. For production, use docker-compose.prod.yml
echo.
echo 🎯 Next Steps:
echo    1. Test Jenkins Docker access
echo    2. Create and run your first pipeline
echo    3. Build and deploy your services
echo.
pause
