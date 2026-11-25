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
                    // 1. Levantar la app CON la SECRET_KEY para que no falle
                    sh """
                    docker rm -f zap-target || true
                    docker run -d --name zap-target -e SECRET_KEY=clave-super-secreta-para-el-pipeline -p 8000:8000 ${APP_IMAGE}
                    sleep 5
                    """
                    
                    // 2. Ejecutar ZAP compartiendo la red del contenedor
                    sh """
                    docker run --rm --network container:zap-target \
                        -v \$(pwd):/zap/wrk/:rw \
                        --user root \
                        -t ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py -t http://localhost:8000 -r zap-report.html
                    """
                    
                    // 3. Limpiar el contenedor
                    sh "docker rm -f zap-target"
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