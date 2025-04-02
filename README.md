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

When deploying to Kubernetes, the server will automatically use the in-cluster configuration. The Kubernetes manifests in the `k8s/` directory are set up to:

1. Create a ServiceAccount with appropriate permissions
2. Mount the service account token and certificate
3. Set up the necessary environment variables

You can customize the deployment by editing the manifests:

```yaml
# k8s/deployment.yaml (example)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-k8s-server
  # ...
spec:
  # ...
  template:
    # ...
    spec:
      serviceAccountName: mcp-k8s-server  # Uses the ServiceAccount defined in rbac.yaml
      containers:
      - name: mcp-k8s-server
        # ...
        env:
        - name: MCP_K8S_SERVER_NAMESPACE
          value: "default"  # Set your default namespace
        # No need to set KUBERNETES_SERVICE_HOST and KUBERNETES_SERVICE_PORT
        # as they are automatically set by Kubernetes
```

The `KUBERNETES_SERVICE_HOST` and `KUBERNETES_SERVICE_PORT` environment variables are automatically set by Kubernetes when the pod is created, so you don't need to specify them in your deployment manifest.

## Configuration

The server can be configured using a YAML configuration file, environment variables, or command-line arguments.

### In-Cluster Configuration

When running inside a Kubernetes cluster, the server automatically uses the in-cluster configuration. This relies on the following:

1. Environment variables:
   - `KUBERNETES_SERVICE_HOST`: Set by Kubernetes to the IP address of the Kubernetes API server
   - `KUBERNETES_SERVICE_PORT`: Set by Kubernetes to the port of the Kubernetes API server

2. Service account token and certificate:
   - `/var/run/secrets/kubernetes.io/serviceaccount/token`: Service account token
   - `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt`: CA certificate

These are automatically set by Kubernetes when running in a pod. If you're running the server outside a Kubernetes cluster but want to test the in-cluster configuration, you would need to manually set these environment variables and create the token and certificate files.

When running outside a cluster, the server falls back to using the kubeconfig file.

### Testing In-Cluster Configuration Locally

If you want to test the in-cluster configuration locally (outside a Kubernetes cluster), you can manually set up the required environment variables and files:

1. Set the environment variables:
   ```bash
   export KUBERNETES_SERVICE_HOST=<kubernetes-api-server-ip>
   export KUBERNETES_SERVICE_PORT=<kubernetes-api-server-port>
   ```
   
   You can get these values by running:
   ```bash
   kubectl cluster-info
   ```

2. Create the service account token and certificate directories:
   ```bash
   mkdir -p /var/run/secrets/kubernetes.io/serviceaccount/
   ```

3. Copy your Kubernetes certificate and create a token:
   ```bash
   # Copy the CA certificate
   kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
   
   # Create a token file (you can use a service account token or generate a temporary one)
   echo "your-service-account-token" > /var/run/secrets/kubernetes.io/serviceaccount/token
   ```

Note that this approach requires root privileges to create files in `/var/run/secrets/`. Alternatively, you can modify the code to use different paths for testing purposes.

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
  ssl_verify: true  # Set to false to disable SSL certificate verification (insecure)
```

### Environment Variables

- `MCP_K8S_SERVER_TRANSPORT`: Transport type (stdio, sse, or both)
- `MCP_K8S_SERVER_PORT`: Port for SSE transport
- `MCP_K8S_SERVER_HOST`: Host for SSE transport
- `MCP_K8S_SERVER_CONFIG_PATH`: Path to Kubernetes config file
- `MCP_K8S_SERVER_CONTEXT`: Kubernetes context
- `MCP_K8S_SERVER_NAMESPACE`: Kubernetes namespace
- `MCP_K8S_SERVER_KUBERNETES__SSL_VERIFY`: SSL verification (true/false)

## SSL Verification

By default, the server verifies SSL certificates when connecting to the Kubernetes API server. This is the recommended setting for production environments to ensure secure communication.

However, in some development or testing scenarios, you might need to disable SSL verification:

1. When using self-signed certificates
2. When testing with a local Kubernetes cluster without proper certificates
3. When troubleshooting certificate issues

To disable SSL verification, set the `ssl_verify` option to `false` in your configuration:

```yaml
# config.yaml
kubernetes:
  ssl_verify: false  # Disable SSL verification (insecure)
```

Or using environment variables:

```bash
export MCP_K8S_SERVER_KUBERNETES__SSL_VERIFY=false
```

**Warning**: Disabling SSL verification is insecure and should only be used for testing purposes. It makes your connection vulnerable to man-in-the-middle attacks.

### Testing SSL Verification

The project includes several test scripts for testing SSL verification settings:

```bash
# Run all SSL verification tests
python tests/run_all_tests.py --ssl-verify

# Test with SSL verification disabled
python tests/test_k8s_connection.py --config config/test_config_no_ssl_verify.yaml

# Test with SSL verification enabled
python tests/test_k8s_connection.py --config config/config.yaml
```

See the [tests/README.md](tests/README.md) file for more information about the available tests.

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
