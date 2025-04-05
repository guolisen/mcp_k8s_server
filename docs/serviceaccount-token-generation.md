# Service Account Token Generation for mcp_k8s_server

## Question
> How can I generate a temporary serviceaccount token for use with mcp_k8s_server?

## Answer

The mcp_k8s_server uses Kubernetes service account tokens for authentication. Here are several methods to generate temporary tokens for different scenarios.

## Understanding Token Types in Kubernetes

In Kubernetes, there are several ways to generate service account tokens:

1. **Automatically Mounted Tokens**: Each pod gets a token automatically mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`
2. **TokenRequest API**: For generating short-lived tokens with explicit expiration 
3. **Service Account Token Secret**: Manually created, longer-lived tokens

Based on the project configuration, mcp_k8s_server uses a service account named `mcp-k8s-server` (as defined in k8s/rbac.yaml and k8s/deployment.yaml).

## Method 1: Generate a Token Using kubectl

The simplest way to generate a temporary token is using kubectl:

```bash
# Create a temporary token valid for 1 hour (3600 seconds)
kubectl create token mcp-k8s-server --duration=3600s
```

This uses the TokenRequest API and generates a short-lived JWT token.

## Method 2: Use the TokenRequest API Programmatically

If you want to generate tokens programmatically from your code, you could use the Kubernetes API directly:

```python
from kubernetes import client, config
from datetime import datetime, timedelta

# Load kube config
config.load_kube_config()  # or config.load_incluster_config() if running in a pod

# Create API client
api = client.CoreV1Api()

# Create token request
expiration = int((datetime.now() + timedelta(hours=1)).timestamp())
token_request = client.V1TokenRequest(
    spec=client.V1TokenRequestSpec(
        audiences=["https://kubernetes.default.svc"],
        expiration_seconds=3600  # 1 hour in seconds
    )
)

# Request the token
token_response = api.create_namespaced_service_account_token(
    "default",  # Namespace where the service account exists
    "mcp-k8s-server",  # Service account name
    token_request
)

# Use the token
token = token_response.status.token
print(f"Token: {token}")
```

## Method 3: For Local Development/Testing

For local development, you can extract the token from an existing Kubernetes secret:

1. First, find the secret associated with the service account:
   ```bash
   kubectl get serviceaccount mcp-k8s-server -o jsonpath='{.secrets[0].name}'
   ```

2. Then, extract the token from the secret:
   ```bash
   kubectl get secret <secret-name> -o jsonpath='{.data.token}' | base64 --decode
   ```

Note: In newer Kubernetes versions (v1.24+), service accounts don't automatically get a secret created, so you would use Method 1 or 2 instead.

## Using the Token with mcp_k8s_server

Once you have the token, you can use it for authentication as described in client-authentication.md:

```python
import requests

# Base URL from your config
base_url = "http://192.168.182.128:8000"  # From your config.yaml

# API key authentication
headers = {
    "Authorization": "Bearer your-generated-token-here"
}

# Make a request to an MCP endpoint
response = requests.post(
    f"{base_url}/api/mcp/tools/get_resources", 
    json={"resource_type": "pods", "namespace": "default"},
    headers=headers
)
```

## Token Security Best Practices

When working with service account tokens, keep these security practices in mind:

1. **Use short-lived tokens**: Generate tokens with the shortest practical lifetime for your use case
2. **Limit token scope**: Use service accounts with the minimum required permissions
3. **Secure token storage**: Never hard-code tokens in your application or commit them to source control
4. **Use HTTPS**: Always use encrypted connections when transmitting tokens
5. **Rotate tokens**: Regularly generate new tokens for long-running applications
6. **Audit token usage**: Monitor token usage for suspicious activity

## Additional Resources

- [Kubernetes Documentation: Managing Service Accounts](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/)
- [Kubernetes Documentation: ServiceAccount TokenRequest API](https://kubernetes.io/docs/reference/kubernetes-api/authentication-resources/token-request-v1/)
