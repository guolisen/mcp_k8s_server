"""
Kubernetes status detection tools for the MCP server.
Provides tools for checking the health and status of Kubernetes clusters.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from mcp.server.lowlevel import Server
from mcp.types import (
    CallToolResult,
    CallToolRequest,
    TextContent,
    Tool,
)

from ..k8s.api_client import KubernetesApiClient
from ..k8s.kubectl import KubectlWrapper

logger = logging.getLogger(__name__)

class KubernetesStatus:
    """Handler for Kubernetes status detection tools."""
    
    def __init__(self, server: Server, api_client: KubernetesApiClient, kubectl_wrapper: KubectlWrapper):
        """
        Initialize the Kubernetes status detection tools.
        
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
        """Register all status detection tools."""
        self._register_check_component_status_tool()
        self._register_check_node_health_tool()
        self._register_check_deployment_health_tool()
        self._register_check_api_server_health_tool()
        self._register_check_resource_quotas_tool()
        self._register_run_cluster_diagnostics_tool()
    
    def _register_check_component_status_tool(self) -> None:
        """Register the check_component_status tool."""
        # Register the handler for the CallToolRequest
        self.server.request_handlers[CallToolRequest] = self._handle_tool_request
    
    def _handle_check_component_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a check_component_status tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the component status information.
        """
        try:
            # Try using componentstatus (may not be available in newer K8s versions)
            component_statuses = []
            try:
                component_statuses = self.kubectl_wrapper.get_component_statuses()
            except Exception as e:
                logger.warning(f"Could not get componentstatuses: {e}")
            
            # If componentstatus failed, check with the health endpoint
            if not component_statuses:
                health = self.api_client.get_cluster_health()
                
                output = "Cluster Component Status:\n\n"
                
                if health["components"]:
                    for component, status in health["components"].items():
                        status_emoji = "✅" if status == "Healthy" else "⚠️" if status == "Degraded" else "❌"
                        output += f"{status_emoji} {component}: {status}\n"
                else:
                    output += "Could not retrieve detailed component status.\n"
                    output += f"Overall cluster status: {health['status']}\n"
                    
                    if health["issues"]:
                        output += "\nIssues:\n"
                        for issue in health["issues"]:
                            output += f"- {issue}\n"
            else:
                # Format the componentstatus output
                output = "Cluster Component Status:\n\n"
                
                for component in component_statuses:
                    name = component.get("metadata", {}).get("name", "Unknown")
                    conditions = component.get("conditions", [])
                    
                    if conditions:
                        status = next((c.get("status") for c in conditions if c.get("type") == "Healthy"), "Unknown")
                        message = next((c.get("message") for c in conditions if c.get("type") == "Healthy"), "")
                        status_emoji = "✅" if status == "True" else "❌"
                        output += f"{status_emoji} {name}: {status}\n"
                        if message:
                            output += f"   Message: {message}\n"
                    else:
                        output += f"⚠️ {name}: No health information available\n"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error checking component status: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error checking component status: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_check_node_health_tool(self) -> None:
        """Register the check_node_health tool."""
        # No need to register separately, all tool calls are handled by _handle_tool_request
        pass
    
    def _handle_check_node_health(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a check_node_health tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the node health information.
        """
        try:
            node_name = arguments.get("node_name")
            
            # Get all nodes
            nodes = self.api_client.get_nodes()
            
            if node_name:
                # Filter to the specific node
                nodes = [node for node in nodes if node["name"] == node_name]
                
                if not nodes:
                    return CallToolResult(
                        content=[
                            ToolContent(
                                type="text",
                                text=f"Node not found: {node_name}"
                            )
                        ],
                        is_error=True
                    )
            
            # Format output
            output = "Node Health Status:\n\n"
            
            for node in nodes:
                ready_condition = "Ready" if node["status"] == "Ready" else "NotReady"
                status_emoji = "✅" if ready_condition == "Ready" else "❌"
                
                output += f"{status_emoji} Node: {node['name']}\n"
                output += f"   Status: {node['status']}\n"
                output += f"   Roles: {', '.join(node['roles'])}\n"
                output += f"   Kubelet Version: {node['kubelet_version']}\n"
                output += f"   OS: {node['os_image']}\n"
                output += f"   Internal IP: {node['internal_ip']}\n"
                
                if node['external_ip']:
                    output += f"   External IP: {node['external_ip']}\n"
                
                output += "   Conditions:\n"
                for condition_type, status in node["conditions"].items():
                    condition_emoji = "✅" if status == "True" else "❌"
                    output += f"      {condition_emoji} {condition_type}: {status}\n"
                
                if node["taints"]:
                    output += "   Taints:\n"
                    for taint in node["taints"]:
                        output += f"      - {taint['key']}={taint['value']}:{taint['effect']}\n"
                
                output += f"   CPU Capacity: {node['cpu_capacity']}\n"
                output += f"   Memory Capacity: {node['memory_capacity']}\n"
                output += f"   Pod Capacity: {node['pods_capacity']}\n"
                output += "\n"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error checking node health: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error checking node health: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_check_deployment_health_tool(self) -> None:
        """Register the check_deployment_health tool."""
        # No need to register separately, all tool calls are handled by _handle_tool_request
        pass
    
    def _handle_check_deployment_health(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a check_deployment_health tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the deployment health information.
        """
        try:
            namespace = arguments.get("namespace")
            deployment_name = arguments.get("deployment_name")
            
            # Get deployments
            deployments = self.api_client.get_deployments(namespace)
            
            if deployment_name:
                # Filter to the specific deployment
                deployments = [dep for dep in deployments if dep["name"] == deployment_name]
                
                if not deployments:
                    namespace_str = f"in namespace {namespace}" if namespace else "in any namespace"
                    return CallToolResult(
                        content=[
                            ToolContent(
                                type="text",
                                text=f"Deployment not found: {deployment_name} {namespace_str}"
                            )
                        ],
                        is_error=True
                    )
            
            # Format output
            namespace_str = f"in namespace {namespace}" if namespace else "across all namespaces"
            deployment_str = f"for deployment {deployment_name}" if deployment_name else ""
            
            output = f"Deployment Health Status {namespace_str} {deployment_str}:\n\n"
            
            if not deployments:
                output += "No deployments found.\n"
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text=output
                        )
                    ]
                )
            
            unhealthy_deployments = []
            
            for dep in deployments:
                desired = dep["replicas"]
                available = dep["available_replicas"] if dep["available_replicas"] is not None else 0
                ready = dep["ready_replicas"] if dep["ready_replicas"] is not None else 0
                
                is_healthy = (available == desired) and (ready == desired)
                status_emoji = "✅" if is_healthy else "❌"
                
                if not is_healthy:
                    unhealthy_deployments.append(dep["name"])
                
                output += f"{status_emoji} Deployment: {dep['namespace']}/{dep['name']}\n"
                output += f"   Desired Replicas: {desired}\n"
                output += f"   Available Replicas: {available}\n"
                output += f"   Ready Replicas: {ready}\n"
                output += f"   Strategy: {dep['strategy']}\n"
                output += f"   Created: {dep['creation_timestamp']}\n"
                output += "\n"
            
            if unhealthy_deployments:
                output += f"⚠️ Found {len(unhealthy_deployments)} unhealthy deployments:\n"
                for dep_name in unhealthy_deployments:
                    output += f"   - {dep_name}\n"
            else:
                output += "✅ All deployments are healthy.\n"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error checking deployment health: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error checking deployment health: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_check_api_server_health_tool(self) -> None:
        """Register the check_api_server_health tool."""
        # No need to register separately, all tool calls are handled by _handle_tool_request
        pass
    
    def _handle_check_api_server_health(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a check_api_server_health tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the API server health information.
        """
        try:
            # Get cluster info
            cluster_info = self.kubectl_wrapper.get_cluster_info()
            
            # Check API server health via health endpoint
            health = self.api_client.get_cluster_health()
            api_server_health = health["components"].get("apiServer", "Unknown")
            
            # Format output
            output = "Kubernetes API Server Health:\n\n"
            
            status_emoji = "✅" if api_server_health == "Healthy" else "⚠️" if api_server_health == "Degraded" else "❌"
            output += f"{status_emoji} API Server Status: {api_server_health}\n\n"
            
            # Add cluster info
            output += "Cluster Information:\n"
            output += cluster_info
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error checking API server health: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error checking API server health: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_check_resource_quotas_tool(self) -> None:
        """Register the check_resource_quotas tool."""
        # No need to register separately, all tool calls are handled by _handle_tool_request
        pass
    
    def _handle_check_resource_quotas(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a check_resource_quotas tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the resource quota information.
        """
        try:
            namespace = arguments.get("namespace")
            
            # Get resource quotas
            quotas = self.api_client.get_resource_quotas(namespace)
            
            # Format output
            namespace_str = f"in namespace {namespace}" if namespace else "across all namespaces"
            
            output = f"Resource Quotas {namespace_str}:\n\n"
            
            if not quotas:
                output += "No resource quotas found.\n"
                return CallToolResult(
                    content=[
                        ToolContent(
                            type="text",
                            text=output
                        )
                    ]
                )
            
            for quota in quotas:
                output += f"Quota: {quota['namespace']}/{quota['name']}\n"
                
                if quota["hard"]:
                    output += "   Hard Limits:\n"
                    for resource, limit in quota["hard"].items():
                        output += f"      - {resource}: {limit}\n"
                
                if quota["used"]:
                    output += "   Usage:\n"
                    for resource, usage in quota["used"].items():
                        # Get the corresponding hard limit, if available
                        hard_limit = quota["hard"].get(resource, "N/A")
                        usage_str = f"{usage} / {hard_limit}" if hard_limit != "N/A" else usage
                        
                        output += f"      - {resource}: {usage_str}\n"
                
                output += "\n"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error checking resource quotas: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error checking resource quotas: {str(e)}"
                    )
                ],
                is_error=True
            )
    
    def _register_run_cluster_diagnostics_tool(self) -> None:
        """Register the run_cluster_diagnostics tool."""
        # No need to register separately, all tool calls are handled by _handle_tool_request
        pass
        
    def _handle_tool_request(self, request):
        """
        Handle a tool request.
        
        Args:
            request: The tool request.
            
        Returns:
            The result of the tool call.
        """
        tool_name = request["params"]["name"]
        arguments = request["params"]["arguments"]
        
        # Route to the appropriate handler based on the tool name
        if tool_name == "check_component_status":
            return self._handle_check_component_status(arguments)
        elif tool_name == "check_node_health":
            return self._handle_check_node_health(arguments)
        elif tool_name == "check_deployment_health":
            return self._handle_check_deployment_health(arguments)
        elif tool_name == "check_api_server_health":
            return self._handle_check_api_server_health(arguments)
        elif tool_name == "check_resource_quotas":
            return self._handle_check_resource_quotas(arguments)
        elif tool_name == "run_cluster_diagnostics":
            return self._handle_run_cluster_diagnostics(arguments)
        else:
            logger.error(f"Unknown tool: {tool_name}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Unknown tool: {tool_name}"
                    )
                ],
                is_error=True
            )
    
    def _handle_run_cluster_diagnostics(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Handle a run_cluster_diagnostics tool call.
        
        Args:
            arguments: The tool arguments.
        
        Returns:
            CallToolResult with the diagnostics results.
        """
        try:
            # Get timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Start with overall cluster health
            health = self.api_client.get_cluster_health()
            
            # Format output
            output = f"Kubernetes Cluster Diagnostics Report\n"
            output += f"Generated at: {timestamp}\n"
            output += f"==================================\n\n"
            
            # 1. Overall Health
            status_emoji = "✅" if health["status"] == "Healthy" else "⚠️" if health["status"] == "Degraded" else "❌"
            output += f"1. Overall Cluster Health: {status_emoji} {health['status']}\n\n"
            
            if health["issues"]:
                output += "   Issues Detected:\n"
                for issue in health["issues"]:
                    output += f"   - {issue}\n"
                output += "\n"
            
            # 2. API Server Health
            api_server_health = health["components"].get("apiServer", "Unknown")
            status_emoji = "✅" if api_server_health == "Healthy" else "⚠️" if api_server_health == "Degraded" else "❌"
            output += f"2. API Server: {status_emoji} {api_server_health}\n\n"
            
            # 3. Node Health
            nodes = self.api_client.get_nodes()
            ready_nodes = [n for n in nodes if n["status"] == "Ready"]
            not_ready_nodes = [n for n in nodes if n["status"] != "Ready"]
            
            node_health = "Healthy" if len(not_ready_nodes) == 0 else "Degraded"
            status_emoji = "✅" if node_health == "Healthy" else "⚠️"
            
            output += f"3. Node Health: {status_emoji} {node_health}\n"
            output += f"   - Total Nodes: {len(nodes)}\n"
            output += f"   - Ready Nodes: {len(ready_nodes)}\n"
            output += f"   - Not Ready Nodes: {len(not_ready_nodes)}\n"
            
            if not_ready_nodes:
                output += "   Not Ready Node Details:\n"
                for node in not_ready_nodes:
                    output += f"   - {node['name']}\n"
                    for condition_type, status in node["conditions"].items():
                        if status != "True" and condition_type != "Ready":
                            output += f"     {condition_type}: {status}\n"
            
            output += "\n"
            
            # 4. Deployment Health
            deployments = self.api_client.get_deployments()
            healthy_deployments = []
            unhealthy_deployments = []
            
            for dep in deployments:
                desired = dep["replicas"]
                available = dep["available_replicas"] if dep["available_replicas"] is not None else 0
                ready = dep["ready_replicas"] if dep["ready_replicas"] is not None else 0
                
                if (available == desired) and (ready == desired):
                    healthy_deployments.append(dep)
                else:
                    unhealthy_deployments.append(dep)
            
            deployment_health = "Healthy" if len(unhealthy_deployments) == 0 else "Degraded"
            status_emoji = "✅" if deployment_health == "Healthy" else "⚠️"
            
            output += f"4. Deployment Health: {status_emoji} {deployment_health}\n"
            output += f"   - Total Deployments: {len(deployments)}\n"
            output += f"   - Healthy Deployments: {len(healthy_deployments)}\n"
            output += f"   - Unhealthy Deployments: {len(unhealthy_deployments)}\n"
            
            if unhealthy_deployments:
                output += "   Unhealthy Deployment Details:\n"
                for dep in unhealthy_deployments:
                    output += f"   - {dep['namespace']}/{dep['name']}\n"
                    output += f"     Desired: {dep['replicas']}, "
                    output += f"Available: {dep['available_replicas'] or 0}, "
                    output += f"Ready: {dep['ready_replicas'] or 0}\n"
            
            output += "\n"
            
            # 5. Recent Events (only warnings and errors)
            events = self.api_client.get_events()
            # Sort events by timestamp (newest first)
            events.sort(key=lambda e: e.get("last_timestamp", ""), reverse=True)
            # Filter to only warnings and errors
            warning_events = [e for e in events if e.get("type") != "Normal"]
            
            output += f"5. Recent Warning Events (Last 10):\n"
            
            if not warning_events:
                output += "   No warning events found.\n"
            else:
                for event in warning_events[:10]:
                    event_time = event.get("last_timestamp") or event.get("first_timestamp") or event.get("creation_timestamp", "Unknown")
                    reason = event.get("reason", "")
                    obj_kind = event.get("involved_object", {}).get("kind", "")
                    obj_name = event.get("involved_object", {}).get("name", "")
                    message = event.get("message", "")
                    
                    output += f"   ⚠️ [{event_time}] {reason} ({obj_kind}/{obj_name}): {message}\n"
            
            output += "\n"
            
            # 6. Resource Usage
            output += f"6. Resource Usage Summary:\n"
            output += "   See detailed resource usage with the get_resource_usage and get_pod_resource_usage tools.\n\n"
            
            # 7. Recommendations
            output += f"7. Recommendations:\n"
            
            if not_ready_nodes:
                output += "   - Check the status of not ready nodes with 'check_node_health'\n"
            
            if unhealthy_deployments:
                output += "   - Investigate unhealthy deployments with 'check_deployment_health'\n"
                output += "   - Check deployment logs with 'get_logs'\n"
            
            if warning_events:
                output += "   - Review warning events with 'get_events'\n"
            
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=output
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error running cluster diagnostics: {e}")
            return CallToolResult(
                content=[
                    ToolContent(
                        type="text",
                        text=f"Error running cluster diagnostics: {str(e)}"
                    )
                ],
                is_error=True
            )
