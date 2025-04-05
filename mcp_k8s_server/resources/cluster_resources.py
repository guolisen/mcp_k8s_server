#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: MCP resources for Kubernetes cluster.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote, unquote

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource

from mcp_k8s_server.k8s.client import K8sClient

logger = logging.getLogger(__name__)


def register_cluster_resources(mcp: FastMCP, k8s_client: K8sClient) -> None:
    """Register cluster resources with the MCP server.
    
    Args:
        mcp: MCP server.
        k8s_client: Kubernetes client.
    """
    
    @mcp.list_resources()
    def list_resources() -> List[Resource]:
        """List all available resources.
        
        Returns:
            List of resources.
        """
        resources = []
        
        # Add namespace resources
        try:
            namespaces = k8s_client.get_namespaces()
            for namespace in namespaces:
                name = namespace["name"]
                resources.append(
                    Resource(
                        uri=f"k8s://namespaces/{name}",
                        name=f"Namespace: {name}",
                        description=f"Kubernetes namespace {name}",
                        mimeType="application/json",
                    )
                )
        except Exception as e:
            logger.error(f"Error listing namespaces: {e}")
        
        # Add node resources
        try:
            nodes = k8s_client.get_nodes()
            for node in nodes:
                name = node["name"]
                resources.append(
                    Resource(
                        uri=f"k8s://nodes/{name}",
                        name=f"Node: {name}",
                        description=f"Kubernetes node {name}",
                        mimeType="application/json",
                    )
                )
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
        
        # Add persistent volume resources
        try:
            pvs = k8s_client.get_persistent_volumes()
            for pv in pvs:
                name = pv["name"]
                resources.append(
                    Resource(
                        uri=f"k8s://persistentvolumes/{name}",
                        name=f"PersistentVolume: {name}",
                        description=f"Kubernetes persistent volume {name}",
                        mimeType="application/json",
                    )
                )
        except Exception as e:
            logger.error(f"Error listing persistent volumes: {e}")
        
        # Add namespace-specific resources
        try:
            namespaces = k8s_client.get_namespaces()
            for namespace in namespaces:
                ns_name = namespace["name"]
                
                # Add pod resources
                try:
                    pods = k8s_client.get_pods(namespace=ns_name)
                    for pod in pods:
                        name = pod["name"]
                        resources.append(
                            Resource(
                                uri=f"k8s://namespaces/{ns_name}/pods/{name}",
                                name=f"Pod: {name} (ns: {ns_name})",
                                description=f"Kubernetes pod {name} in namespace {ns_name}",
                                mimeType="application/json",
                            )
                        )
                except Exception as e:
                    logger.error(f"Error listing pods in namespace {ns_name}: {e}")
                
                # Add deployment resources
                try:
                    deployments = k8s_client.get_deployments(namespace=ns_name)
                    for deployment in deployments:
                        name = deployment["name"]
                        resources.append(
                            Resource(
                                uri=f"k8s://namespaces/{ns_name}/deployments/{name}",
                                name=f"Deployment: {name} (ns: {ns_name})",
                                description=f"Kubernetes deployment {name} in namespace {ns_name}",
                                mimeType="application/json",
                            )
                        )
                except Exception as e:
                    logger.error(f"Error listing deployments in namespace {ns_name}: {e}")
                
                # Add service resources
                try:
                    services = k8s_client.get_services(namespace=ns_name)
                    for service in services:
                        name = service["name"]
                        resources.append(
                            Resource(
                                uri=f"k8s://namespaces/{ns_name}/services/{name}",
                                name=f"Service: {name} (ns: {ns_name})",
                                description=f"Kubernetes service {name} in namespace {ns_name}",
                                mimeType="application/json",
                            )
                        )
                except Exception as e:
                    logger.error(f"Error listing services in namespace {ns_name}: {e}")
                
                # Add persistent volume claim resources
                try:
                    pvcs = k8s_client.get_persistent_volume_claims(namespace=ns_name)
                    for pvc in pvcs:
                        name = pvc["name"]
                        resources.append(
                            Resource(
                                uri=f"k8s://namespaces/{ns_name}/persistentvolumeclaims/{name}",
                                name=f"PersistentVolumeClaim: {name} (ns: {ns_name})",
                                description=f"Kubernetes persistent volume claim {name} in namespace {ns_name}",
                                mimeType="application/json",
                            )
                        )
                except Exception as e:
                    logger.error(f"Error listing persistent volume claims in namespace {ns_name}: {e}")
        except Exception as e:
            logger.error(f"Error processing namespaces: {e}")
        
        return resources
    
    @mcp.read_resource()
    def read_resource(uri: str) -> str:
        """Read a resource.
        
        Args:
            uri: Resource URI.
        
        Returns:
            Resource content.
        """
        logger.info(f"Reading resource: {uri}")
        
        # Parse the URI
        match = re.match(r"k8s://namespaces/([^/]+)/([^/]+)/([^/]+)$", uri)
        if match:
            namespace = unquote(match.group(1))
            resource_type = match.group(2)
            name = unquote(match.group(3))
            
            # Get the resource
            try:
                resource = None
                
                if resource_type == "pods":
                    resource = k8s_client.get_pod(name, namespace)
                elif resource_type == "deployments":
                    resource = k8s_client.get_deployment(name, namespace)
                elif resource_type == "services":
                    resource = k8s_client.get_service(name, namespace)
                elif resource_type == "persistentvolumeclaims":
                    resource = k8s_client.get_persistent_volume_claim(name, namespace)
                else:
                    return json.dumps({"error": f"Unsupported resource type: {resource_type}"})
                
                if resource is None:
                    return json.dumps({"error": f"{resource_type} {name} not found in namespace {namespace}"})
                
                return json.dumps(resource, indent=2)
            except Exception as e:
                logger.error(f"Error reading resource: {e}")
                return json.dumps({"error": str(e)})
        
        # Check for non-namespaced resources
        match = re.match(r"k8s://([^/]+)/([^/]+)$", uri)
        if match:
            resource_type = match.group(1)
            name = unquote(match.group(2))
            
            # Get the resource
            try:
                resource = None
                
                if resource_type == "nodes":
                    resource = k8s_client.get_node(name)
                elif resource_type == "persistentvolumes":
                    resource = k8s_client.get_persistent_volume(name)
                elif resource_type == "namespaces":
                    # Get all resources in the namespace
                    namespace_info = {}
                    
                    # Get namespace details
                    namespace = k8s_client.get_namespaces()
                    namespace_info["namespace"] = next((ns for ns in namespace if ns["name"] == name), {})
                    
                    # Get pods in the namespace
                    namespace_info["pods"] = k8s_client.get_pods(namespace=name)
                    
                    # Get deployments in the namespace
                    namespace_info["deployments"] = k8s_client.get_deployments(namespace=name)
                    
                    # Get services in the namespace
                    namespace_info["services"] = k8s_client.get_services(namespace=name)
                    
                    # Get persistent volume claims in the namespace
                    namespace_info["persistentvolumeclaims"] = k8s_client.get_persistent_volume_claims(namespace=name)
                    
                    resource = namespace_info
                else:
                    return json.dumps({"error": f"Unsupported resource type: {resource_type}"})
                
                if resource is None:
                    return json.dumps({"error": f"{resource_type} {name} not found"})
                
                return json.dumps(resource, indent=2)
            except Exception as e:
                logger.error(f"Error reading resource: {e}")
                return json.dumps({"error": str(e)})
        
        return json.dumps({"error": f"Invalid resource URI: {uri}"})
