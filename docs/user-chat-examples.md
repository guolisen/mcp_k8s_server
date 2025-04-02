# MCP Kubernetes Server User Chat Examples

This document provides examples of natural language user chat messages that would trigger each MCP Kubernetes Server interface. These examples can be used to understand how to interact with the server through conversational AI assistants.

## Resource Information Tools

### get_resources

**User Chat Examples:**
- "Show me all pods in the default namespace"
- "List all deployments in the system"
- "What services are running in the kube-system namespace?"
- "Show me all the configmaps"
- "List all persistent volumes in the cluster"

### get_resource

**User Chat Examples:**
- "Show me details about the nginx-pod"
- "Tell me about the frontend deployment"
- "What's the configuration of the kubernetes service?"
- "Give me information about the config-map-1 configmap"
- "Show me the details of the persistent volume claim pvc-1"

### get_resource_status

**User Chat Examples:**
- "What's the status of the nginx-pod?"
- "Is the frontend deployment healthy?"
- "Check the status of the database service"
- "Tell me if the config-map-1 configmap is working properly"
- "What's the current state of the persistent volume claim pvc-1?"

### get_resource_events

**User Chat Examples:**
- "Show me events related to the nginx-pod"
- "What events have happened with the frontend deployment?"
- "List all events for the database service"
- "Show me the event history for the config-map-1 configmap"
- "What events are associated with the persistent volume claim pvc-1?"

### get_pod_logs

**User Chat Examples:**
- "Show me the logs for the nginx-pod"
- "What are the recent logs from the database pod?"
- "Display the last 100 lines of logs from the frontend pod"
- "Show me the logs from the auth-container in the api-pod"
- "What errors are showing up in the logs of the monitoring pod?"

## Resource Operation Tools

### create_resource

**User Chat Examples:**
- "Create a new pod with the nginx image"
- "Deploy a new application using this YAML"
- "Set up a new service for the frontend deployment"
- "Create a configmap with these key-value pairs"
- "I need a new persistent volume claim for my database"

### update_resource

**User Chat Examples:**
- "Update the nginx-pod to use the latest nginx image"
- "Change the replica count in the frontend deployment"
- "Modify the service port for the database service"
- "Update the values in the config-map-1 configmap"
- "Change the storage size of the persistent volume claim pvc-1"

### delete_resource

**User Chat Examples:**
- "Delete the nginx-pod"
- "Remove the frontend deployment"
- "Get rid of the database service"
- "Delete the config-map-1 configmap"
- "Remove the persistent volume claim pvc-1"

### scale_deployment

**User Chat Examples:**
- "Scale the frontend deployment to 5 replicas"
- "Increase the number of pods in the api deployment to 3"
- "Reduce the database deployment to 1 replica"
- "Scale up the worker deployment to handle more load"
- "I need more instances of the cache deployment, scale it to 4"

### restart_deployment

**User Chat Examples:**
- "Restart the frontend deployment"
- "Roll the api deployment"
- "Restart all pods in the database deployment"
- "I need to refresh the worker deployment"
- "Perform a rolling restart of the cache deployment"

### execute_command

**User Chat Examples:**
- "Run 'ls -la' in the nginx-pod"
- "Execute 'cat /etc/config.json' in the database pod"
- "Check the environment variables in the api pod with 'env'"
- "Run 'curl localhost:8080/health' inside the frontend pod"
- "Execute 'df -h' in the storage pod to check disk usage"

## Monitoring Tools

### get_cluster_status

**User Chat Examples:**
- "What is my cluster status now?"
- "Give me an overview of the cluster health"
- "How is the Kubernetes cluster doing?"
- "Show me the current state of the cluster"
- "Is my cluster healthy?"

### get_node_status

**User Chat Examples:**
- "What's the status of all nodes in the cluster?"
- "Is node-1 healthy?"
- "Show me the condition of the worker nodes"
- "Are there any issues with the cluster nodes?"
- "Give me details about the master node"

### get_resource_metrics

**User Chat Examples:**
- "What's the CPU and memory usage of the nginx-pod?"
- "Show me the metrics for the frontend deployment"
- "How much resources is the database pod consuming?"
- "Give me the performance metrics of node-1"
- "What's the resource utilization of the kube-system namespace?"

### check_cluster_health

**User Chat Examples:**
- "Perform a health check on the cluster"
- "Is everything working properly in the cluster?"
- "Run a comprehensive check of the Kubernetes cluster"
- "Are there any issues I should be aware of in the cluster?"
- "Give me a full health report of the Kubernetes environment"

## Prompt Usage

### analyze_cluster_status

**User Chat Examples:**
- "Analyze the current state of my cluster"
- "Help me understand what's going on with my Kubernetes cluster"
- "Provide insights into my cluster's health"
- "What should I know about my cluster's current status?"
- "Give me an analysis of the cluster performance"

### troubleshoot_pod_issues

**User Chat Examples:**
- "Why is my nginx-pod crashing?"
- "Help me troubleshoot issues with the database pod"
- "My frontend pod is in a CrashLoopBackOff state, what's wrong?"
- "The api pod is not starting properly, can you help?"
- "Diagnose why my application pod is not responding"

### analyze_resource_usage

**User Chat Examples:**
- "Analyze the resource usage in my cluster"
- "Are there any pods using too many resources?"
- "Help me understand the CPU and memory consumption patterns"
- "Which deployments are using the most resources?"
- "Is my cluster efficiently utilizing resources?"

### security_assessment

**User Chat Examples:**
- "Assess the security of my Kubernetes cluster"
- "Are there any security vulnerabilities in my cluster setup?"
- "Perform a security audit of my Kubernetes environment"
- "Check if my cluster follows security best practices"
- "What security improvements should I make to my cluster?"

### performance_optimization

**User Chat Examples:**
- "How can I optimize the performance of my cluster?"
- "Suggest ways to make my Kubernetes environment faster"
- "What performance bottlenecks exist in my cluster?"
- "Help me improve the efficiency of my Kubernetes resources"
- "Recommend performance tuning for my Kubernetes deployments"

### cost_optimization

**User Chat Examples:**
- "How can I reduce the cost of running my Kubernetes cluster?"
- "Suggest ways to optimize resource allocation for cost savings"
- "Are there any unused resources I can remove to save money?"
- "Help me understand how to right-size my deployments"
- "What cost-saving measures can I implement in my Kubernetes environment?"

## Resource Access

### k8s://namespaces/{namespace}

**User Chat Examples:**
- "Show me everything in the default namespace"
- "What resources exist in the kube-system namespace?"
- "Give me a complete overview of the application namespace"
- "What's running in the monitoring namespace?"
- "Show all resources in the database namespace"

### k8s://nodes/{name}

**User Chat Examples:**
- "Tell me about node-1"
- "Show me the details of the master node"
- "What's the configuration of worker-3?"
- "Give me information about the node running my database"
- "Show me the specs of the node with IP 10.0.0.5"

### k8s://namespaces/{namespace}/pods/{name}

**User Chat Examples:**
- "Show me the nginx-pod in the default namespace"
- "What's in the monitoring pod in the system namespace?"
- "Give me details about the database-0 pod in the database namespace"
- "Show me the configuration of the frontend-5d4d4d4d4d-abcde pod"
- "I need information about the redis pod in the cache namespace"

### k8s://namespaces/{namespace}/deployments/{name}

**User Chat Examples:**
- "Show me the frontend deployment in the default namespace"
- "What's the configuration of the api deployment?"
- "Give me details about the database deployment in the database namespace"
- "Show me the replica count and strategy for the cache deployment"
- "I need information about the monitoring deployment in the system namespace"

### k8s://namespaces/{namespace}/services/{name}

**User Chat Examples:**
- "Show me the frontend service in the default namespace"
- "What's the configuration of the api service?"
- "Give me details about the database service in the database namespace"
- "Show me the ports and target ports for the cache service"
- "I need information about the monitoring service in the system namespace"

## Combined Operations

### Deployment Management

**User Chat Examples:**
- "Create a new deployment with 3 replicas of nginx and expose it on port 80"
- "Update the frontend deployment to use the latest image and scale it to 5 replicas"
- "Check the health of the api deployment and show me its logs if there are any issues"
- "Roll out the database deployment and monitor its status during the update"
- "Delete the test deployment and all associated services and configmaps"

### Troubleshooting Workflows

**User Chat Examples:**
- "One of my pods is crashing, help me figure out why and fix it"
- "The frontend service is not accessible, diagnose the issue"
- "My cluster seems to be running slowly, identify the performance bottlenecks"
- "I'm getting 'out of memory' errors, help me find which pods are using too much memory"
- "The persistent volume claim is stuck in pending state, what's wrong?"

### Cluster Administration

**User Chat Examples:**
- "Give me a complete overview of my cluster's health, resource usage, and potential issues"
- "Help me optimize my cluster for both performance and cost"
- "Perform a security audit of my cluster and suggest improvements"
- "I need to migrate workloads from node-1 to node-2, help me plan and execute this"
- "Create a backup strategy for all critical resources in my cluster"

## Multi-step Operations

### Application Deployment

**User Chat Examples:**
- "Deploy a three-tier application with a frontend, API, and database"
- "Set up a highly available Redis cluster with sentinel"
- "Deploy a monitoring stack with Prometheus and Grafana"
- "Create a CI/CD pipeline using Jenkins in Kubernetes"
- "Set up a development environment with namespaces for each team member"

### Cluster Maintenance

**User Chat Examples:**
- "Help me upgrade my Kubernetes cluster from version 1.24 to 1.25"
- "I need to add a new node to my cluster, walk me through the process"
- "Perform routine maintenance on my cluster including updating certificates"
- "Help me implement a backup and restore solution for etcd"
- "Set up a disaster recovery plan for my Kubernetes environment"

### Performance Tuning

**User Chat Examples:**
- "My application is experiencing high latency, help me diagnose and fix the issues"
- "Optimize the resource requests and limits for all my deployments"
- "Implement horizontal pod autoscaling for my web application based on CPU usage"
- "Set up network policies to improve security and reduce unnecessary traffic"
- "Help me implement a caching layer to improve application performance"
