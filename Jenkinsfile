pipeline {
    agent any

    environment {
        DEPLOYMENT_FILE = 'deployment.yaml'
        SERVICE_FILE = 'service.yaml'
        DOCKER_IMAGE = 'kanishka9723/tomcat-sample:v1'
    }

    stages {
        stage('Generate Deployment YAML') {
            steps {
                script {
                    writeFile file: "${DEPLOYMENT_FILE}", text: """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tomcat-war-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tomcat-war
  template:
    metadata:
      labels:
        app: tomcat-war
    spec:
      containers:
      - name: tomcat-container
        image: ${DOCKER_IMAGE}
        ports:
        - containerPort: 8080
"""
                }
            }
        }

        stage('Generate Service YAML') {
            steps {
                script {
                    writeFile file: "${SERVICE_FILE}", text: """
apiVersion: v1
kind: Service
metadata:
  name: tomcat-war-service
spec:
  type: NodePort
  selector:
    app: tomcat-war
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
      nodePort: 30080
"""
                }
            }
        }

        stage('Apply to Kubernetes') {
            steps {
                sh "kubectl apply -f ${DEPLOYMENT_FILE}"
                sh "kubectl apply -f ${SERVICE_FILE}"
            }
        }

        stage('Check Rollout Status') {
            steps {
                sh "kubectl rollout status deployment/tomcat-war-deployment"
            }
        }

        stage('Verify Deployment') {
            steps {
                sh "kubectl get pods"
                sh "kubectl get svc"
            }
        }
    }

    post {
        success {
            echo 'Deployment completed successfully.'
        }
        failure {
            echo 'Deployment failed. Check Jenkins logs and Kubernetes events.'
        }
    }
}
