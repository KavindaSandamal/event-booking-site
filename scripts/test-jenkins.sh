#!/bin/bash

echo "🧪 Testing Jenkins CI/CD Setup..."

# Test Jenkins accessibility
echo "1. Testing Jenkins accessibility..."
if curl -s http://localhost:8080 > /dev/null; then
    echo "   ✅ Jenkins is accessible at http://localhost:8080"
else
    echo "   ❌ Jenkins is not accessible. Make sure port forwarding is active:"
    echo "      kubectl port-forward -n jenkins service/jenkins 8080:8080"
fi

# Test Jenkins API
echo "2. Testing Jenkins API..."
if curl -s http://localhost:8080/api/json > /dev/null; then
    echo "   ✅ Jenkins API is responding"
else
    echo "   ❌ Jenkins API is not responding"
fi

# Test Kubernetes connectivity from Jenkins
echo "3. Testing Kubernetes connectivity..."
if kubectl exec -n jenkins deployment/jenkins -- kubectl get nodes > /dev/null 2>&1; then
    echo "   ✅ Jenkins can access Kubernetes cluster"
else
    echo "   ❌ Jenkins cannot access Kubernetes cluster"
fi

# Test Docker access from Jenkins
echo "4. Testing Docker access..."
if kubectl exec -n jenkins deployment/jenkins -- docker ps > /dev/null 2>&1; then
    echo "   ✅ Jenkins can access Docker daemon"
else
    echo "   ❌ Jenkins cannot access Docker daemon"
fi

echo ""
echo "📋 Next Steps:"
echo "   1. Access Jenkins at: http://localhost:8080"
echo "   2. Login with: admin / admin123"
echo "   3. Create a new Pipeline job"
echo "   4. Configure Git repository"
echo "   5. Test the CI/CD pipeline"
