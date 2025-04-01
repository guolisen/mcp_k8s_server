# MCP Kubernetes Server Deployment Guide

This guide provides instructions for deploying and using the MCP Kubernetes Server in various environments.

## Prerequisites

Before deploying the MCP Kubernetes Server, ensure you have the following prerequisites:

- Python 3.13 or later
- Access to a Kubernetes cluster
- Kubernetes configuration file (kubeconfig) with appropriate permissions
- Docker (for containerized deployment)

## Installation Options

The MCP Kubernetes Server can be deployed in three ways:

1. Direct Python Installation
2. Docker Container
3. Kubernetes Pod

## 1. Direct Python Installation

### Installing from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-k8s-server.git
cd mcp-k8s-server

# Install the package
pip install -e .
```

### Installing from PyPI

```bash
pip install mcp-k8s-server
```

### Running the Server

Once installed, you can run the server using the following command:

```bash
# Run with default settings
mcp-k8s-server

# Run with specific transport type
mcp-k8s-server --transport sse

# Run with specific port for SSE transport
mcp-k8s-server --port 8000

# Run with specific config file
mcp-k8s-server --config /path/to/config.yaml

# Run with debug logging
mcp-k8s-server --debug
```

## 2. Docker Container

### Building the Docker Image

```bash
# Build the Docker image
docker build -t mcp-k8s-server .
```

### Running the Docker Container

```bash
# Run with default settings
docker run -p 8000:8000 -v ~/.kube:/home/mcp/.kube mcp-k8s-server

# Run with specific transport type
docker run -p 8000:8000 -v ~/.kube:/home/mcp/.kube -e TRANSPORT=sse mcp-k8s-server

# Run with specific config file
docker run -p 8000:8000 -v ~/.kube:/home/mcp/.kube -v /path/to/config.yaml:/app/config/config.yaml mcp-k8s-server
```

### Environment Variables

The Docker container supports the following environment variables:

- `TRANSPORT`: Transport type (stdio, sse, or both)
- `PORT`: Port for SSE transport
- `HOST`: Host for SSE transport
- `CONFIG_PATH`: Path to configuration file

## 3. Kubernetes Pod

### Deploying to Kubernetes

The MCP Kubernetes Server can be deployed to a Kubernetes cluster using the provided manifests:

```bash
# Apply the Kubernetes manifests
kubectl apply -f k8s/
```

This will create the following resources:

- ServiceAccount: `mcp-k8s-server`
- ClusterRole: `mcp-k8s-server`
- ClusterRoleBinding: `mcp-k8s-server`
- ConfigMap: `mcp-k8s-server-config`
- Deployment: `mcp-k8s-server`
- Service: `mcp-k8s-server`

### Accessing the Server

Once deployed, the server can be accessed using the service:

```bash
# Port-forward the service
kubectl port-forward service/mcp-k8s-server 8000:8000
```

Then you can access the server at `http://localhost:8000`.

### Customizing the Deployment

You can customize the deployment by editing the ConfigMap:

```bash
# Edit the ConfigMap
kubectl edit configmap mcp-k8s-server-config
```

## Configuration

### Configuration File

The MCP Kubernetes Server is configured using a YAML configuration file. The default configuration file is located at `config/config.yaml`.

Here's an example configuration file:

```yaml
# MCP Kubernetes Server Configuration

server:
  name: mcp-k8s-server
  transport: both  # stdio, sse, or both
  port: 8000
  host: 0.0.0.0

kubernetes:
  # Path to kubeconfig file
  # If empty, will try to use in-cluster config when running in Kubernetes
  # or ~/.kube/config when running locally
  config_path: ""
  
  # Kubernetes context to use
  # If empty, will use the current context from kubeconfig
  context: ""
  
  # Default namespace
  namespace: default
  
  # Resource types to include
  resource_types:
    - pods
    - deployments
    - services
    - configmaps
    - secrets
    - persistentvolumeclaims
    - persistentvolumes
    - nodes
    - namespaces
    - events
    - ingresses
    - statefulsets
    - daemonsets
    - jobs
    - cronjobs
    - replicasets

monitoring:
  # Enable monitoring features
  enabled: true
  
  # Polling interval in seconds
  interval: 30
  
  # Resources to monitor
  resources:
    - pods
    - nodes
    - deployments
    
  # Metrics to collect
  metrics:
    - cpu
    - memory
    - disk
    - network
```

### Environment Variables

The MCP Kubernetes Server also supports configuration through environment variables. The environment variables override the values in the configuration file.

The environment variables are prefixed with `MCP_K8S_SERVER_` and use `__` as a separator for nested values. For example:

- `MCP_K8S_SERVER_SERVER__TRANSPORT`: Transport type (stdio, sse, or both)
- `MCP_K8S_SERVER_SERVER__PORT`: Port for SSE transport
- `MCP_K8S_SERVER_SERVER__HOST`: Host for SSE transport
- `MCP_K8S_SERVER_KUBERNETES__CONFIG_PATH`: Path to Kubernetes config file
- `MCP_K8S_SERVER_KUBERNETES__CONTEXT`: Kubernetes context
- `MCP_K8S_SERVER_KUBERNETES__NAMESPACE`: Kubernetes namespace
- `MCP_K8S_SERVER_MONITORING__ENABLED`: Enable monitoring features
- `MCP_K8S_SERVER_MONITORING__INTERVAL`: Polling interval in seconds

## Using the MCP Kubernetes Server

### Connecting to the Server

The MCP Kubernetes Server can be connected to using any MCP client. The connection URL depends on the transport type:

- **stdio**: The server is connected to directly through standard input/output.
- **SSE**: The server is connected to through HTTP at `http://<host>:<port>`.

### Using MCP Tools

The MCP Kubernetes Server provides a variety of tools for interacting with Kubernetes clusters. See the [API Reference](api-reference.md) for a complete list of available tools.

Here's an example of using the `get_resources` tool:

```python
# Example Python code using an MCP client
from mcp.client import Client

# Connect to the MCP server
client = Client("http://localhost:8000")

# Get all pods in the default namespace
pods = client.call_tool("get_resources", {"resource_type": "pods", "namespace": "default"})
print(pods)
```

### Using MCP Prompts

The MCP Kubernetes Server provides prompt templates for common Kubernetes analysis tasks. See the [API Reference](api-reference.md) for a complete list of available prompts.

Here's an example of using the `analyze_cluster_status` prompt:

```python
# Example Python code using an MCP client
from mcp.client import Client

# Connect to the MCP server
client = Client("http://localhost:8000")

# Get the cluster status
cluster_status = client.call_tool("get_cluster_status")

# Create a prompt for analyzing the cluster status
prompt = client.get_prompt("analyze_cluster_status", {"context": cluster_status})
print(prompt)
```

### Using MCP Resources

The MCP Kubernetes Server exposes Kubernetes resources as MCP resources. See the [API Reference](api-reference.md) for a complete list of available resources.

Here's an example of accessing a pod resource:

```python
# Example Python code using an MCP client
from mcp.client import Client

# Connect to the MCP server
client = Client("http://localhost:8000")

# Get all available resources
resources = client.list_resources()
print(resources)

# Read a specific resource
pod = client.read_resource("k8s://namespaces/default/pods/example-pod")
print(pod)
```

## Troubleshooting

### Common Issues

#### Connection Refused

If you get a "Connection refused" error when connecting to the MCP server, check the following:

- The server is running
- The port is correct
- The host is correct
- No firewall is blocking the connection

#### Authentication Errors

If you get authentication errors when the server tries to connect to the Kubernetes API, check the following:

- The kubeconfig file is accessible to the server
- The kubeconfig file has the correct permissions
- The kubeconfig file contains valid credentials
- The service account has the correct permissions (for in-cluster deployment)

#### Resource Not Found

If you get "Resource not found" errors when trying to access Kubernetes resources, check the following:

- The resource exists in the specified namespace
- The server has permission to access the resource
- The resource name is correct

### Logs

The MCP Kubernetes Server logs to standard output by default. You can enable debug logging for more detailed logs:

```bash
# Run with debug logging
mcp-k8s-server --debug
```

For Docker containers, you can view the logs using:

```bash
# View Docker container logs
docker logs <container-id>
```

For Kubernetes pods, you can view the logs using:

```bash
# View Kubernetes pod logs
kubectl logs deployment/mcp-k8s-server
```

## Security Considerations

### Authentication

The MCP Kubernetes Server uses the Kubernetes authentication mechanisms (kubeconfig or in-cluster) to authenticate with the Kubernetes API. Make sure the credentials have the appropriate permissions.

### Authorization

The MCP Kubernetes Server uses the Kubernetes authorization mechanisms (RBAC) to authorize access to Kubernetes resources. Make sure the service account or user has the appropriate permissions.

### Transport Security

When using the SSE transport, consider using HTTPS to secure the connection. This can be done by setting up a reverse proxy (like Nginx) in front of the MCP server.

### Non-Root Execution

The Docker container runs as a non-root user to improve security. Make sure the kubeconfig file and any other mounted files have the appropriate permissions.

## Performance Tuning

### Monitoring Interval

The monitoring interval can be adjusted to balance between real-time updates and resource usage. A shorter interval provides more up-to-date information but uses more resources.

```yaml
monitoring:
  interval: 30  # seconds
```

### Resource Types

The list of resource types to include can be adjusted to focus on the resources you care about. This can reduce the load on the Kubernetes API.

```yaml
kubernetes:
  resource_types:
    - pods
    - deployments
    - services
```

### Caching

The MCP Kubernetes Server caches resource information to reduce the load on the Kubernetes API. The cache is updated based on the monitoring interval.
