# 🚀 Local CI/CD Setup Guide - Event Booking Platform

## 📋 Overview
This guide helps you set up and test **CI/CD (Continuous Integration/Continuous Deployment)** **locally on your Windows machine** without needing external servers.

## 🎯 **What You'll Have Locally**

### **✅ Complete CI/CD Pipeline**
- **Jenkins**: Pipeline orchestration and automation
- **SonarQube**: Code quality analysis and security scanning
- **Docker Registry**: Local image storage
- **Kafka**: Event streaming for CI/CD events
- **Monitoring**: Full observability of your pipeline

---

## 🚀 **Quick Start - Local CI/CD**

### **Step 1: Start Your Local CI/CD Environment**
```bash
# Start everything including CI/CD tools
start-local.bat
```

### **Step 2: Access CI/CD Tools**
- **Jenkins**: http://localhost:8081 (admin / admin)
- **SonarQube**: http://localhost:9000 (admin / admin)
- **Docker Registry**: http://localhost:5000

### **Step 3: Test Your Pipeline**
- Create a Jenkins job using `jenkins/Jenkinsfile.local`
- Run the pipeline to build and deploy locally

---

## 🔧 **Setting Up Jenkins Locally**

### **1. Initial Jenkins Setup**
1. Open http://localhost:8081
2. Get initial admin password:
   ```bash
   docker compose -f docker-compose.local.yml logs jenkins
   ```
3. Install suggested plugins
4. Create admin user: `admin` / `admin`

### **2. Configure Jenkins for Local Development**
1. **Install Required Plugins**:
   - Docker Pipeline
   - Git Integration
   - Pipeline
   - SonarQube Scanner

2. **Configure Docker**:
   - Jenkins can access Docker daemon (already configured)
   - Use local registry: `localhost:5000`

3. **Configure SonarQube**:
   - URL: `http://sonarqube:9000`
   - Token: `local_sonar_token`

---

## 📊 **Setting Up SonarQube Locally**

### **1. Initial SonarQube Setup**
1. Open http://localhost:9000
2. Login: `admin` / `admin`
3. Create a new project for your event booking platform

### **2. Configure SonarQube**
1. **Quality Gates**: Set up basic quality rules
2. **Security Rules**: Enable security scanning
3. **Code Coverage**: Configure test coverage reporting

---

## 🐳 **Setting Up Docker Registry Locally**

### **1. Access Local Registry**
- **URL**: http://localhost:5000
- **No authentication required** (local development)

### **2. Test Registry**
```bash
# Test pushing an image
docker pull hello-world
docker tag hello-world localhost:5000/hello-world:latest
docker push localhost:5000/hello-world:latest

# List images in registry
curl http://localhost:5000/v2/_catalog
```

---

## 🔄 **Your Local CI/CD Pipeline**

### **Pipeline Stages**
1. **Checkout**: Get latest code from Git
2. **Code Quality**: Run SonarQube analysis
3. **Unit Tests**: Execute test suites
4. **Build Images**: Create Docker containers
5. **Push to Registry**: Store in local registry
6. **Deploy Locally**: Update running services

### **Pipeline Benefits**
- **Instant Feedback**: See results immediately
- **Local Testing**: Test deployment locally
- **No External Dependencies**: Everything runs on your machine
- **Production-Like**: Same process as production

---

## 🧪 **Testing Your CI/CD Pipeline**

### **1. Create a Jenkins Job**
1. Open Jenkins: http://localhost:8081
2. Click "New Item"
3. Choose "Pipeline"
4. Name: `event-booking-platform-local`
5. Pipeline: From SCM (Git)
6. Repository: Your local Git repo
7. Script Path: `jenkins/Jenkinsfile.local`

### **2. Run the Pipeline**
1. Click "Build Now"
2. Watch the pipeline execute
3. Check each stage for success/failure
4. View logs for detailed information

### **3. Monitor Results**
- **Jenkins**: Pipeline execution status
- **SonarQube**: Code quality metrics
- **Docker Registry**: Built images
- **Grafana**: Pipeline performance metrics

---

## 📈 **Monitoring Your CI/CD Pipeline**

### **1. Jenkins Dashboard**
- Build history and trends
- Pipeline execution times
- Success/failure rates
- Build logs and artifacts

### **2. SonarQube Dashboard**
- Code quality metrics
- Security vulnerabilities
- Code coverage reports
- Technical debt analysis

### **3. Grafana Dashboards**
- Pipeline performance metrics
- Build duration trends
- Resource usage during builds
- Deployment success rates

---

## 🔍 **Troubleshooting Local CI/CD**

### **Common Issues**

#### **Jenkins Won't Start**
```bash
# Check logs
docker compose -f docker-compose.local.yml logs jenkins

# Check if port 8081 is available
netstat -ano | findstr :8081
```

#### **SonarQube Memory Issues**
```bash
# Increase Docker memory for SonarQube
# In Docker Desktop: Settings > Resources > Memory: 4GB+
```

#### **Docker Registry Access**
```bash
# Test registry connectivity
curl http://localhost:5000/v2/_catalog

# Check if registry is running
docker compose -f docker-compose.local.yml ps registry
```

#### **Pipeline Failures**
```bash
# Check Jenkins logs
docker compose -f docker-compose.local.yml logs jenkins

# Check specific build logs in Jenkins UI
```

---

## 🚀 **Advanced Local CI/CD Features**

### **1. Multi-Branch Pipelines**
- Automatically create pipelines for each Git branch
- Test feature branches automatically
- Merge only after pipeline success

### **2. Automated Testing**
- Run unit tests on every commit
- Integration tests before deployment
- Performance tests for critical paths

### **3. Blue-Green Deployment**
- Deploy new version alongside old
- Switch traffic when ready
- Rollback capability

### **4. Infrastructure as Code**
- Use Docker Compose for deployments
- Version control your infrastructure
- Reproducible environments

---

## 📚 **Learning Resources**

### **Jenkins**
- [Jenkins Pipeline Tutorial](https://www.jenkins.io/doc/pipeline/tour/hello-world/)
- [Jenkins Docker Guide](https://www.jenkins.io/doc/book/installing/docker/)

### **SonarQube**
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Quality Gates Setup](https://docs.sonarqube.org/latest/user-guide/quality-gates/)

### **Docker Registry**
- [Docker Registry Documentation](https://docs.docker.com/registry/)
- [Local Registry Setup](https://docs.docker.com/registry/deploying/)

---

## 🎉 **You're Ready for Local CI/CD!**

**Your Event Booking Platform now has:**

✅ **Complete CI/CD pipeline locally**  
✅ **Jenkins automation**  
✅ **SonarQube code quality**  
✅ **Docker registry**  
✅ **Event streaming with Kafka**  
✅ **Full monitoring stack**  

**🚀 Start automating your development workflow!**

---

## 🔄 **Next Steps**

### **1. Test Your Pipeline**
- Run the Jenkins job
- Check SonarQube reports
- Verify Docker images in registry

### **2. Customize Your Pipeline**
- Add more test stages
- Configure quality gates
- Set up notifications

### **3. Scale Up Later**
- When you get a server, use `docker-compose.prod.yml`
- Same tools, same process, different environment

**Happy automating! 🎯**
