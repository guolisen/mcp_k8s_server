# Client-Side Token Authentication for mcp_k8s_server

## Question
> How can I config token on client side for communicate with mcp_k8s_server? Give me some examples.

## Answer

Based on the code and configuration files, here's how you can configure token authentication on the client side to communicate with the mcp_k8s_server:

## Authentication Methods

The mcp_k8s_server supports two main authentication methods:

1. **SSE Transport Authentication** - When connecting to the server via HTTP/SSE
2. **Kubernetes API Authentication** - For the server's interactions with the Kubernetes API

## Client-Side Token Configuration Examples

### Example 1: Simple HTTP/API Key Authentication

When connecting to the mcp_k8s_server running with SSE transport (over HTTP), you can use standard HTTP authentication methods:

```python
import requests

# Base URL from your config
base_url = "http://192.168.182.128:8000"  # From your config.yaml

# API key authentication
headers = {
    "Authorization": "Bearer your-api-token-here"
}

# Make a request to an MCP endpoint
response = requests.post(
    f"{base_url}/api/mcp/tools/get_resources", 
    json={"resource_type": "pods", "namespace": "default"},
    headers=headers
)
```

### Example 2: Using an MCP Client Library

If you're building an MCP client application to interact with the server:

```python
from mcp_client import MCPClient

# Initialize client with authentication
client = MCPClient(
    server_url="http://192.168.182.128:8000",
    auth_token="your-api-token-here",
    auth_type="bearer"  # or "basic", depending on your server configuration
)

# Call MCP tools
resources = client.call_tool(
    tool_name="get_resources", 
    arguments={"resource_type": "pods", "namespace": "default"}
)
```

### Example 3: Client with Kubernetes Configuration

For a client that needs to maintain its own Kubernetes configuration:

```python
from mcp_client import MCPClient
from kubernetes import config as k8s_config

# Load Kubernetes config for client-side operations
k8s_config.load_kube_config(config_file="~/.kube/config")

# Initialize MCP client with server auth and K8s config
client = MCPClient(
    server_url="http://192.168.182.128:8000",
    auth_token="your-api-token-here",
    kubernetes_config={
        "config_path": "~/.kube/config",
        "context": "my-context",
        "namespace": "default"
    }
)

# Call Kubernetes-related tools
pod_logs = client.call_tool(
    tool_name="get_resource_logs",
    arguments={"name": "my-pod", "namespace": "default"}
)
```

### Example 4: Configuration File Approach

You can create a client configuration file (similar to the server's config.yaml):

```yaml
# client_config.yaml
server:
  url: "http://192.168.182.128:8000"
  auth:
    type: "bearer"
    token: "your-api-token-here"

kubernetes:
  config_path: "~/.kube/config"
  context: "my-context"
  namespace: "default"
```

Then load it in your client code:

```python
import yaml
from mcp_client import MCPClient

# Load client config
with open("client_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize client from config
client = MCPClient(
    server_url=config["server"]["url"],
    auth_token=config["server"]["auth"]["token"],
    auth_type=config["server"]["auth"]["type"],
    kubernetes_config=config.get("kubernetes")
)
```

## Token Sources

Depending on your setup, your authentication tokens could come from:

1. **Static configuration** - Hardcoded tokens in config files (not recommended for production)
2. **Environment variables** - Tokens loaded from environment variables
3. **Kubernetes secrets** - Tokens fetched from Kubernetes secrets
4. **Service account tokens** - For in-cluster authentication
5. **OAuth flows** - For more complex authentication scenarios

## Security Best Practices

- Never hardcode tokens in your application code
- Use environment variables or secure vaults to store tokens
- Rotate tokens periodically
- Use HTTPS for all communications
- Set appropriate token permissions and scopes
