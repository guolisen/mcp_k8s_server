"""
Kubernetes monitoring tools for the MCP server.
Provides tools for monitoring Kubernetes cluster status.
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

class KubernetesMonitoring:
    """Handler for Kubernetes monitoring tools."""
    
    def __init__(self, server: Server, api_client: KubernetesApiClient, kubectl_wrapper: KubectlWrapper):
        """
        Initialize the Kubernetes monitoring tools.
        
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
        """Register all monitoring tools."""
        self._register_get_cluster_health_tool()
        self._register_get_resource_usage_tool()
        self._register_get_pod_resource_usage_tool()
        self._register_get_events_tool()
        self._register_describe_resource_tool()
    
    def _register_get_cluster_health_tool(self) -> None:
        """Register the get_cluster_health tool."""
        self.server.tools.append(
            ToolDefinition(
                name="get_cluster_health",
                description="Get the overall health status of the Kubernetes cluster",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        )
        
        self.server.register_tool("get_cluster_health", self._handle_get_cluster_health)
    
    def _handle_get_cluster_health(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a get_cluster_health tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the health status of the cluster.
        """
        try:
            # Get cluster health
            health = self.api_client.get_cluster_health()
            
            # Format output
            status_emoji = "✅" if health["status"] == "Healthy" else "⚠️" if health["status"] == "Degraded" else "❌"
            
            # Start with the overall status
            output = f"{status_emoji} Cluster Status: {health['status']}\n\n"
            
            # Add component statuses
            if health["components"]:
                output += "Component Status:\n"
                for component, status in health["components"].items():
                    comp_emoji = "✅" if status == "Healthy" else "⚠️" if status == "Degraded" else "❌"
                    output += f"{comp_emoji} {component}: {status}\n"
                output += "\n"
            
            # Add node statuses
            if health["nodes"]:
                output += "Node Status:\n"
                for node, status in health["nodes"].items():
                    node_emoji = "✅" if status == "Ready" else "❌"
                    output += f"{node_emoji} {node}: {status}\n"
                output += "\n"
            
            # Add issues
            if health["issues"]:
                output += "Issues:\n"
                for issue in health["issues"]:
                    output += f"- {issue}\n"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error getting cluster health: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error getting cluster health: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_get_resource_usage_tool(self) -> None:
        """Register the get_resource_usage tool."""
        self.server.tools.append(
            ToolDefinition(
                name="get_resource_usage",
                description="Get resource usage (CPU, memory) across all nodes in the cluster",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        )
        
        self.server.register_tool("get_resource_usage", self._handle_get_resource_usage)
    
    def _handle_get_resource_usage(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a get_resource_usage tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the resource usage information.
        """
        try:
            # Get resource usage
            usage = self.kubectl_wrapper.get_resource_usage()
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Cluster Node Resource Usage:\n\n{usage}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error getting resource usage: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_get_pod_resource_usage_tool(self) -> None:
        """Register the get_pod_resource_usage tool."""
        self.server.tools.append(
            ToolDefinition(
                name="get_pod_resource_usage",
                description="Get resource usage (CPU, memory) for pods",
                input_schema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Namespace to filter pods (optional)"
                        }
                    },
                    "required": []
                }
            )
        )
        
        self.server.register_tool("get_pod_resource_usage", self._handle_get_pod_resource_usage)
    
    def _handle_get_pod_resource_usage(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a get_pod_resource_usage tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the pod resource usage information.
        """
        try:
            namespace = arguments.get("namespace")
            
            # Get pod resource usage
            usage = self.kubectl_wrapper.get_pod_resource_usage(namespace)
            
            namespace_str = f"in namespace {namespace}" if namespace else "across all namespaces"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Pod Resource Usage {namespace_str}:\n\n{usage}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error getting pod resource usage: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error getting pod resource usage: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_get_events_tool(self) -> None:
        """Register the get_events tool."""
        self.server.tools.append(
            ToolDefinition(
                name="get_events",
                description="Get Kubernetes events",
                input_schema={
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Namespace to filter events (optional)"
                        }
                    },
                    "required": []
                }
            )
        )
        
        self.server.register_tool("get_events", self._handle_get_events)
    
    def _handle_get_events(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a get_events tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the Kubernetes events.
        """
        try:
            namespace = arguments.get("namespace")
            
            # Get events
            events = self.api_client.get_events(namespace)
            
            # Sort events by timestamp (newest first)
            events.sort(key=lambda e: e.get("last_timestamp", ""), reverse=True)
            
            # Format output
            namespace_str = f"in namespace {namespace}" if namespace else "across all namespaces"
            
            if not events:
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text=f"No events found {namespace_str}."
                        )
                    ]
                )
            
            output = f"Recent Kubernetes Events {namespace_str}:\n\n"
            
            for event in events[:20]:  # Limit to 20 most recent events
                event_time = event.get("last_timestamp") or event.get("first_timestamp") or event.get("creation_timestamp", "Unknown")
                event_type = event.get("type", "Normal")
                reason = event.get("reason", "")
                obj_kind = event.get("involved_object", {}).get("kind", "")
                obj_name = event.get("involved_object", {}).get("name", "")
                message = event.get("message", "")
                
                type_emoji = "ℹ️" if event_type == "Normal" else "⚠️"
                
                output += f"{type_emoji} [{event_time}] {reason} ({obj_kind}/{obj_name}): {message}\n\n"
            
            if len(events) > 20:
                output += f"... and {len(events) - 20} more events."
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error getting events: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_describe_resource_tool(self) -> None:
        """Register the describe_resource tool."""
        self.server.tools.append(
            ToolDefinition(
                name="describe_resource",
                description="Get detailed description of a Kubernetes resource",
                input_schema={
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Type of resource to describe (e.g., pod, deployment, service)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the resource"
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
        
        self.server.register_tool("describe_resource", self._handle_describe_resource)
    
    def _handle_describe_resource(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a describe_resource tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the resource description.
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
            
            # Describe the resource
            description = self.kubectl_wrapper.describe_resource(resource_type, name, namespace)
            
            namespace_str = f"in namespace {namespace}" if namespace else ""
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Description of {resource_type} {name} {namespace_str}:\n\n{description}"
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error describing resource: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error describing resource: {str(e)}"
                    )
                ],
                is_error=True
            )
