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
DOCKER_REGISTRY="dockerrepo:5000"
IMAGE_NAME="mcp-k8s-server"
IMAGE_TAG=$1
FULL_IMAGE_NAME="${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Build the Docker image
echo "Building Docker image: ${FULL_IMAGE_NAME}"
docker build -t ${FULL_IMAGE_NAME} .
rm /var/lib/ddcontainers/mcp_k8s_server/images/*
docker image save -o /var/lib/ddcontainers/mcp_k8s_server/images/${IMAGE_NAME}-${IMAGE_TAG}.tar ${FULL_IMAGE_NAME}

# Push the Docker image to the registry
echo "Pushing Docker image to registry"
cd /var/lib/ddcontainers/
./bin/dpimage remove mcp_k8s_server
./bin/dpimage push mcp_k8s_server


# Apply Kubernetes manifests
echo "Applying Kubernetes manifests"
cd /root/code/mcp_k8s_server
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

echo "Deployment complete!"
echo "To check the status of the deployment, run:"
echo "kubectl get pods -l app=mcp-k8s-server"
echo "To view the logs, run:"
echo "kubectl logs -l app=mcp-k8s-server"
