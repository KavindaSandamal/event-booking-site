# Jenkins CI/CD Setup for Event Booking Platform

This document provides a complete guide for setting up Jenkins CI/CD pipeline for the event-booking platform.

## 🏗️ Architecture Overview

```
GitHub Repository
       ↓ (Webhook)
   Jenkins (Minikube)
       ↓ (Build & Test)
   Docker Images
       ↓ (Deploy)
   Minikube Cluster
       ↓ (Access)
   event-booking.local
```

## 📋 Prerequisites

- Minikube cluster running
- Docker installed
- kubectl configured
- Git repository (GitHub/GitLab)

## 🚀 Quick Setup

### 1. Deploy Jenkins

```bash
# Deploy Jenkins to Minikube
kubectl apply -f k8s/jenkins/jenkins-deployment.yaml

# Wait for Jenkins to be ready
kubectl wait --for=condition=ready pod -l app=jenkins -n jenkins --timeout=300s
```

### 2. Access Jenkins

```bash
# Port forward to access Jenkins
kubectl port-forward -n jenkins service/jenkins 8080:8080

# Access Jenkins at: http://localhost:8080
# Username: admin
# Password: Get from pod logs or use 'admin123'
```

### 3. Get Admin Password

```bash
# Get Jenkins admin password
kubectl exec -n jenkins deployment/jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
```

## 🔧 Configuration

### 1. Install Required Plugins

Navigate to: **Manage Jenkins** → **Manage Plugins** → **Available**

Install these plugins:
- **Pipeline** (workflow-aggregator)
- **Kubernetes**
- **Docker Pipeline**
- **Git**
- **GitHub Integration**

### 2. Configure Kubernetes Integration

1. Go to **Manage Jenkins** → **Manage Nodes and Clouds**
2. Click **Configure Clouds**
3. Add **Kubernetes Cloud**
4. Configure:
   - **Name**: `minikube`
   - **Kubernetes URL**: `https://kubernetes.default.svc.cluster.local`
   - **Credentials**: Use service account token

### 3. Create CI/CD Job

1. Click **New Item**
2. Enter name: `event-booking-cicd`
3. Select **Pipeline**
4. Configure:
   - **Pipeline script from SCM**
   - **SCM**: Git
   - **Repository URL**: Your Git repository
   - **Script Path**: `Jenkinsfile`

## 📝 Pipeline Stages

The Jenkinsfile includes these stages:

### 1. **Checkout**
- Clone repository
- Set build tags

### 2. **Build Images** (Parallel)
- Build all service images
- Tag with build number

### 3. **Run Tests** (Parallel)
- Backend service tests
- Frontend tests

### 4. **Deploy to Minikube**
- Update Kubernetes deployments
- Wait for rollouts

### 5. **Health Check**
- Verify service health
- Test endpoints

## 🔄 Automated Triggers

### SCM Polling
- Polls repository every 5 minutes
- Triggers build on changes

### Webhook (Recommended)
1. In your Git repository, add webhook:
   - **URL**: `http://your-jenkins-url/github-webhook/`
   - **Events**: Push, Pull Request

2. Configure Jenkins:
   - Install **GitHub Plugin**
   - Enable **GitHub hook trigger**

## 🐳 Docker Integration

Jenkins has access to Docker daemon through:
- Host path mount: `/var/run/docker.sock`
- Builds images in Minikube's Docker environment

## ☸️ Kubernetes Integration

Jenkins can deploy to Minikube through:
- kubectl configuration mounted from host
- Service account with deployment permissions

## 📊 Monitoring & Logs

### View Build Logs
1. Go to job dashboard
2. Click on build number
3. View **Console Output**

### Monitor Deployments
```bash
# Watch deployment status
kubectl get pods -n event-booking -w

# Check service health
curl http://event-booking.local/health
```

## 🔧 Troubleshooting

### Common Issues

1. **Jenkins Pod Not Starting**
   ```bash
   kubectl describe pod -n jenkins -l app=jenkins
   kubectl logs -n jenkins -l app=jenkins
   ```

2. **Docker Build Failures**
   - Check Docker daemon access
   - Verify image names and tags

3. **Kubernetes Deployment Failures**
   - Check kubectl configuration
   - Verify service account permissions

4. **Service Health Check Failures**
   - Wait for services to be ready
   - Check ingress configuration

### Useful Commands

```bash
# Restart Jenkins
kubectl rollout restart deployment/jenkins -n jenkins

# Check Jenkins logs
kubectl logs -n jenkins -l app=jenkins -f

# Access Jenkins shell
kubectl exec -n jenkins deployment/jenkins -- /bin/bash

# Check build status
kubectl get pods -n event-booking
```

## 🎯 Best Practices

1. **Security**
   - Use service accounts with minimal permissions
   - Store secrets in Kubernetes secrets
   - Enable HTTPS for Jenkins

2. **Performance**
   - Use parallel stages for builds
   - Implement proper caching
   - Clean up old images

3. **Monitoring**
   - Set up build notifications
   - Monitor resource usage
   - Track deployment metrics

## 📚 Additional Resources

- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Kubernetes Jenkins Plugin](https://plugins.jenkins.io/kubernetes/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)

## 🆘 Support

For issues or questions:
1. Check Jenkins build logs
2. Review Kubernetes pod logs
3. Verify service configurations
4. Test individual components
