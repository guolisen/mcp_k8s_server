#!/bin/bash
#
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Shell script for the MCP Kubernetes server: env.sh
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

mkdir -p /var/run/secrets/kubernetes.io/serviceaccount/
kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > ls 
echo "your-service-account-token" > /var/run/secrets/kubernetes.io/serviceaccount/token


