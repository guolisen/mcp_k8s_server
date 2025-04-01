# MCP Kubernetes Server API Reference

This document provides a comprehensive reference for the API exposed by the MCP Kubernetes Server, including all available tools, prompts, and resources.

## MCP Tools

The MCP Kubernetes Server exposes the following tools that can be called by MCP clients:

### Resource Information Tools

These tools provide information about Kubernetes resources.

#### `get_resources`

Get a list of resources of a specific type.

**Parameters:**
- `resource_type` (string, required): Type of resource (pods, deployments, services, etc.).
- `namespace` (string, optional): Namespace to get resources from. If not provided, uses the default namespace. Use "all" to get resources from all namespaces.

**Returns:**
JSON string with the list of resources.

**Example:**
```json
[
  {
    "kind": "Pod",
    "apiVersion": "v1",
    "name": "example-pod",
    "namespace": "default",
    "creationTimestamp": "2025-04-01T12:00:00Z",
    "status": {
      "phase": "Running",
      "conditions": [...]
    }
  },
  ...
]
```

#### `get_resource`

Get detailed information about a specific resource.

**Parameters:**
- `resource_type` (string, required): Type of resource (pod, deployment, service, etc.).
- `name` (string, required): Name of the resource.
- `namespace` (string, optional): Namespace of the resource. If not provided, uses the default namespace.

**Returns:**
JSON string with the resource information.

**Example:**
```json
{
  "kind": "Pod",
  "apiVersion": "v1",
  "name": "example-pod",
  "namespace": "default",
  "creationTimestamp": "2025-04-01T12:00:00Z",
  "status": {
    "phase": "Running",
    "conditions": [...]
  },
  "spec": {
    "containers": [...]
  }
}
```

#### `get_resource_status`

Get the status of a specific resource.

**Parameters:**
- `resource_type` (string, required): Type of resource (pod, deployment, service, etc.).
- `name` (string, required): Name of the resource.
- `namespace` (string, optional): Namespace of the resource. If not provided, uses the default namespace.

**Returns:**
JSON string with the resource status.

**Example:**
```json
{
  "phase": "Running",
  "conditions": [
    {
      "type": "Ready",
      "status": "True",
      "lastProbeTime": null,
      "lastTransitionTime": "2025-04-01T12:00:00Z"
    },
    ...
  ],
  "containerStatuses": [...]
}
```

#### `get_resource_events`

Get events related to a specific resource.

**Parameters:**
- `resource_type` (string, required): Type of resource (pod, deployment, service, etc.).
- `name` (string, required): Name of the resource.
- `namespace` (string, optional): Namespace of the resource. If not provided, uses the default namespace.

**Returns:**
JSON string with the resource events.

**Example:**
```json
[
  {
    "kind": "Event",
    "apiVersion": "v1",
    "name": "example-pod.16b4a9c5d4e3f2b1",
    "namespace": "default",
    "reason": "Started",
    "message": "Started container example",
    "type": "Normal",
    "count": 1,
    "firstTimestamp": "2025-04-01T12:00:00Z",
    "lastTimestamp": "2025-04-01T12:00:00Z",
    "involvedObject": {
      "kind": "Pod",
      "name": "example-pod",
      "namespace": "default"
    }
  },
  ...
]
```

#### `get_pod_logs`

Get logs for a pod.

**Parameters:**
- `name` (string, required): Name of the pod.
- `namespace` (string, optional): Namespace of the pod. If not provided, uses the default namespace.
- `container` (string, optional): Name of the container. If not provided, uses the first container.
- `tail_lines` (integer, optional): Number of lines to return from the end of the logs. Default is 100.

**Returns:**
Pod logs as a string.

**Example:**
```
2025-04-01T12:00:00.000000Z stdout F Starting application...
2025-04-01T12:00:01.000000Z stdout F Application started successfully.
...
```

### Resource Operation Tools

These tools perform operations on Kubernetes resources.

#### `create_resource`

Create a resource from YAML.

**Parameters:**
- `resource_yaml` (string, required): YAML representation of the resource.

**Returns:**
JSON string with the result of the operation.

**Example:**
```json
{
  "success": true,
  "message": "Created Pod example-pod in namespace default",
  "resource": {
    "kind": "Pod",
    "apiVersion": "v1",
    "name": "example-pod",
    "namespace": "default",
    ...
  }
}
```

#### `update_resource`

Update a resource from YAML.

**Parameters:**
- `resource_yaml` (string, required): YAML representation of the resource.

**Returns:**
JSON string with the result of the operation.

**Example:**
```json
{
  "success": true,
  "message": "Updated Pod example-pod in namespace default",
  "resource": {
    "kind": "Pod",
    "apiVersion": "v1",
    "name": "example-pod",
    "namespace": "default",
    ...
  }
}
```

#### `delete_resource`

Delete a resource.

**Parameters:**
- `resource_type` (string, required): Type of resource (pod, deployment, service, etc.).
- `name` (string, required): Name of the resource.
- `namespace` (string, optional): Namespace of the resource. If not provided, uses the default namespace.

**Returns:**
JSON string with the result of the operation.

**Example:**
```json
{
  "success": true,
  "message": "Deleted Pod example-pod in namespace default"
}
```

#### `scale_deployment`

Scale a deployment.

**Parameters:**
- `name` (string, required): Name of the deployment.
- `replicas` (integer, required): Number of replicas.
- `namespace` (string, optional): Namespace of the deployment. If not provided, uses the default namespace.

**Returns:**
JSON string with the result of the operation.

**Example:**
```json
{
  "success": true,
  "message": "Scaled deployment example-deployment to 3 replicas in namespace default"
}
```

#### `restart_deployment`

Restart a deployment.

**Parameters:**
- `name` (string, required): Name of the deployment.
- `namespace` (string, optional): Namespace of the deployment. If not provided, uses the default namespace.

**Returns:**
JSON string with the result of the operation.

**Example:**
```json
{
  "success": true,
  "message": "Restarted deployment example-deployment in namespace default"
}
```

#### `execute_command`

Execute a command in a pod.

**Parameters:**
- `pod_name` (string, required): Name of the pod.
- `command` (string, required): Command to execute (as a string, will be split on spaces).
- `namespace` (string, optional): Namespace of the pod. If not provided, uses the default namespace.
- `container` (string, optional): Name of the container. If not provided, uses the first container.

**Returns:**
JSON string with the result of the operation.

**Example:**
```json
{
  "success": true,
  "message": "Executed command in pod example-pod in namespace default",
  "output": "Hello, World!\n"
}
```

### Monitoring Tools

These tools provide monitoring information about the Kubernetes cluster.

#### `get_cluster_status`

Get the overall status of the cluster.

**Parameters:**
None

**Returns:**
JSON string with the cluster status.

**Example:**
```json
{
  "timestamp": 1712047200,
  "status": "Healthy",
  "nodes": {
    "total": 3,
    "ready": 3
  },
  "pods": {
    "total": 10,
    "running": 10,
    "pending": 0,
    "failed": 0,
    "succeeded": 0,
    "unknown": 0
  },
  "deployments": {
    "total": 5,
    "available": 5,
    "unavailable": 0
  }
}
```

#### `get_node_status`

Get the status of a node or all nodes.

**Parameters:**
- `name` (string, optional): Name of the node. If not provided, returns status of all nodes.

**Returns:**
JSON string with the node status.

**Example:**
```json
{
  "node-1": {
    "name": "node-1",
    "ready": true,
    "conditions": [...],
    "addresses": [...],
    "capacity": {...},
    "allocatable": {...},
    "architecture": "amd64",
    "kernelVersion": "5.15.0",
    "osImage": "Ubuntu 22.04.2 LTS",
    "containerRuntimeVersion": "containerd://1.6.0",
    "kubeletVersion": "v1.26.0"
  },
  ...
}
```

#### `get_pod_status`

Get the status of a pod or all pods.

**Parameters:**
- `name` (string, optional): Name of the pod. If not provided, returns status of all pods.
- `namespace` (string, optional): Namespace of the pod. If not provided, uses the default namespace.

**Returns:**
JSON string with the pod status.

**Example:**
```json
{
  "example-pod": {
    "name": "example-pod",
    "namespace": "default",
    "phase": "Running",
    "conditions": [...],
    "containerStatuses": [...],
    "podIP": "10.0.0.1",
    "hostIP": "192.168.1.1",
    "startTime": "2025-04-01T12:00:00Z",
    "qosClass": "Guaranteed"
  },
  ...
}
```

#### `get_deployment_status`

Get the status of a deployment or all deployments.

**Parameters:**
- `name` (string, optional): Name of the deployment. If not provided, returns status of all deployments.
- `namespace` (string, optional): Namespace of the deployment. If not provided, uses the default namespace.

**Returns:**
JSON string with the deployment status.

**Example:**
```json
{
  "example-deployment": {
    "name": "example-deployment",
    "namespace": "default",
    "replicas": 3,
    "availableReplicas": 3,
    "unavailableReplicas": 0,
    "updatedReplicas": 3,
    "readyReplicas": 3,
    "conditions": [...],
    "strategy": "RollingUpdate",
    "minReadySeconds": 0,
    "revisionHistoryLimit": 10
  },
  ...
}
```

#### `get_resource_metrics`

Get metrics for a specific resource.

**Parameters:**
- `kind` (string, required): Kind of the resource (e.g., "Pod", "Node").
- `name` (string, required): Name of the resource.
- `namespace` (string, optional): Namespace of the resource. If not provided, uses the default namespace.

**Returns:**
JSON string with the resource metrics.

**Example:**
```json
{
  "timestamp": "2025-04-01T12:00:00Z",
  "window": "30s",
  "containers": {
    "example-container": {
      "cpu": {
        "raw": "100m",
        "millicores": 100
      },
      "memory": {
        "raw": "256Mi",
        "mib": 256
      }
    }
  }
}
```

#### `check_cluster_health`

Perform a comprehensive health check of the Kubernetes cluster.

**Parameters:**
None

**Returns:**
JSON string with the cluster health summary.

**Example:**
```json
{
  "timestamp": 1712047200,
  "overall_status": "Healthy",
  "health_scores": {
    "nodes": {
      "percentage": 100,
      "ready": 3,
      "total": 3
    },
    "pods": {
      "percentage": 100,
      "running": 10,
      "total": 10,
      "pending": 0,
      "failed": 0
    },
    "deployments": {
      "percentage": 100,
      "available": 5,
      "total": 5
    }
  },
  "issues": {
    "nodes": [],
    "pods": [],
    "deployments": []
  },
  "recommendations": [],
  "assessment": "The cluster appears to be healthy with all components functioning properly."
}
```

## MCP Prompts

The MCP Kubernetes Server provides the following prompt templates for common Kubernetes analysis tasks:

### `analyze_cluster_status`

Create a prompt for analyzing cluster status.

**Parameters:**
- `context` (string, optional): Optional context information.

**Returns:**
List of prompt messages.

### `troubleshoot_pod_issues`

Create a prompt for troubleshooting pod issues.

**Parameters:**
- `context` (string, optional): Optional context information.

**Returns:**
List of prompt messages.

### `analyze_resource_usage`

Create a prompt for analyzing resource usage.

**Parameters:**
- `context` (string, optional): Optional context information.

**Returns:**
List of prompt messages.

### `security_assessment`

Create a prompt for security assessment.

**Parameters:**
- `context` (string, optional): Optional context information.

**Returns:**
List of prompt messages.

### `performance_optimization`

Create a prompt for performance optimization.

**Parameters:**
- `context` (string, optional): Optional context information.

**Returns:**
List of prompt messages.

### `cost_optimization`

Create a prompt for cost optimization.

**Parameters:**
- `context` (string, optional): Optional context information.

**Returns:**
List of prompt messages.

## MCP Resources

The MCP Kubernetes Server exposes the following resources that can be accessed by MCP clients:

### Resource URIs

The following resource URIs are available:

- `k8s://namespaces/{namespace}`: Kubernetes namespace and all resources in it.
- `k8s://nodes/{name}`: Kubernetes node.
- `k8s://persistentvolumes/{name}`: Kubernetes persistent volume.
- `k8s://namespaces/{namespace}/pods/{name}`: Kubernetes pod in a namespace.
- `k8s://namespaces/{namespace}/deployments/{name}`: Kubernetes deployment in a namespace.
- `k8s://namespaces/{namespace}/services/{name}`: Kubernetes service in a namespace.
- `k8s://namespaces/{namespace}/persistentvolumeclaims/{name}`: Kubernetes persistent volume claim in a namespace.

### Resource Content

The content of the resources is returned as JSON strings with detailed information about the Kubernetes resources.
