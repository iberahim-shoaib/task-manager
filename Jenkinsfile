
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'iberahimshoaib/task-manager:latest'
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
                    sh 'docker compose -f docker-compose-part2.yml config -q'
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
                    sh 'docker compose -f docker-compose-part2.yml up -d --remove-orphans'
                }
            }
        }
    }
}
