#!/bin/bash

# Jenkins CI/CD Setup Script for Event Booking Platform
echo "🚀 Setting up Jenkins CI/CD for Event Booking Platform..."

# Wait for Jenkins to be ready
echo "⏳ Waiting for Jenkins to be ready..."
kubectl wait --for=condition=ready pod -l app=jenkins -n jenkins --timeout=300s

# Get Jenkins admin password
echo "🔑 Getting Jenkins admin password..."
JENKINS_PASSWORD=$(kubectl exec -n jenkins deployment/jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "admin123")

echo "📋 Jenkins Setup Information:"
echo "   URL: http://localhost:8080"
echo "   Username: admin"
echo "   Password: $JENKINS_PASSWORD"
echo ""

# Install required plugins
echo "🔌 Installing required Jenkins plugins..."
kubectl exec -n jenkins deployment/jenkins -- curl -X POST -u admin:$JENKINS_PASSWORD \
  -d '<install plugin="workflow-aggregator@latest" />' \
  -H 'Content-Type: text/xml' \
  http://localhost:8080/pluginManager/installNecessaryPlugins

kubectl exec -n jenkins deployment/jenkins -- curl -X POST -u admin:$JENKINS_PASSWORD \
  -d '<install plugin="kubernetes@latest" />' \
  -H 'Content-Type: text/xml' \
  http://localhost:8080/pluginManager/installNecessaryPlugins

kubectl exec -n jenkins deployment/jenkins -- curl -X POST -u admin:$JENKINS_PASSWORD \
  -d '<install plugin="docker-workflow@latest" />' \
  -H 'Content-Type: text/xml' \
  http://localhost:8080/pluginManager/installNecessaryPlugins

# Wait for plugins to install
echo "⏳ Waiting for plugins to install..."
sleep 30

# Create the CI/CD job
echo "📝 Creating CI/CD job..."
kubectl exec -n jenkins deployment/jenkins -- curl -X POST -u admin:$JENKINS_PASSWORD \
  -H 'Content-Type: application/xml' \
  -d @/var/jenkins_home/job-config.xml \
  http://localhost:8080/createItem?name=event-booking-cicd

echo "✅ Jenkins CI/CD setup completed!"
echo ""
echo "🌐 Access Jenkins at: http://localhost:8080"
echo "👤 Login with: admin / $JENKINS_PASSWORD"
echo "🔧 Job created: event-booking-cicd"
echo ""
echo "📚 Next steps:"
echo "   1. Access Jenkins web interface"
echo "   2. Configure Git repository URL in the job"
echo "   3. Set up webhook for automatic builds"
echo "   4. Test the pipeline with a code change"
