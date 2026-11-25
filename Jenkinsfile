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
                    // 1. Levantar la app. Al no especificar red, Docker la pone en la red por defecto
                    sh """
                    docker run -d --rm --name zap-target -p 8000:8000 ${APP_IMAGE}
                    sleep 5
                    """
                    
                    // 2. Ejecutar ZAP.
                    // Usamos --network container:zap-target
                    // Así, ZAP puede acceder a la app directamente usando http://localhost:8000
                    sh """
                    docker run --rm --network container:zap-target \
                        -v \$(pwd):/zap/wrk/:rw \
                        --user root \
                        -t ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py -t http://localhost:8000 -r zap-report.html
                    """
                    
                    // 3. Detener la app
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