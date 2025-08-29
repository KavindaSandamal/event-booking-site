pipeline {
    agent any
    
    stages {
        stage('Hello World') {
            steps {
                echo '🚀 Hello from your local CI/CD pipeline!'
                echo 'This is a test to verify Jenkins is working locally.'
            }
        }
        
        stage('Environment Check') {
            steps {
                echo '🔍 Checking your local environment...'
                sh 'echo "Current directory: $(pwd)"'
                sh 'echo "Docker version: $(docker --version)"'
                sh 'echo "Jenkins is running on: localhost:8081"'
            }
        }
        
        stage('Test Docker Registry') {
            steps {
                echo '🐳 Testing Docker Registry connection...'
                sh 'curl -s http://localhost:5000/v2/_catalog || echo "Registry not ready yet"'
            }
        }
        
        stage('Success!') {
            steps {
                echo '✅ Your local CI/CD pipeline is working!'
                echo '🎉 You can now build real pipelines for your event booking platform.'
            }
        }
    }
    
    post {
        always {
            echo '🎯 Pipeline completed!'
        }
        success {
            echo '🚀 Ready to build real applications!'
        }
    }
}
