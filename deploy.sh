#!/bin/bash
#
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Shell script for the MCP Kubernetes server: deploy.sh
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
set -e

# Configuration
DOCKER_REGISTRY="guolisen"
IMAGE_NAME="mcp-k8s-server"
IMAGE_TAG=$1
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
