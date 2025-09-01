# 🚀 Jenkins CI/CD Platform for Event Booking Platform

This directory contains a complete Jenkins CI/CD setup for the Event Booking Platform, including Docker Registry, SonarQube, and automated deployment to Minikube.

## 📋 **Table of Contents**

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Components](#components)
- [Configuration](#configuration)
- [GitHub Integration](#github-integration)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)

## 🎯 **Overview**

This Jenkins setup provides:
- ✅ **Automated CI/CD Pipeline** with multi-stage builds
- ✅ **Docker Registry** for image storage
- ✅ **SonarQube** for code quality analysis
- ✅ **GitHub Webhook Integration** for automatic triggers
- ✅ **Kubernetes Deployment** to Minikube
- ✅ **Health Monitoring** and performance testing
- ✅ **Security Scanning** with Trivy

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Jenkins Server │───▶│  Minikube K8s   │
│                 │    │                 │    │                 │
│  (Source Code)  │    │  (CI/CD Engine) │    │  (Deployment)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Docker Registry│
                       │                 │
                       │  (Image Store)  │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SonarQube     │
                       │                 │
                       │ (Code Quality)  │
                       └─────────────────┘
```

## ⚡ **Quick Start**

### **Prerequisites**
- Docker Desktop running
- Minikube running
- Git repository with your code

### **Step 1: Start Jenkins Platform**
```bash
cd jenkins
chmod +x setup-jenkins.sh
./setup-jenkins.sh
```

### **Step 2: Access Jenkins**
1. Open browser: `http://jenkins.event-booking.local`
2. Get initial password from terminal output
3. Install suggested plugins
4. Create admin user

### **Step 3: Configure GitHub Webhook**
1. Follow the guide in `GITHUB_WEBHOOK_SETUP.md`
2. Set webhook URL: `http://jenkins.event-booking.local/jenkins/github-webhook/`
3. Use ngrok for public access: `ngrok http 80`

### **Step 4: Create Jenkins Job**
1. New Item → Pipeline
2. Name: `event-booking-platform`
3. Pipeline script from SCM
4. Git repository: Your GitHub repo
5. Script path: `jenkins/Jenkinsfile`

## 🧩 **Components**

### **1. Jenkins Server**
- **Port**: 8080
- **URL**: `http://jenkins.event-booking.local`
- **Purpose**: CI/CD orchestration
- **Features**: Pipeline execution, GitHub integration

### **2. Docker Registry**
- **Port**: 5000
- **URL**: `http://registry.event-booking.local`
- **Purpose**: Store Docker images
- **Features**: Image versioning, local storage

### **3. SonarQube**
- **Port**: 9000
- **URL**: `http://sonar.event-booking.local`
- **Purpose**: Code quality analysis
- **Features**: Code coverage, security scanning

### **4. Nginx Reverse Proxy**
- **Port**: 80
- **Purpose**: Route traffic to services
- **Features**: SSL termination, load balancing

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Jenkins
JENKINS_OPTS=--httpPort=8080
JAVA_OPTS=-Djenkins.install.runSetupWizard=false

# Docker Registry
REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY=/var/lib/registry

# SonarQube
SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
```

### **Pipeline Configuration**
The Jenkinsfile includes:
- **Code Quality**: Linting for frontend and backend
- **Security Scan**: Trivy vulnerability scanning
- **Build**: Docker image building for all services
- **Test**: Unit and integration tests
- **Deploy**: Kubernetes deployment to Minikube
- **Health Check**: Application health verification
- **Performance Test**: Load testing with Apache Bench

### **Kubernetes Integration**
- **Namespace**: `event-booking`
- **Services**: All microservices deployed
- **Ingress**: External access configuration
- **Health Checks**: Automated verification

## 🔗 **GitHub Integration**

### **Webhook Setup**
1. **Repository Settings** → **Webhooks**
2. **Payload URL**: `http://jenkins.event-booking.local/jenkins/github-webhook/`
3. **Events**: Push, Pull Request, Issues, Release
4. **Public Access**: Use ngrok or similar tunnel

### **Authentication**
- **GitHub App** or **Personal Access Token**
- **Repository Access**: Full access to your repo
- **Webhook Management**: Jenkins manages webhooks

### **Branch Strategy**
- **Main Branch**: Automatic deployment
- **Feature Branches**: Build and test only
- **Pull Requests**: Automated testing

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Jenkins Not Starting**
```bash
# Check Docker status
docker info

# Check logs
docker-compose logs jenkins

# Restart services
docker-compose restart jenkins
```

#### **2. Webhook Not Working**
```bash
# Check webhook endpoint
curl -X POST http://jenkins.event-booking.local/jenkins/github-webhook/ \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}'

# Check GitHub webhook delivery logs
# Go to GitHub repo → Settings → Webhooks → Click webhook
```

#### **3. Build Failures**
```bash
# Check Minikube status
minikube status

# Check Kubernetes resources
kubectl get pods -n event-booking

# Check Docker registry
curl http://registry.event-booking.local/v2/_catalog
```

#### **4. Network Issues**
```bash
# Check hosts file
cat /etc/hosts | grep event-booking

# Add missing entries
echo "127.0.0.1 jenkins.event-booking.local" | sudo tee -a /etc/hosts
echo "127.0.0.1 registry.event-booking.local" | sudo tee -a /etc/hosts
echo "127.0.0.1 sonar.event-booking.local" | sudo tee -a /etc/hosts
```

### **Debug Commands**
```bash
# View all logs
docker-compose logs -f

# Check service status
docker-compose ps

# Restart all services
docker-compose down && docker-compose up -d

# Clean up volumes
docker-compose down -v
```

## 🚀 **Advanced Features**

### **1. Multi-Branch Pipelines**
```groovy
// In Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            when {
                branch 'main'
            }
            steps {
                echo 'Building for main branch'
            }
        }
    }
}
```

### **2. Parallel Execution**
```groovy
stage('Parallel Tests') {
    parallel {
        stage('Frontend Tests') {
            steps {
                sh 'npm test'
            }
        }
        stage('Backend Tests') {
            steps {
                sh 'python -m pytest'
            }
        }
    }
}
```

### **3. Conditional Deployment**
```groovy
stage('Deploy') {
    when {
        branch 'main'
        environment name: 'DEPLOY_ENV', value: 'production'
    }
    steps {
        sh 'kubectl apply -f k8s/production/'
    }
}
```

### **4. Notifications**
```groovy
post {
    success {
        emailext (
            subject: "Build Successful: ${env.JOB_NAME}",
            body: "Build ${env.BUILD_NUMBER} completed successfully",
            to: 'team@company.com'
        )
    }
    failure {
        slackSend(
            channel: '#jenkins',
            message: "Build ${env.BUILD_NUMBER} failed!"
        )
    }
}
```

## 📊 **Monitoring & Metrics**

### **Jenkins Metrics**
- Build success/failure rates
- Build duration trends
- Queue length monitoring
- Resource utilization

### **Application Metrics**
- Response time monitoring
- Error rate tracking
- Resource usage (CPU, Memory)
- Database performance

### **Infrastructure Metrics**
- Kubernetes pod status
- Docker registry usage
- SonarQube quality gates
- Network connectivity

## 🔒 **Security Considerations**

### **Access Control**
- Jenkins user management
- GitHub authentication
- Kubernetes RBAC
- Docker registry access

### **Secrets Management**
- GitHub tokens
- Docker registry credentials
- Kubernetes secrets
- Database passwords

### **Network Security**
- HTTPS/TLS encryption
- Firewall rules
- VPN access
- Webhook validation

## 📚 **Additional Resources**

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events)
- [Docker Registry](https://docs.docker.com/registry/)
- [SonarQube](https://docs.sonarqube.org/)
- [Kubernetes](https://kubernetes.io/docs/)

## 🤝 **Support**

For issues and questions:
1. Check the troubleshooting section
2. Review Jenkins and component logs
3. Verify configuration settings
4. Test individual components

---

**Happy CI/CD! 🎉**
