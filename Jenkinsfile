pipeline {
    agent any
    stages {

      stage('CSM') {
            steps {
                git branch: 'master', url: 'https://github.com/gymnasiumBanner/default-management.git'
                echo 'Pulling the project...'
                // Ajoutez ici les commandes pour construire votre projet
            }
        }
        stage('Build') {
            steps {
                echo "Building.."
                sh '''
                echo "doing build stuff.."
                '''
            }
        }
        stage('Test') {
            steps {
                echo "Testing.."
                sh '''
                echo "doing test stuff.."
                '''
            }
        }
        stage('Deliver') {
            steps {
                echo 'Deliver....'
                sh '''
                echo "doing delivery stuff.."
                '''
            }
        }
    }
}
