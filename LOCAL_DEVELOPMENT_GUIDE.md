# 🏠 Local Development Guide - Event Booking Platform

## 📋 Overview
This guide helps you run the complete Event Booking Platform **locally on your Windows machine** without needing any external servers or cloud infrastructure.

## 🚀 **Quick Start (No Server Required!)**

### **Step 1: Start Your Local Environment**
```bash
# Simply double-click this file:
start-local.bat

# Or run from command line:
start-local.bat
```

### **Step 2: Access Your Applications**
- **Frontend**: http://localhost:3000
- **Auth API**: http://localhost:8001/docs
- **Catalog API**: http://localhost:8002/docs
- **Booking API**: http://localhost:8003/docs
- **Payment API**: http://localhost:8004/docs

### **Step 3: Stop When Done**
```bash
# Double-click this file:
stop-local.bat

# Or run from command line:
stop-local.bat
```

---

## 🛠️ **What's Running Locally**

### **✅ Core Services**
- **Frontend**: React application on port 3000
- **Auth Service**: User authentication on port 8001
- **Catalog Service**: Event management on port 8002
- **Booking Service**: Booking system on port 8003
- **Payment Service**: Payment processing on port 8004

### **✅ Infrastructure**
- **PostgreSQL**: Database on port 5432
- **Redis**: Caching on port 6379
- **RabbitMQ**: Message queue on port 5672
- **Kafka**: Event streaming on port 9092

### **✅ Admin Tools**
- **pgAdmin**: Database admin on port 5050
- **RabbitMQ Management**: Queue admin on port 15672
- **Kafka UI**: Topic management on port 8080

### **✅ Monitoring**
- **Prometheus**: Metrics collection on port 9090
- **Grafana**: Dashboards on port 3001

---

## 🔧 **Local Development Workflow**

### **1. Start Development Environment**
```bash
# Start everything
start-local.bat

# Check status
docker compose -f docker-compose.local.yml ps
```

### **2. Make Code Changes**
- Edit files in your favorite editor
- Services will auto-reload (if using development mode)
- Check logs for any errors

### **3. Test Your Changes**
- Frontend: http://localhost:3000
- API docs: http://localhost:8001/docs
- Database: http://localhost:5050

### **4. Stop When Done**
```bash
stop-local.bat
```

---

## 📁 **File Structure for Local Development**

```
event-booking-platform/
├── docker-compose.local.yml     # Local development setup
├── env.local                    # Local environment variables
├── start-local.bat             # Start script for Windows
├── stop-local.bat              # Stop script for Windows
├── services/                    # Backend services
│   ├── auth/                   # Authentication service
│   ├── catalog/                # Event catalog service
│   ├── booking/                # Booking service
│   └── payment/                # Payment service
├── frontend/                    # React frontend
├── monitoring/                  # Monitoring configuration
└── nginx/                       # Nginx configuration (for future use)
```

---

## 🎯 **Local Development Benefits**

### **✅ No External Dependencies**
- Everything runs on your local machine
- No internet connection required after initial setup
- No server costs or configuration

### **✅ Fast Development**
- Instant feedback on code changes
- No deployment delays
- Easy debugging and testing

### **✅ Full Control**
- Modify any service locally
- Test different configurations
- Experiment with new features

### **✅ Production-Like Environment**
- Same Docker containers as production
- Same database and message queues
- Same monitoring tools

---

## 🔍 **Troubleshooting Local Issues**

### **Port Conflicts**
```bash
# Check what's using a port
netstat -ano | findstr :3000

# Kill conflicting process
taskkill /PID <PID> /F
```

### **Docker Issues**
```bash
# Check Docker status
docker info

# Restart Docker Desktop if needed
# Check available memory (need at least 4GB)
```

### **Service Startup Issues**
```bash
# Check service logs
docker compose -f docker-compose.local.yml logs auth

# Restart specific service
docker compose -f docker-compose.local.yml restart auth
```

### **Database Issues**
```bash
# Reset database
docker compose -f docker-compose.local.yml down -v
docker compose -f docker-compose.local.yml up -d postgres
```

---

## 🚀 **Next Steps When You Get a Server**

### **1. Cloud Options (Free Tiers Available)**
- **AWS**: Free tier for 12 months
- **Azure**: Free tier for 12 months
- **Google Cloud**: Free tier with credits
- **DigitalOcean**: $5/month droplets
- **Heroku**: Free tier available

### **2. Migration Path**
```bash
# 1. Test locally (current setup)
start-local.bat

# 2. Deploy to staging server
docker compose -f docker-compose.prod.yml up -d

# 3. Deploy to production server
# (Same as staging but with production config)
```

### **3. What Changes When You Get a Server**
- Update domain names in configuration
- Add SSL certificates
- Configure external databases
- Set up CI/CD pipelines
- Add monitoring and alerting

---

## 📚 **Learning Resources**

### **Docker & Docker Compose**
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows/)
- [Docker Compose Tutorial](https://docs.docker.com/compose/)

### **Event Booking Platform**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)

### **Kafka & Event Streaming**
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka UI Guide](https://github.com/provectus/kafka-ui)

---

## 🎉 **You're Ready to Develop!**

**Your Event Booking Platform is now running completely locally with:**

✅ **No server required**  
✅ **No internet dependency**  
✅ **Full development environment**  
✅ **Production-like setup**  
✅ **Easy start/stop scripts**  
✅ **Complete monitoring stack**  

**🚀 Start building amazing features for your event booking platform!**

---

## 📞 **Need Help?**

If you encounter any issues:

1. **Check the logs**: `docker compose -f docker-compose.local.yml logs [service-name]`
2. **Restart services**: `docker compose -f docker-compose.local.yml restart`
3. **Reset everything**: `stop-local.bat` then `start-local.bat`
4. **Check Docker Desktop**: Ensure it's running and has enough resources

**Happy coding! 🎯**
