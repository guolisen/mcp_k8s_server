#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: MCP tools for Kubernetes resource information.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json, datetime
import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_k8s_server.k8s.client import K8sClient

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def register_resource_tools(mcp: FastMCP, k8s_client: K8sClient) -> None:
    """Register resource information tools with the MCP server.
    
    Args:
        mcp: MCP server.
        k8s_client: Kubernetes client.
    """
    
    @mcp.tool()
    def get_resources(resource_type: str, namespace: Optional[str] = None) -> str:
        """Get a list of resources of a specific type.
        
        Args:
            resource_type: Type of resource (pods, deployments, services, etc.).
            namespace: Namespace to get resources from. If None, uses the default namespace.
                       Use "all" to get resources from all namespaces.
        
        Returns:
            JSON string with the list of resources.
        """
        logger.info(f"Getting {resource_type} in namespace {namespace}")
        
        try:
            resources = []
            
            if resource_type == "pods":
                resources = k8s_client.get_pods(namespace)
            elif resource_type == "deployments":
                resources = k8s_client.get_deployments(namespace)
            elif resource_type == "services":
                resources = k8s_client.get_services(namespace)
            elif resource_type == "nodes":
                resources = k8s_client.get_nodes()
            elif resource_type == "namespaces":
                resources = k8s_client.get_namespaces()
            elif resource_type == "persistentvolumes":
                resources = k8s_client.get_persistent_volumes()
            elif resource_type == "persistentvolumeclaims":
                resources = k8s_client.get_persistent_volume_claims(namespace)
            elif resource_type == "events":
                resources = k8s_client.get_events(namespace)
            else:
                return json.dumps({"error": f"Unsupported resource type: {resource_type}"})
            
            return json.dumps(resources, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting {resource_type}: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_resource(resource_type: str, name: str, namespace: Optional[str] = None) -> str:
        """Get detailed information about a specific resource.
        
        Args:
            resource_type: Type of resource (pod, deployment, service, etc.).
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            JSON string with the resource information.
        """
        logger.info(f"Getting {resource_type} {name} in namespace {namespace}")
        
        try:
            resource = None
            
            if resource_type == "pod":
                resource = k8s_client.get_pod(name, namespace)
            elif resource_type == "deployment":
                resource = k8s_client.get_deployment(name, namespace)
            elif resource_type == "service":
                resource = k8s_client.get_service(name, namespace)
            elif resource_type == "node":
                resource = k8s_client.get_node(name)
            elif resource_type == "persistentvolume":
                resource = k8s_client.get_persistent_volume(name)
            elif resource_type == "persistentvolumeclaim":
                resource = k8s_client.get_persistent_volume_claim(name, namespace)
            else:
                return json.dumps({"error": f"Unsupported resource type: {resource_type}"})
            
            if resource is None:
                return json.dumps({"error": f"{resource_type} {name} not found"})
            
            return json.dumps(resource, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting {resource_type} {name}: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_resource_status(resource_type: str, name: str, namespace: Optional[str] = None) -> str:
        """Get the status of a specific resource.
        
        Args:
            resource_type: Type of resource (pod, deployment, service, etc.).
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            JSON string with the resource status.
        """
        logger.info(f"Getting status of {resource_type} {name} in namespace {namespace}")
        
        try:
            resource = None
            
            if resource_type == "pod":
                resource = k8s_client.get_pod(name, namespace)
            elif resource_type == "deployment":
                resource = k8s_client.get_deployment(name, namespace)
            elif resource_type == "service":
                resource = k8s_client.get_service(name, namespace)
            elif resource_type == "node":
                resource = k8s_client.get_node(name)
            elif resource_type == "persistentvolume":
                resource = k8s_client.get_persistent_volume(name)
            elif resource_type == "persistentvolumeclaim":
                resource = k8s_client.get_persistent_volume_claim(name, namespace)
            else:
                return json.dumps({"error": f"Unsupported resource type: {resource_type}"})
            
            if resource is None:
                return json.dumps({"error": f"{resource_type} {name} not found"})
            
            # Extract status from the resource
            status = resource.get("status", {})
            
            return json.dumps(status, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting status of {resource_type} {name}: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_resource_events(resource_type: str, name: str, namespace: Optional[str] = None) -> str:
        """Get events related to a specific resource.
        
        Args:
            resource_type: Type of resource (pod, deployment, service, etc.).
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            JSON string with the resource events.
        """
        logger.info(f"Getting events for {resource_type} {name} in namespace {namespace}")
        
        try:
            events = k8s_client.get_resource_events(resource_type, name, namespace)
            
            return json.dumps(events, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting events for {resource_type} {name}: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_pod_logs(name: str, namespace: Optional[str] = None, container: Optional[str] = None, 
                     tail_lines: int = 100) -> str:
        """Get logs for a pod.
        
        Args:
            name: Name of the pod.
            namespace: Namespace of the pod. If None, uses the default namespace.
            container: Name of the container. If None, uses the first container.
            tail_lines: Number of lines to return from the end of the logs.
        
        Returns:
            Pod logs.
        """
        logger.info(f"Getting logs for pod {name} in namespace {namespace}")
        
        try:
            logs = k8s_client.get_pod_logs(name, namespace, container, tail_lines)
            
            return logs
        except Exception as e:
            logger.error(f"Error getting logs for pod {name}: {e}")
            return f"Error getting logs: {e}"
