        stage('Security Scan (ZAP)') {
            steps {
                script {
                    // 1. Levantar la app en segundo plano en una red específica de Docker
                    sh """
                    docker network create zap-net || true
                    docker run -d --rm --name zap-target --network zap-net -p 8000:8000 ${APP_IMAGE}
                    sleep 5
                    """
                    
                    // 2. Ejecutar OWASP ZAP
                    // Usamos la red 'zap-net' y el nombre del contenedor 'zap-target' en lugar de localhost
                    sh """
                    docker run --rm --network zap-net \
                        -v \$(pwd):/zap/wrk/:rw \
                        --user root \
                        -t ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py -t http://zap-target:8000 -r zap-report.html
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