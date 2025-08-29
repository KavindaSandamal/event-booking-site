@echo off
echo 🧪 Testing Your Local CI/CD Setup
echo =================================
echo.

echo 🔍 Checking service status...
docker compose -f docker-compose.local.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 📊 CI/CD Services Status:
echo.

REM Test Docker Registry
echo 🐳 Testing Docker Registry...
curl -s http://localhost:5000/v2/_catalog >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Registry: http://localhost:5000 - WORKING
) else (
    echo ❌ Docker Registry: http://localhost:5000 - NOT READY
)

REM Test Jenkins
echo 🔧 Testing Jenkins...
curl -s http://localhost:8081 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Jenkins: http://localhost:8081 - WORKING
    echo    Initial Password: 0e5b7747240b45c8b54780378ddee68a
) else (
    echo ❌ Jenkins: http://localhost:8081 - NOT READY
)

REM Test SonarQube
echo 📊 Testing SonarQube...
curl -s http://localhost:9000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SonarQube: http://localhost:9000 - WORKING
) else (
    echo ❌ SonarQube: http://localhost:9000 - NOT READY
)

echo.
echo 🚀 CI/CD Access Information:
echo =============================
echo.
echo 🐳 Docker Registry: http://localhost:5000
echo    - No authentication required
echo    - Test with: curl http://localhost:5000/v2/_catalog
echo.
echo 🔧 Jenkins: http://localhost:8081
echo    - Initial setup required
echo    - Initial password: 0e5b7747240b45c8b54780378ddee68a
echo    - Create admin user: admin / admin
echo.
echo 📊 SonarQube: http://localhost:9000
echo    - Initial setup required
echo    - Default: admin / admin
echo.
echo 🧪 Test Pipeline: jenkins/test-pipeline.groovy
echo    - Simple pipeline to test Jenkins
echo    - Copy content into Jenkins job
echo.
echo 📋 Next Steps:
echo    1. Open Jenkins: http://localhost:8081
echo    2. Use password: 0e5b7747240b45c8b54780378ddee68a
echo    3. Install suggested plugins
echo    4. Create admin user: admin / admin
echo    5. Create new pipeline job
echo    6. Use test-pipeline.groovy content
echo.
pause
