# 🚀 Local Deployment Guide - Event Booking Platform

## 📋 Overview
This guide will help you deploy and test the complete Event Booking Platform locally using Docker and Docker Compose.

## 🏗️ System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Auth Service  │    │ Catalog Service │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 8002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   PostgreSQL    │    │     Redis       │
         │              │   Port: 5432    │    │   Port: 6379    │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Payment Service│    │ Booking Service │    │  Worker Service │
│   (FastAPI)     │    │   (FastAPI)     │    │   (Background)  │
│   Port: 8004    │    │   Port: 8003    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
         └───────────────────────┼───────────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │    RabbitMQ     │
                        │  Port: 15672    │
                        └─────────────────┘
```

## 🛠️ Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **Git** for cloning the repository
- **Web Browser** for testing

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 5GB free space
- **CPU**: 2+ cores recommended

## 🚀 Quick Start Deployment

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/KavindaSandamal/event-booking-platform.git
cd event-booking-platform

# Copy environment file
cp env.example .env
```

### Step 2: Start All Services
```bash
# Start all services with Docker Compose
docker compose up -d

# Check service status
docker compose ps
```

### Step 3: Verify Deployment
```bash
# Wait for services to start (2-3 minutes)
# Then test the endpoints
```

## 🔧 Detailed Deployment Steps

### 1. Infrastructure Services First
```bash
# Start only infrastructure services
docker compose up -d postgres redis rabbitmq pgadmin

# Verify they're running
docker compose ps postgres redis rabbitmq pgadmin
```

### 2. Backend Services
```bash
# Start backend services
docker compose up -d auth catalog booking payment worker

# Check logs for any errors
docker compose logs auth
docker compose logs catalog
```

### 3. Frontend Service
```bash
# Start frontend
docker compose up -d frontend

# Check frontend logs
docker compose logs frontend
```

## 🧪 Testing the Complete System

### Service Health Checks

#### 1. Frontend Application
```bash
# Test frontend
curl http://localhost:3000
# Expected: HTML response with React app
```

#### 2. Backend API Services
```bash
# Auth Service
curl http://localhost:8001/docs
# Expected: Swagger UI documentation

# Catalog Service  
curl http://localhost:8002/docs
# Expected: Swagger UI documentation

# Booking Service
curl http://localhost:8003/docs
# Expected: Swagger UI documentation

# Payment Service
curl http://localhost:8004/docs
# Expected: Swagger UI documentation
```

#### 3. Database Services
```bash
# PostgreSQL
docker exec -it event-booking-platform-postgres-1 psql -U postgres -d eventdb -c "\dt"

# Redis
docker exec -it event-booking-platform-redis-1 redis-cli ping
# Expected: PONG

# RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview
# Expected: JSON response with queue info
```

#### 4. Admin Interfaces
```bash
# pgAdmin
# Open: http://localhost:5050
# Login: admin@admin.com / admin

# RabbitMQ Management
# Open: http://localhost:15672
# Login: guest / guest
```

### Complete System Test

#### Test User Registration Flow
1. **Open Frontend**: http://localhost:3000
2. **Register User**: Use the registration form
3. **Verify in Database**: Check user table in pgAdmin
4. **Test Login**: Use registered credentials

#### Test Event Booking Flow
1. **Browse Events**: Navigate to events catalog
2. **Select Event**: Choose an event to book
3. **Book Event**: Complete booking process
4. **Verify Booking**: Check booking in database

## 📊 Monitoring and Logs

### View Service Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs auth
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f auth
```

### Service Status Monitoring
```bash
# Check all service statuses
docker compose ps

# Check resource usage
docker stats

# Check service health
docker compose exec auth curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Port Conflicts
```bash
# Check what's using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8001

# Kill conflicting processes
taskkill /PID <PID> /F
```

#### 2. Service Startup Failures
```bash
# Check service logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>

# Rebuild and restart
docker compose up -d --build <service-name>
```

#### 3. Database Connection Issues
```bash
# Check PostgreSQL status
docker compose exec postgres pg_isready -U postgres

# Restart PostgreSQL
docker compose restart postgres

# Check network connectivity
docker compose exec auth ping postgres
```

#### 4. Memory Issues
```bash
# Check Docker memory usage
docker stats

# Increase Docker memory limit in Docker Desktop
# Settings > Resources > Memory: 8GB+
```

### Reset Everything
```bash
# Stop all services
docker compose down

# Remove all containers and volumes
docker compose down -v

# Remove all images
docker compose down --rmi all

# Start fresh
docker compose up -d
```

## 🔄 Development Workflow

### Local Development Mode
```bash
# Start only infrastructure
docker compose up -d postgres redis rabbitmq

# Run services locally for development
cd services/auth
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

cd services/catalog
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# Frontend development
cd frontend
npm install
npm run dev
```

### Hot Reload
- Backend services automatically reload on code changes
- Frontend uses Vite for fast hot reload
- Database changes persist between restarts

## 📱 Access Points

### Web Interfaces
- **Frontend App**: http://localhost:3000
- **Auth API Docs**: http://localhost:8001/docs
- **Catalog API Docs**: http://localhost:8002/docs
- **Booking API Docs**: http://localhost:8003/docs
- **Payment API Docs**: http://localhost:8004/docs
- **pgAdmin**: http://localhost:5050
- **RabbitMQ Management**: http://localhost:15672

### Database Connections
- **PostgreSQL**: localhost:5432
  - Database: eventdb
  - Username: postgres
  - Password: postgres
- **Redis**: localhost:6379
- **RabbitMQ**: localhost:5672

## 🚀 Next Steps

### 1. Explore the Application
- Test user registration and login
- Browse events and create bookings
- Test payment processing

### 2. Understand the Code
- Review service implementations
- Study API endpoints
- Examine database schemas

### 3. Make Changes
- Modify service logic
- Add new features
- Update frontend components

### 4. Prepare for Production
- Set up production environment variables
- Configure SSL certificates
- Set up monitoring and logging

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Project Files
- `docker-compose.yml` - Service orchestration
- `.env` - Environment configuration
- `README.md` - Project overview
- `FEATURE_BRANCH_WORKFLOW.md` - Git workflow guide

---

## ✅ **Deployment Checklist**

- [ ] Docker Desktop running
- [ ] All services started successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] All API docs accessible
- [ ] Database connections working
- [ ] User registration working
- [ ] Event browsing working
- [ ] Booking system functional
- [ ] Payment processing working
- [ ] Logs showing no errors

**🎉 Congratulations! Your Event Booking Platform is now running locally!**
