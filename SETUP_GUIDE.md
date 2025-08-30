# 🚀 Event Booking Platform - Setup Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

### **Required Software:**
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **PowerShell** (Windows) or **Terminal** (Mac/Linux)

### **System Requirements:**
- **RAM:** Minimum 8GB, Recommended 16GB
- **Storage:** At least 10GB free space
- **OS:** Windows 10/11, macOS 10.15+, or Linux

## 🎯 Quick Start (5 Minutes)

### **1. Clone the Repository**
```bash
git clone https://github.com/KavindaSandamal/event-booking-site.git
cd event-booking-site
```

### **2. Start All Services**
```bash
# Windows PowerShell
.\start-local-simple.ps1

# Or manually
docker compose -f docker-compose.local.yml up -d
```

### **3. Access Your Application**
- **Frontend:** http://localhost:3000
- **Auth Service:** http://localhost:8001
- **Catalog Service:** http://localhost:8002
- **Booking Service:** http://localhost:8003
- **Payment Service:** http://localhost:8004
- **Jenkins CI/CD:** http://localhost:8081
- **Docker Registry:** http://localhost:5000

## 🔧 Detailed Setup

### **Step 1: Install Docker Desktop**
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and restart your computer
3. Start Docker Desktop
4. Verify installation: `docker --version`

### **Step 2: Clone the Project**
```bash
git clone https://github.com/KavindaSandamal/event-booking-site.git
cd event-booking-site
```

### **Step 3: Start Infrastructure Services**
```bash
# Start core infrastructure
docker compose -f docker-compose.local.yml up -d postgres redis rabbitmq kafka zookeeper

# Wait for services to be ready (about 30 seconds)
Start-Sleep -Seconds 30
```

### **Step 4: Start Application Services**
```bash
# Start all application services
docker compose -f docker-compose.local.yml up -d auth catalog booking payment frontend worker
```

### **Step 5: Start CI/CD Tools**
```bash
# Start Jenkins and CI/CD tools
docker compose -f docker-compose.local.yml up -d jenkins registry sonarqube prometheus grafana
```

## 🧪 Testing Your Setup

### **Health Check Commands**
```bash
# Check all services are running
docker compose -f docker-compose.local.yml ps

# Check service logs
docker compose -f docker-compose.local.yml logs auth
docker compose -f docker-compose.local.yml logs frontend
```

### **Test API Endpoints**
```bash
# Test auth service
curl http://localhost:8001/health

# Test catalog service
curl http://localhost:8002/health

# Test frontend
curl http://localhost:3000
```

## 🚀 Development Workflow

### **Making Changes**
1. **Edit code** in your preferred editor
2. **Test locally** using the running services
3. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin main
   ```
4. **Watch CI/CD** automatically run in GitHub Actions

### **Local Development**
- **Frontend:** Edit files in `frontend/src/` - changes auto-reload
- **Backend:** Edit files in `services/*/app/` - restart containers to see changes
- **Database:** Connect to PostgreSQL at `localhost:5432`

## 🐛 Troubleshooting

### **Common Issues & Solutions**

#### **Port Already in Use**
```bash
# Stop all services
docker compose -f docker-compose.local.yml down

# Check what's using the port
netstat -ano | findstr :8001

# Start services again
docker compose -f docker-compose.local.yml up -d
```

#### **Docker Desktop Not Running**
- Start Docker Desktop application
- Wait for it to fully load
- Try commands again

#### **Services Not Starting**
```bash
# Check logs for specific service
docker compose -f docker-compose.local.yml logs auth

# Restart specific service
docker compose -f docker-compose.local.yml restart auth
```

#### **Memory Issues**
- Increase Docker Desktop memory limit (Settings → Resources → Memory)
- Recommended: 8GB minimum, 16GB preferred

### **Reset Everything**
```bash
# Stop and remove all containers, networks, and volumes
docker compose -f docker-compose.local.yml down -v

# Remove all images
docker system prune -a

# Start fresh
.\start-local-simple.ps1
```

## 📚 Project Structure

```
event-booking-platform/
├── frontend/                 # React frontend application
├── services/                 # Backend microservices
│   ├── auth/                # Authentication service
│   ├── catalog/             # Event catalog service
│   ├── booking/             # Booking management service
│   ├── payment/             # Payment processing service
│   └── worker/              # Background task worker
├── jenkins/                 # CI/CD configuration
├── docker-compose.local.yml # Local development setup
└── README.md               # Project overview
```

## 🔗 Useful Links

- **GitHub Repository:** https://github.com/KavindaSandamal/event-booking-site
- **Docker Documentation:** https://docs.docker.com/
- **GitHub Actions:** https://github.com/features/actions

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Check GitHub Issues for similar problems
3. Create a new issue with your error details

## 🎉 You're All Set!

Once you complete these steps, you'll have:
- ✅ **Full-stack application** running locally
- ✅ **Microservices architecture** with all services
- ✅ **CI/CD pipeline** with GitHub Actions
- ✅ **Development environment** ready for coding
- ✅ **Professional setup** matching production standards

**Happy coding! 🚀**
