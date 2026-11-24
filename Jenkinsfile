pipeline {
    agent any

    environment {
        APP_IMAGE = 'securedev-app:latest'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', 
                        url: 'https://github.com/SavageMathy/cyber-security-3.git',
                        credentialsId: 'github-token'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh "docker build -t ${APP_IMAGE} ."
                }
            }
        }

        stage('Security Scan (ZAP)') {
            steps {
                script {
                    sh """
                    docker network create zap-net || true
                    docker run -d --rm --name zap-target --network zap-net -p 8000:8000 ${APP_IMAGE}
                    sleep 5
                    """
                    
                    sh """
                    docker run --rm --network zap-net \
                        -v \$(pwd):/zap/wrk/:rw \
                        --user root \
                        -t ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py -t http://zap-target:8000 -r zap-report.html
                    """
                    
                    sh "docker stop zap-target"
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Simulando despliegue en producción...'
            }
        }
    }
}