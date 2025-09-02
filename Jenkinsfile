pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'minikube'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Images') {
            steps {
                script {
                    // Set minikube docker environment
                    sh '''
                        eval $(minikube -p minikube docker-env)
                        
                        # Build auth service
                        docker build -t auth-service:latest -f services/auth/Dockerfile services/auth/
                        
                        # Build booking service
                        docker build -t booking-service:latest -f services/booking/Dockerfile services/booking/
                        
                        # Build catalog service
                        docker build -t catalog-service:latest -f services/catalog/Dockerfile services/catalog/
                        
                        # Build payment service
                        docker build -t payment-service:latest -f services/payment/Dockerfile services/payment/
                        
                        # Build frontend
                        docker build -t frontend:latest -f frontend/Dockerfile frontend/
                    '''
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh '''
                        # Apply base configurations
                        kubectl apply -f k8s/base/
                        
                        # Restart deployments to use new images
                        kubectl rollout restart deployment/auth-service -n event-booking
                        kubectl rollout restart deployment/booking-service -n event-booking
                        kubectl rollout restart deployment/catalog-service -n event-booking
                        kubectl rollout restart deployment/payment-service -n event-booking
                        kubectl rollout restart deployment/frontend -n event-booking
                        
                        # Wait for rollouts to complete
                        kubectl rollout status deployment/auth-service -n event-booking
                        kubectl rollout status deployment/booking-service -n event-booking
                        kubectl rollout status deployment/catalog-service -n event-booking
                        kubectl rollout status deployment/payment-service -n event-booking
                        kubectl rollout status deployment/frontend -n event-booking
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        # Wait for services to be ready
                        sleep 30
                        
                        # Check pod status
                        kubectl get pods -n event-booking
                        
                        # Test health endpoints
                        kubectl port-forward -n event-booking service/auth-service 8000:8000 &
                        sleep 5
                        curl -f http://localhost:8000/health || exit 1
                        pkill -f "kubectl port-forward"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}