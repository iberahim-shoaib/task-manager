
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'iberahimshoaib/task-manager:latest'
        TEST_EMAIL = 'ibrahimshoaib054@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate Compose') {
            steps {
                withCredentials([
                    string(credentialsId: 'taskmanager-db-password',
                           variable: 'DB_PASSWORD'),
                    string(credentialsId: 'taskmanager-mysql-root-password',
                           variable: 'MYSQL_ROOT_PASSWORD')
                ]) {
                    sh 'docker compose -p task-manager -f docker-compose-part2.yml config -q'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}")
                }
            }
        }

        stage('Deploy Application') {
            steps {
                withCredentials([
                    string(credentialsId: 'taskmanager-db-password',
                           variable: 'DB_PASSWORD'),
                    string(credentialsId: 'taskmanager-mysql-root-password',
                           variable: 'MYSQL_ROOT_PASSWORD')
                ]) {
                    sh 'docker compose -p task-manager -f docker-compose-part2.yml up -d --remove-orphans'
                }
            }
        }
    }

    post {
        success {
            emailext(
                to: "${TEST_EMAIL}",
                subject: "SUCCESS: Task Manager Build #${BUILD_NUMBER}",
                body: """The Task Manager pipeline completed successfully.

Build Number: ${BUILD_NUMBER}
Build Status: SUCCESS
Build URL: ${BUILD_URL}

Part II application: http://52.64.64.145:8082
"""
            )
        }

        failure {
            emailext(
                to: "${TEST_EMAIL}",
                subject: "FAILED: Task Manager Build #${BUILD_NUMBER}",
                body: """The Task Manager pipeline failed.

Build Number: ${BUILD_NUMBER}
Build Status: FAILURE
Build URL: ${BUILD_URL}

Please check the Jenkins console output for details.
"""
            )
        }
    }
}
