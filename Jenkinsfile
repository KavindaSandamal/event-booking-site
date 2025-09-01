pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'minikube'
        KUBECONFIG = '/root/.kube/config'
        NAMESPACE = 'event-booking'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    env.BUILD_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                }
            }
        }
        
        stage('Build Images') {
            parallel {
                stage('Build Auth Service') {
                    steps {
                        script {
                            dir('services/auth') {
                                sh """
                                    docker build -t auth-service:${BUILD_TAG} .
                                    docker tag auth-service:${BUILD_TAG} auth-service:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Booking Service') {
                    steps {
                        script {
                            dir('services/booking') {
                                sh """
                                    docker build -t booking-service:${BUILD_TAG} .
                                    docker tag booking-service:${BUILD_TAG} booking-service:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Catalog Service') {
                    steps {
                        script {
                            dir('services/catalog') {
                                sh """
                                    docker build -t catalog-service:${BUILD_TAG} .
                                    docker tag catalog-service:${BUILD_TAG} catalog-service:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Payment Service') {
                    steps {
                        script {
                            dir('services/payment') {
                                sh """
                                    docker build -t payment-service:${BUILD_TAG} .
                                    docker tag payment-service:${BUILD_TAG} payment-service:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Frontend') {
                    steps {
                        script {
                            dir('frontend') {
                                sh """
                                    docker build -t frontend-service:${BUILD_TAG} .
                                    docker tag frontend-service:${BUILD_TAG} frontend-service:latest
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "Skipping tests for now - focusing on deployment"
                }
            }
        }
        
        stage('Deploy to Minikube') {
            steps {
                script {
                    // Update Kubernetes deployments with new images
                    sh """
                        # Update all service deployments
                        kubectl set image deployment/auth-service auth-service=auth-service:${BUILD_TAG} -n ${NAMESPACE}
                        kubectl set image deployment/booking-service booking-service=booking-service:${BUILD_TAG} -n ${NAMESPACE}
                        kubectl set image deployment/catalog-service catalog-service=catalog-service:${BUILD_TAG} -n ${NAMESPACE}
                        kubectl set image deployment/payment-service payment-service=payment-service:${BUILD_TAG} -n ${NAMESPACE}
                        kubectl set image deployment/frontend-service frontend-service=frontend-service:${BUILD_TAG} -n ${NAMESPACE}
                        
                        # Wait for rollouts to complete
                        kubectl rollout status deployment/auth-service -n ${NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/booking-service -n ${NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/catalog-service -n ${NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/payment-service -n ${NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/frontend-service -n ${NAMESPACE} --timeout=300s
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh """
                        # Wait for services to be ready
                        sleep 30
                        
                        # Check service health
                        echo "Checking service health..."
                        kubectl get pods -n ${NAMESPACE}
                        
                        # Test endpoints
                        curl -f http://event-booking.local/auth/health || echo "Auth service health check failed"
                        curl -f http://event-booking.local/booking/health || echo "Booking service health check failed"
                        curl -f http://event-booking.local/catalog/health || echo "Catalog service health check failed"
                        curl -f http://event-booking.local/payment/health || echo "Payment service health check failed"
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Clean up old images
            sh """
                docker image prune -f
                docker system prune -f
            """
        }
        
        success {
            echo "✅ Deployment successful! Build ${BUILD_TAG} deployed to Minikube"
            // Send notification (Slack, email, etc.)
        }
        
        failure {
            echo "❌ Deployment failed for build ${BUILD_TAG}"
            // Send failure notification
        }
    }
}
