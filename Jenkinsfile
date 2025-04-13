pipeline {
    agent any

    environment {
        KUBECONFIG = '/var/lib/jenkins/.kube/config' // ✅ Make sure this is correct
        DEPLOYMENT_FILE = 'deployment.yaml'
        SERVICE_FILE = 'service.yaml'
        DOCKER_IMAGE = 'kanishka9723/tomcat-sample:v1'
        NAMESPACE = 'default'
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
  namespace: ${NAMESPACE}
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
      restartPolicy: Always
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
  namespace: ${NAMESPACE}
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
                    sh 'echo "Checking Kubernetes Cluster Access..."'
                    sh 'kubectl version --client'
                    sh "kubectl config view"
                    sh "kubectl get nodes"
                }
            }
        }

        stage('Apply to Kubernetes') {
            steps {
                script {
                    try {
                        sh "kubectl apply -f ${DEPLOYMENT_FILE} --namespace=${NAMESPACE}"
                        sh "kubectl apply -f ${SERVICE_FILE} --namespace=${NAMESPACE}"
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
                    try {
                        sh "kubectl rollout status deployment/tomcat-war-deployment --namespace=${NAMESPACE}"
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
                    sh "kubectl get pods --namespace=${NAMESPACE}"
                    sh "kubectl get svc --namespace=${NAMESPACE}"
                }
            }
        }
    }

    post {
        success {
            echo '✅ Deployment completed successfully.'
        }
        failure {
            echo '❌ Deployment failed. Check Jenkins logs and Kubernetes events.'
        }
    }
}
