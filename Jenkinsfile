pipeline {
    agent any
    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }
    triggers {
        githubPush()
        // Local Jenkins can detect commits without an internet-facing webhook.
        pollSCM('H/5 * * * *')
    }
    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }
        stage('Install dependencies') {
            steps {
                sh 'python3 -m venv .venv-ci'
                sh '.venv-ci/bin/python -m pip install -r requirements.txt'
            }
        }
        stage('Offline tests') {
            steps {
                sh '.venv-ci/bin/python scripts/run_offline_tests.py'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'test-results/unittest.txt', allowEmptyArchive: true
            deleteDir()
        }
    }
}
