#!/bin/bash

echo "🔌 Installing Jenkins plugins..."

# Get Jenkins CLI jar
echo "📥 Downloading Jenkins CLI..."
kubectl exec -n jenkins deployment/jenkins -- curl -o /tmp/jenkins-cli.jar http://localhost:8080/jnlpJars/jenkins-cli.jar

# Install required plugins
echo "📦 Installing Pipeline plugin..."
kubectl exec -n jenkins deployment/jenkins -- java -jar /tmp/jenkins-cli.jar -s http://localhost:8080 -auth admin:admin123 install-plugin workflow-aggregator

echo "📦 Installing Git plugin..."
kubectl exec -n jenkins deployment/jenkins -- java -jar /tmp/jenkins-cli.jar -s http://localhost:8080 -auth admin:admin123 install-plugin git

echo "📦 Installing Docker Pipeline plugin..."
kubectl exec -n jenkins deployment/jenkins -- java -jar /tmp/jenkins-cli.jar -s http://localhost:8080 -auth admin:admin123 install-plugin docker-workflow

echo "📦 Installing Kubernetes plugin..."
kubectl exec -n jenkins deployment/jenkins -- java -jar /tmp/jenkins-cli.jar -s http://localhost:8080 -auth admin:admin123 install-plugin kubernetes

echo "🔄 Restarting Jenkins..."
kubectl exec -n jenkins deployment/jenkins -- java -jar /tmp/jenkins-cli.jar -s http://localhost:8080 -auth admin:admin123 restart

echo "✅ Plugin installation completed! Jenkins is restarting..."
echo "⏳ Please wait 2-3 minutes for Jenkins to fully restart, then refresh your browser."
