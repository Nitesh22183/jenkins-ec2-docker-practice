pipeline {
    agent any

    environment {
        AWS_REGION = "us-east-1"
        AWS_ACCOUNT_ID = "656697807549"

        IMAGE_NAME = "jenkins-ec2-docker-practice"
        IMAGE_TAG = "${BUILD_NUMBER}"

        ECR_REPO = "656697807549.dkr.ecr.us-east-1.amazonaws.com/jenkins-ec2-docker-practice"

        EC2_HOST = "52.90.133.186"
        EC2_USER = "ubuntu"
        CONTAINER_NAME = "endava-practice-app"
        APP_PORT = "5000"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "Pulling code from GitHub..."
                checkout scm
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo "Installing dependencies and running tests..."
                sh '''
                    python3 --version
                    pip3 install -r requirements.txt
                    python3 -m pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh '''
                    docker build -t $IMAGE_NAME:$IMAGE_TAG .
                    docker tag $IMAGE_NAME:$IMAGE_TAG $ECR_REPO:$IMAGE_TAG
                    docker tag $IMAGE_NAME:$IMAGE_TAG $ECR_REPO:latest
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                echo "Logging Docker into AWS ECR..."
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                echo "Pushing image to ECR..."
                sh '''
                    docker push $ECR_REPO:$IMAGE_TAG
                    docker push $ECR_REPO:latest
                '''
            }
        }

        stage('Deploy on EC2') {
            steps {
                echo "Connecting to EC2 and deploying container..."
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST "
                            aws ecr get-login-password --region $AWS_REGION | \
                            docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com &&

                            docker pull $ECR_REPO:$IMAGE_TAG &&

                            docker rm -f $CONTAINER_NAME || true &&

                            docker run -d \
                              --name $CONTAINER_NAME \
                              -p $APP_PORT:5000 \
                              -e ENV_NAME=dev \
                              $ECR_REPO:$IMAGE_TAG &&

                            docker ps
                        "
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                echo "Checking app health..."
                sh '''
                    sleep 10
                    curl http://$EC2_HOST:$APP_PORT/health
                '''
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Image pushed to ECR and deployed on EC2."
        }
        failure {
            echo "FAILED: Check the failed Jenkins stage."
        }
        always {
            echo "Pipeline completed."
        }
    }
}
