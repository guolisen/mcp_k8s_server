#!/bin/bash
set -e

# Configuration
DOCKER_REGISTRY="dockerrepo:30500"
IMAGE_NAME="mcp-k8s-server"
IMAGE_TAG="1.2"
FULL_IMAGE_NAME="${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Build the Docker image
echo "Building Docker image: ${FULL_IMAGE_NAME}"
docker build -t ${FULL_IMAGE_NAME} .

# Push the Docker image to the registry
echo "Pushing Docker image to registry"
docker push ${FULL_IMAGE_NAME}

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests"
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

echo "Deployment complete!"
echo "To check the status of the deployment, run:"
echo "kubectl get pods -l app=mcp-k8s-server"
echo "To view the logs, run:"
echo "kubectl logs -l app=mcp-k8s-server"
