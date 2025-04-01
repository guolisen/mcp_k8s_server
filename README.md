# MCP Kubernetes Server

A Kubernetes management MCP (Model Context Protocol) server that provides interfaces for getting information about Kubernetes clusters, performing operations, monitoring status, and analyzing resources.

## Features

- **Cluster Information**: Get detailed information about Kubernetes resources (pods, deployments, services, etc.)
- **Cluster Operations**: Perform operations on Kubernetes resources (create, update, delete, scale, etc.)
- **Monitoring**: Monitor the status of Kubernetes clusters and resources
- **Analysis**: Analyze Kubernetes resources and provide recommendations
- **Prompts**: Includes prompts for common Kubernetes analysis tasks

## Installation

### From Source

```bash
git clone https://github.com/yourusername/mcp-k8s-server.git
cd mcp-k8s-server
pip install -e .
```

### Using pip

```bash
pip install mcp-k8s-server
```

## Usage

### Running Directly

```bash
# Run with default settings
mcp-k8s-server

# Specify transport type
mcp-k8s-server --transport sse

# Specify port for SSE transport
mcp-k8s-server --port 8000

# Specify config file
mcp-k8s-server --config /path/to/config.yaml
```

### Using Docker

```bash
# Build the Docker image
docker build -t mcp-k8s-server .

# Run the Docker container
docker run -p 8000:8000 -v ~/.kube:/home/mcp/.kube mcp-k8s-server
```

### Deploying to Kubernetes

```bash
# Apply the Kubernetes manifests
kubectl apply -f k8s/
```

## Configuration

The server can be configured using a YAML configuration file, environment variables, or command-line arguments.

### Configuration File

```yaml
# config.yaml
server:
  name: mcp-k8s-server
  transport: both  # stdio, sse, or both
  port: 8000
  host: 0.0.0.0

kubernetes:
  config_path: ~/.kube/config
  context: default
  namespace: default
```

### Environment Variables

- `MCP_K8S_SERVER_TRANSPORT`: Transport type (stdio, sse, or both)
- `MCP_K8S_SERVER_PORT`: Port for SSE transport
- `MCP_K8S_SERVER_HOST`: Host for SSE transport
- `MCP_K8S_SERVER_CONFIG_PATH`: Path to Kubernetes config file
- `MCP_K8S_SERVER_CONTEXT`: Kubernetes context
- `MCP_K8S_SERVER_NAMESPACE`: Kubernetes namespace

## MCP Tools

The server provides the following MCP tools:

### Resource Information

- `get_resources`: Get a list of resources of a specific type
- `get_resource`: Get detailed information about a specific resource
- `get_resource_status`: Get the status of a specific resource
- `get_resource_events`: Get events related to a specific resource
- `get_resource_logs`: Get logs for a specific resource

### Resource Operations

- `create_resource`: Create a new resource
- `update_resource`: Update an existing resource
- `delete_resource`: Delete a resource
- `scale_deployment`: Scale a deployment
- `restart_deployment`: Restart a deployment
- `execute_command`: Execute a command in a pod

### Monitoring

- `get_cluster_status`: Get the overall status of the cluster
- `get_node_status`: Get the status of cluster nodes
- `get_resource_metrics`: Get metrics for a specific resource
- `get_cluster_metrics`: Get metrics for the entire cluster
- `check_cluster_health`: Perform a comprehensive health check of the cluster and get a detailed summary

## License

MIT
