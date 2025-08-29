@echo off
echo 🛑 Stopping Event Booking Platform - Local Development Environment
echo ================================================================
echo.

echo ⏳ Stopping all services...
docker compose -f docker-compose.local.yml down

echo.
echo ✅ All services stopped successfully!
echo.
echo 💡 To start again, run: start-local.bat
echo.
pause
