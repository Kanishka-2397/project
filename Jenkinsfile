pipeline {
    agent any

    environment {
        KUBECONFIG = '/path/to/kubeconfig'  // Ensure this is correct
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

        stage('Validate kubectl Configuration') {
            steps {
                script {
                    // Check if KUBECONFIG is set and kubectl can access the cluster
                    sh 'echo "Checking Kubernetes Cluster Access..."'
                    sh 'kubectl version --client'  // Validate kubectl installation
                    sh "kubectl config view"
                    sh "kubectl get nodes"
                }
            }
        }

        stage('Apply to Kubernetes') {
            steps {
                script {
                    // Apply the deployment and service YAML files to Kubernetes
                    try {
                        sh "kubectl apply -f ${DEPLOYMENT_FILE}"
                        sh "kubectl apply -f ${SERVICE_FILE}"
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Kubernetes deployment failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Check Rollout Status') {
            steps {
                script {
                    // Wait for the deployment to be rolled out successfully
                    try {
                        sh "kubectl rollout status deployment/tomcat-war-deployment"
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Rollout failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    // Verify the deployed pods and service status
                    sh "kubectl get pods"
                    sh "kubectl get svc"
                }
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
