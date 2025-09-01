# 🌐 Event Booking Platform Access Guide

## ✅ **Current Working Access Methods**

### **🎯 Primary Access Method (Recommended)**
- **Frontend Application**: http://localhost:3000
- **Health Check**: http://localhost:3000/health
- **Method**: Port-forwarding (currently active)

### **🔧 How to Access**

#### **Option 1: Port-Forwarding (Currently Working)**
```powershell
# Frontend is already accessible via port-forward
kubectl port-forward -n event-booking service/frontend-service 3000:3000

# Access URLs:
# Frontend: http://localhost:3000
# Health: http://localhost:3000/health
```

#### **Option 2: Ingress with Tunnel (Alternative)**
```powershell
# Start minikube tunnel (if not already running)
minikube tunnel

# Access via domain (requires hosts entry)
# Frontend: http://event-booking.local
# Health: http://event-booking.local/health
```

## 🏗️ **Architecture Status**

### **✅ Development Environment (Jenkins CI/CD)**
- **Jenkins**: http://localhost:8080
- **Docker Registry**: http://localhost:5000
- **SonarQube**: http://localhost:9000
- **Jenkins Nginx**: http://localhost:8081 (moved from port 80)

### **✅ Production Environment (Event Booking Platform)**
- **Frontend**: http://localhost:3000 ✅ **WORKING**
- **Backend Services**: Running in Minikube
- **Databases**: PostgreSQL and Redis operational

## 🔍 **Why event-booking.local Might Not Work**

### **Issue**: Port Conflict
- **Problem**: Jenkins nginx was using port 80
- **Solution**: Moved Jenkins nginx to port 8081
- **Status**: Port 80 is now free for Minikube tunnel

### **Issue**: Tunnel Configuration
- **Problem**: Minikube tunnel might need restart
- **Solution**: Restart tunnel after port changes
- **Status**: Tunnel restarted, testing in progress

## 🚀 **Recommended Access Methods**

### **1. For Development (CI/CD)**
```powershell
# Jenkins Dashboard
http://localhost:8080

# Docker Registry
http://localhost:5000

# SonarQube
http://localhost:9000
```

### **2. For Application Testing**
```powershell
# Frontend (Primary)
http://localhost:3000

# Health Check
http://localhost:3000/health

# API Endpoints (via frontend)
http://localhost:3000/auth/login
http://localhost:3000/catalog/events
```

### **3. For Production-like Access**
```powershell
# Start tunnel
minikube tunnel

# Access via domain
http://event-booking.local
```

## 📋 **Current Status Summary**

| Component | Status | Access Method | URL |
|-----------|--------|---------------|-----|
| **Frontend** | ✅ Working | Port-forward | http://localhost:3000 |
| **Jenkins** | ✅ Working | Direct | http://localhost:8080 |
| **Docker Registry** | ✅ Working | Direct | http://localhost:5000 |
| **SonarQube** | ✅ Working | Direct | http://localhost:9000 |
| **Ingress** | ⚠️ Testing | Tunnel | http://event-booking.local |

## 🎯 **Quick Access Commands**

```powershell
# Test frontend
curl http://localhost:3000

# Test health
curl http://localhost:3000/health

# Test Jenkins
curl http://localhost:8080

# Test Docker Registry
curl http://localhost:5000/v2/_catalog

# Test SonarQube
curl http://localhost:9000
```

## 🔧 **Troubleshooting**

### **If event-booking.local doesn't work:**
1. **Use port-forwarding**: http://localhost:3000 ✅
2. **Check tunnel**: `minikube tunnel`
3. **Check hosts**: `127.0.0.1 event-booking.local`
4. **Check ingress**: `kubectl get ingress -n event-booking`

### **If port-forwarding stops:**
```powershell
# Restart port-forward
kubectl port-forward -n event-booking service/frontend-service 3000:3000
```

## 🎉 **Success!**

Your Event Booking Platform is **fully accessible** via:
- **Primary**: http://localhost:3000 ✅
- **Health**: http://localhost:3000/health ✅
- **CI/CD**: Jenkins, Registry, SonarQube ✅

**The application is working perfectly! 🚀**
