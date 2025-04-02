"""MCP tools for Kubernetes operations."""

import json, datetime
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_k8s_server.k8s.operations import K8sOperations

logger = logging.getLogger(__name__)

class DatetimeEncode(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def register_operation_tools(mcp: FastMCP, k8s_operations: K8sOperations) -> None:
    """Register operation tools with the MCP server.
    
    Args:
        mcp: MCP server.
        k8s_operations: Kubernetes operations.
    """
    
    @mcp.tool()
    def create_resource(resource_yaml: str) -> str:
        """Create a resource from YAML.
        
        Args:
            resource_yaml: YAML representation of the resource.
        
        Returns:
            JSON string with the result of the operation.
        """
        logger.info("Creating resource")
        
        try:
            result = k8s_operations.create_resource(resource_yaml)
            
            return json.dumps(result, indent=2, cls=DatetimeEncode, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error creating resource: {e}")
            return json.dumps({"success": False, "message": str(e)})
    
    @mcp.tool()
    def update_resource(resource_yaml: str) -> str:
        """Update a resource from YAML.
        
        Args:
            resource_yaml: YAML representation of the resource.
        
        Returns:
            JSON string with the result of the operation.
        """
        logger.info("Updating resource")
        
        try:
            result = k8s_operations.update_resource(resource_yaml)
            
            return json.dumps(result, indent=2, cls=DatetimeEncode, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error updating resource: {e}")
            return json.dumps({"success": False, "message": str(e)})
    
    @mcp.tool()
    def delete_resource(resource_type: str, name: str, namespace: Optional[str] = None) -> str:
        """Delete a resource.
        
        Args:
            resource_type: Type of resource (pod, deployment, service, etc.).
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            JSON string with the result of the operation.
        """
        logger.info(f"Deleting {resource_type} {name} in namespace {namespace}")
        
        try:
            result = k8s_operations.delete_resource(resource_type, name, namespace)
            
            return json.dumps(result, indent=2, cls=DatetimeEncode, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error deleting {resource_type} {name}: {e}")
            return json.dumps({"success": False, "message": str(e)})
    
    @mcp.tool()
    def scale_deployment(name: str, replicas: int, namespace: Optional[str] = None) -> str:
        """Scale a deployment.
        
        Args:
            name: Name of the deployment.
            replicas: Number of replicas.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            JSON string with the result of the operation.
        """
        logger.info(f"Scaling deployment {name} to {replicas} replicas in namespace {namespace}")
        
        try:
            result = k8s_operations.scale_deployment(name, replicas, namespace)
            
            return json.dumps(result, indent=2, cls=DatetimeEncode, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error scaling deployment {name}: {e}")
            return json.dumps({"success": False, "message": str(e)})
    
    @mcp.tool()
    def restart_deployment(name: str, namespace: Optional[str] = None) -> str:
        """Restart a deployment.
        
        Args:
            name: Name of the deployment.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            JSON string with the result of the operation.
        """
        logger.info(f"Restarting deployment {name} in namespace {namespace}")
        
        try:
            result = k8s_operations.restart_deployment(name, namespace)
            
            return json.dumps(result, indent=2, cls=DatetimeEncode, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error restarting deployment {name}: {e}")
            return json.dumps({"success": False, "message": str(e)})
    
    @mcp.tool()
    def execute_command(pod_name: str, command: str, namespace: Optional[str] = None, 
                        container: Optional[str] = None) -> str:
        """Execute a command in a pod.
        
        Args:
            pod_name: Name of the pod.
            command: Command to execute (as a string, will be split on spaces).
            namespace: Namespace of the pod. If None, uses the default namespace.
            container: Name of the container. If None, uses the first container.
        
        Returns:
            JSON string with the result of the operation.
        """
        logger.info(f"Executing command in pod {pod_name} in namespace {namespace}")
        
        try:
            # Split the command string into a list
            command_list = command.split()
            
            result = k8s_operations.execute_command(pod_name, command_list, namespace, container)
            
            return json.dumps(result, indent=2, cls=DatetimeEncode, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error executing command in pod {pod_name}: {e}")
            return json.dumps({"success": False, "message": str(e)})
