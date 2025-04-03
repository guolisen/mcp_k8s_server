#!/bin/bash
set -e

# Configuration
IMAGE_NAME="mcp-k8s-server"
PORT="8000"
CONFIG_PATH="/app/config/config.yaml"

# Build the Docker image
echo "Building Docker image: ${IMAGE_NAME}"
docker build -t ${IMAGE_NAME} .

# Run the Docker container
echo "Running Docker container"
docker run -p ${PORT}:${PORT} \
  -v ~/.kube:/home/mcp/.kube \
  -v $(pwd)/config:/app/config \
  ${IMAGE_NAME}

echo "Docker container is running!"
echo "The server is accessible at http://localhost:${PORT}"
echo "Press Ctrl+C to stop the container"
