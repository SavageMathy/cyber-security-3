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
                    // 1. Levantar la app
                    sh """
                    docker rm -f zap-target || true
                    docker run -d --name zap-target -e SECRET_KEY=clave-super-secreta-para-el-pipeline -e DATABASE_PATH=/tmp/securedev.db -p 8000:8000 ${APP_IMAGE}
                    sleep 5
                    """
                    
                    // 2. Ejecutar ZAP y guardar en un volumen, luego imprimir el reporte
                    sh """
                    docker volume create zap-data || true
                    docker run --rm --network container:zap-target -v zap-data:/zap/wrk/:rw --user root -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://localhost:8000 -J zap-report.json -I || true
                    echo "========== INICIO REPORTE ZAP =========="
                    docker run --rm -v zap-data:/data alpine cat /data/zap-report.json
                    echo "========== FIN REPORTE ZAP =========="
                    """
                    
                    // 3. Limpiar
                    sh "docker rm -f zap-target"
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