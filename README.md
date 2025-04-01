# MCP Kubernetes Server

A Model Context Protocol (MCP) server for Kubernetes cluster management, monitoring, and status detection.

## Overview

The MCP Kubernetes Server provides interfaces to interact with Kubernetes clusters through the Model Context Protocol. It enables LLMs to:

- Retrieve information about cluster resources (nodes, deployments, etc.)
- Perform operations on the cluster (scaling, restarting, etc.)
- Monitor cluster status and health
- Detect and diagnose issues

## Features

### Resource Interfaces

- **Nodes**: Get information about cluster nodes
- **Deployments**: Manage and monitor deployments
- **Services**: Access service details and status
- **ConfigMaps/Secrets**: View configuration resources
- **StatefulSets/DaemonSets**: Monitor stateful applications
- **Jobs/CronJobs**: Track batch processing tasks
- **Ingresses**: Access ingress configuration
- **PersistentVolumes/PVCs**: Storage management

### Operation Tools

- **Scale Deployments**: Adjust the number of replicas
- **Restart Deployments**: Rolling restarts
- **Create Namespaces**: Organize resources
- **Delete Resources**: Remove Kubernetes objects
- **Get Logs**: View container logs
- **Execute Commands**: Run commands in containers

### Monitoring Tools

- **Cluster Health**: Overall health status
- **Resource Usage**: CPU and memory metrics
- **Pod Resource Usage**: Container resource utilization
- **Events**: Track cluster events
- **Resource Description**: Detailed resource information

### Status Detection Tools

- **Component Status**: Check cluster components
- **Node Health**: Detailed node diagnostics
- **Deployment Health**: Verify deployment status
- **API Server Health**: API server connectivity
- **Resource Quotas**: Track resource usage limits
- **Cluster Diagnostics**: Comprehensive health check

## Installation

### Prerequisites

- Python 3.8+
- Access to a Kubernetes cluster
- `kubectl` installed and configured

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp_k8s_server.git
   cd mcp_k8s_server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

### Starting the Server

Run the MCP server with:

```bash
python -m src.server
```

Options:
- `--config PATH`: Path to configuration file
- `--kubeconfig PATH`: Path to kubeconfig file (overrides config file)
- `--bind-ip IP`: IP address to bind to (overrides config file)
- `--bind-port PORT`: Port to bind to (overrides config file)
- `--mode {stdio,network}`: Server mode (overrides config file)
- `--debug`: Enable debug logging

### Configuration File

The server can be configured using a YAML configuration file. Create a `config.yaml` file with the following structure:

```yaml
server:
  bind_ip: "0.0.0.0"  # IP address to bind to
  bind_port: 8080     # Port to bind to
  mode: "network"     # "network" or "stdio"

kubernetes:
  kubeconfig_path: null  # Path to kubeconfig file, null for default

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: null     # Path to log file, null for stderr only
```

To use the configuration file:

```bash
python -m src.server --config config.yaml
```

### MCP Configuration

Add the server to your MCP configuration file:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "python",
      "args": ["-m", "src.server", "--config", "/path/to/config.yaml"],
      "env": {
        "KUBECONFIG": "/path/to/kubeconfig"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For network mode, you can also specify:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "python",
      "args": ["-m", "src.server", "--mode", "network", "--bind-ip", "127.0.0.1", "--bind-port", "8080"],
      "env": {
        "KUBECONFIG": "/path/to/kubeconfig"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Authentication

The server uses your default Kubernetes configuration. Make sure you have proper permissions to access and manage your cluster.

## Resource URI Format

Resources follow this URI format:
- `kubernetes://[resource_type]` - All resources of a type
- `kubernetes://[resource_type]/[namespace]` - Resources in a namespace
- `kubernetes://[resource_type]/[namespace]/[name]` - Specific resource

Examples:
- `kubernetes://nodes` - All nodes
- `kubernetes://deployments/default` - All deployments in default namespace
- `kubernetes://deployments/kube-system/coredns` - Specific deployment

## Tools

Tools are available for various cluster operations, monitoring, and status detection. Each tool accepts specific parameters defined in the MCP interface.

## License

[Include license information here]
