pipeline {
    agent any
    stages {

      stage('Clone Repository') {
            steps {
                git branch: 'master', url: 'https://github.com/aymenlamkhanet/school-management.git'
            }
        }

        stage('Verify Folder Structure') {
            steps {
                sh 'ls -R'  // Debug: List all files to confirm paths
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
