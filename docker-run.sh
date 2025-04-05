#!/bin/bash
#
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Shell script for the MCP Kubernetes server: docker-run.sh
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
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
