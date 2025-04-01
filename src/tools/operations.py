"""
Kubernetes operations tools for the MCP server.
Provides tools for managing Kubernetes resources.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from modelcontextprotocol.sdk.server import Server
from modelcontextprotocol.sdk.types import (
    CallToolResult,
    ToolContent,
    ToolDefinition,
    ToolParameterDefinition,
)

from ..k8s.api_client import KubernetesApiClient
from ..k8s.kubectl import KubectlWrapper

logger = logging.getLogger(__name__)

class KubernetesOperations:
    """Handler for Kubernetes operations tools."""
    
    def __init__(self, server: Server, api_client: KubernetesApiClient, kubectl_wrapper: KubectlWrapper):
        """
        Initialize the Kubernetes operations tools.
        
        Args:
            server: The MCP server instance.
            api_client: The Kubernetes API client.
            kubectl_wrapper: The kubectl wrapper.
        """
        self.server = server
        self.api_client = api_client
        self.kubectl_wrapper = kubectl_wrapper
        self.register_tools()
    
    def register_tools(self) -> None:
        """Register all operations tools."""
        self._register_scale_deployment_tool()
        self._register_restart_deployment_tool()
        self._register_create_namespace_tool()
        self._register_delete_resource_tool()
        self._register_get_logs_tool()
        self._register_exec_command_tool()
    
    def _register_scale_deployment_tool(self) -> None:
        """Register the scale_deployment tool."""
        self.server.tools.append(
            ToolDefinition(
                name="scale_deployment",
                description="Scale a Kubernetes deployment to a specified number of replicas",
                input_schema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Namespace of the deployment"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the deployment"
                        },
                        "replicas": {
                            "type": "integer",
                            "description": "Number of replicas to scale to",
                            "minimum": 0
                        }
                    },
                    "required": ["namespace", "name", "replicas"]
                }
            )
        )
        
        self.server.register_tool("scale_deployment", self._handle_scale_deployment)
    
    def _handle_scale_deployment(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a scale_deployment tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the result of the operation.
        """
        try:
            namespace = arguments.get("namespace")
            name = arguments.get("name")
            replicas = arguments.get("replicas")
            
            if not all([namespace, name, isinstance(replicas, int)]):
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text="Missing or invalid arguments. Required: namespace (string), name (string), replicas (integer)"
                        )
                    ],
                    is_error=True
                )
            
            # Scale the deployment
            result = self.kubectl_wrapper.scale_deployment(name, replicas, namespace)
            
            # Get the updated deployment
            deployments = self.api_client.get_deployments(namespace)
            deployment = next((d for d in deployments if d["name"] == name), None)
            
            if not deployment:
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text=f"Deployment scaled, but could not verify the current state. Original result: {result}"
                        )
                    ]
                )
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Successfully scaled deployment {namespace}/{name} to {replicas} replicas.\n\n"
                             f"Current status:\n"
                             f"- Desired replicas: {deployment['replicas']}\n"
                             f"- Available replicas: {deployment['available_replicas'] or 0}\n"
                             f"- Ready replicas: {deployment['ready_replicas'] or 0}\n"
                             f"- Updated replicas: {deployment['updated_replicas'] or 0}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error scaling deployment: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error scaling deployment: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_restart_deployment_tool(self) -> None:
        """Register the restart_deployment tool."""
        self.server.tools.append(
            ToolDefinition(
                name="restart_deployment",
                description="Restart a Kubernetes deployment",
                input_schema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Namespace of the deployment"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the deployment"
                        }
                    },
                    "required": ["namespace", "name"]
                }
            )
        )
        
        self.server.register_tool("restart_deployment", self._handle_restart_deployment)
    
    def _handle_restart_deployment(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a restart_deployment tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the result of the operation.
        """
        try:
            namespace = arguments.get("namespace")
            name = arguments.get("name")
            
            if not all([namespace, name]):
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text="Missing or invalid arguments. Required: namespace (string), name (string)"
                        )
                    ],
                    is_error=True
                )
            
            # Restart the deployment
            result = self.kubectl_wrapper.restart_deployment(name, namespace)
            
            # Get rollout status
            status = self.kubectl_wrapper.get_rollout_status("deployment", name, namespace)
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Successfully restarted deployment {namespace}/{name}.\n\n"
                             f"Rollout status:\n{status}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error restarting deployment: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error restarting deployment: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_create_namespace_tool(self) -> None:
        """Register the create_namespace tool."""
        self.server.tools.append(
            ToolDefinition(
                name="create_namespace",
                description="Create a new Kubernetes namespace",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the namespace to create"
                        }
                    },
                    "required": ["name"]
                }
            )
        )
        
        self.server.register_tool("create_namespace", self._handle_create_namespace)
    
    def _handle_create_namespace(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a create_namespace tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the result of the operation.
        """
        try:
            name = arguments.get("name")
            
            if not name:
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text="Missing or invalid arguments. Required: name (string)"
                        )
                    ],
                    is_error=True
                )
            
            # Create the namespace
            result = self.kubectl_wrapper.create_namespace(name)
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Successfully created namespace {name}."
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error creating namespace: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error creating namespace: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_delete_resource_tool(self) -> None:
        """Register the delete_resource tool."""
        self.server.tools.append(
            ToolDefinition(
                name="delete_resource",
                description="Delete a Kubernetes resource",
                input_schema={
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Type of resource to delete (e.g., pod, deployment, service)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the resource to delete"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Namespace of the resource (not required for cluster-scoped resources)"
                        }
                    },
                    "required": ["resource_type", "name"]
                }
            )
        )
        
        self.server.register_tool("delete_resource", self._handle_delete_resource)
    
    def _handle_delete_resource(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a delete_resource tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the result of the operation.
        """
        try:
            resource_type = arguments.get("resource_type")
            name = arguments.get("name")
            namespace = arguments.get("namespace")
            
            if not all([resource_type, name]):
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text="Missing or invalid arguments. Required: resource_type (string), name (string)"
                        )
                    ],
                    is_error=True
                )
            
            # Delete the resource
            result = self.kubectl_wrapper.delete_resource(resource_type, name, namespace)
            
            namespace_str = f"in namespace {namespace}" if namespace else ""
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Successfully deleted {resource_type} {name} {namespace_str}."
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error deleting resource: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error deleting resource: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_get_logs_tool(self) -> None:
        """Register the get_logs tool."""
        self.server.tools.append(
            ToolDefinition(
                name="get_logs",
                description="Get logs from a Kubernetes pod",
                input_schema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Namespace of the pod"
                        },
                        "pod_name": {
                            "type": "string",
                            "description": "Name of the pod"
                        },
                        "container_name": {
                            "type": "string",
                            "description": "Name of the container (optional, only needed for multi-container pods)"
                        },
                        "tail": {
                            "type": "integer",
                            "description": "Number of lines to show from the end of the logs (optional)",
                            "minimum": 1
                        }
                    },
                    "required": ["namespace", "pod_name"]
                }
            )
        )
        
        self.server.register_tool("get_logs", self._handle_get_logs)
    
    def _handle_get_logs(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a get_logs tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the result of the operation.
        """
        try:
            namespace = arguments.get("namespace")
            pod_name = arguments.get("pod_name")
            container_name = arguments.get("container_name")
            tail = arguments.get("tail")
            
            if not all([namespace, pod_name]):
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text="Missing or invalid arguments. Required: namespace (string), pod_name (string)"
                        )
                    ],
                    is_error=True
                )
            
            # Get the logs
            logs = self.kubectl_wrapper.get_logs(pod_name, container_name, tail, namespace)
            
            container_str = f" (container: {container_name})" if container_name else ""
            tail_str = f" (last {tail} lines)" if tail else ""
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Logs for pod {namespace}/{pod_name}{container_str}{tail_str}:\n\n{logs}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error getting logs: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_exec_command_tool(self) -> None:
        """Register the exec_command tool."""
        self.server.tools.append(
            ToolDefinition(
                name="exec_command",
                description="Execute a command in a Kubernetes pod",
                input_schema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Namespace of the pod"
                        },
                        "pod_name": {
                            "type": "string",
                            "description": "Name of the pod"
                        },
                        "container_name": {
                            "type": "string",
                            "description": "Name of the container (optional, only needed for multi-container pods)"
                        },
                        "command": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Command to execute and its arguments"
                        }
                    },
                    "required": ["namespace", "pod_name", "command"]
                }
            )
        )
        
        self.server.register_tool("exec_command", self._handle_exec_command)
    
    def _handle_exec_command(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle an exec_command tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the result of the operation.
        """
        try:
            namespace = arguments.get("namespace")
            pod_name = arguments.get("pod_name")
            container_name = arguments.get("container_name")
            command = arguments.get("command")
            
            if not all([namespace, pod_name, command]) or not isinstance(command, list):
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text="Missing or invalid arguments. Required: namespace (string), pod_name (string), command (array of strings)"
                        )
                    ],
                    is_error=True
                )
            
            # Execute the command
            result = self.kubectl_wrapper.exec_command_in_pod(pod_name, container_name, command, namespace)
            
            container_str = f" (container: {container_name})" if container_name else ""
            command_str = " ".join(command)
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Command executed in pod {namespace}/{pod_name}{container_str}: {command_str}\n\n"
                             f"Result:\n{result}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error executing command: {str(e)}"
                    )
                ],
                is_error=True
            )
