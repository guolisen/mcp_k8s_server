#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: MCP tools for Kubernetes operations.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json, datetime
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_k8s_server.k8s.operations import K8sOperations

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
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
            
            return json.dumps(result, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
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
            
            return json.dumps(result, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
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
            
            return json.dumps(result, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
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
            
            return json.dumps(result, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
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
            
            return json.dumps(result, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error restarting deployment {name}: {e}")
            return json.dumps({"success": False, "message": str(e)})
    
    @mcp.tool()
    def execute_command_on_pod(pod_name: str = None, command: str = None, namespace: Optional[str] = None, 
                        container: Optional[str] = None, value: Any = None) -> str:
        """Execute a command in a pod
        
        NOTICE: this tool just run command in POD, not on host, if you want to run command on host please refer other mcp server tools.
        
        Args:
            pod_name: Name of the pod.
            command: Command to execute (as a string, will be split on spaces).
            namespace: Namespace of the pod. If None, uses the default namespace.
            container: Name of the container. If None, uses the first container.
            value: Alternative way to pass arguments for compatibility with some clients.
        
        Returns:
            JSON string with the result of the operation.
        """
        # Handle the case where arguments are passed as a single value instead of a dictionary
        if pod_name is None and value is not None:
            logger.warning(f"Received non-dictionary arguments: {value}, using default handling")
            # If value is an integer, it might be a client error
            if isinstance(value, int):
                return json.dumps({
                    "success": False, 
                    "message": f"Invalid arguments: expected dictionary with 'pod_name' and 'command', got integer {value}. Please provide proper arguments."
                }, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
            # If value is a string, assume it's a command to run
            elif isinstance(value, str):
                # We can't run the command without a pod name, so return an error
                return json.dumps({
                    "success": False, 
                    "message": f"Invalid arguments: missing 'pod_name'. Please provide proper arguments including pod_name and command."
                }, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        
        # Check required parameters
        if pod_name is None:
            return json.dumps({
                "success": False, 
                "message": "Missing required parameter: pod_name"
            }, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        
        if command is None:
            return json.dumps({
                "success": False, 
                "message": "Missing required parameter: command"
            }, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        
        logger.info(f"Executing command in pod {pod_name} in namespace {namespace}")
        
        try:
            # Split the command string into a list
            command_list = command.split()
            
            result = k8s_operations.execute_command(pod_name, command_list, namespace, container)
            
            return json.dumps(result, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error executing command in pod {pod_name}: {e}")
            return json.dumps({"success": False, "message": str(e)})
