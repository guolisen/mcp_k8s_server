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


class KubernetesResources:
    """Manager for Kubernetes resources as MCP resources."""
    
    def __init__(self, k8s_client: K8sClient):
        self.k8s_client = k8s_client
        
    def register_resources(self, mcp: FastMCP) -> None:
        """Register all Kubernetes resource templates and static resources."""
        
        # Resource list
        @mcp.resource("k8s://resources", 
                     name="Kubernetes Resources", 
                     description="List of all available Kubernetes resources",
                     mime_type="application/json")
        def list_resources() -> str:
            """List all available Kubernetes resources."""
            try:
                resources = []
                
                # Add namespace-level resources
                namespaces = []
                try:
                    namespaces = self.k8s_client.get_namespaces()
                    
                    # Add namespaces list resource
                    resources.append({
                        "uri": "k8s://namespaces",
                        "name": "Kubernetes Namespaces",
                        "type": "namespace_list",
                        "description": "List of all Kubernetes namespaces"
                    })
                    
                    for namespace in namespaces:
                        ns_name = namespace["name"]
                        
                        # Add namespace resource
                        resources.append({
                            "uri": f"k8s:///{ns_name}",
                            "name": f"Namespace: {ns_name}",
                            "type": "namespace",
                            "description": f"Resources in namespace {ns_name}"
                        })
                        
                        # Add resource type listings for this namespace
                        resources.append({
                            "uri": f"k8s://{ns_name}/pods",
                            "name": f"Pods in {ns_name}",
                            "type": "pod_list",
                            "description": f"List of pods in namespace {ns_name}"
                        })
                        
                        resources.append({
                            "uri": f"k8s://{ns_name}/deployments",
                            "name": f"Deployments in {ns_name}",
                            "type": "deployment_list",
                            "description": f"List of deployments in namespace {ns_name}"
                        })
                        
                        resources.append({
                            "uri": f"k8s://{ns_name}/services",
                            "name": f"Services in {ns_name}",
                            "type": "service_list",
                            "description": f"List of services in namespace {ns_name}"
                        })
                        
                        resources.append({
                            "uri": f"k8s://{ns_name}/persistentvolumeclaims",
                            "name": f"PVCs in {ns_name}",
                            "type": "pvc_list",
                            "description": f"List of persistent volume claims in namespace {ns_name}"
                        })
                        
                        # Add individual resources for this namespace
                        # Pods
                        pods = []
                        try:
                            pods = self.k8s_client.get_pods(namespace=ns_name)
                            for pod in pods:
                                resources.append({
                                    "uri": f"k8s://{ns_name}/pods/{pod['name']}",
                                    "name": f"Pod: {pod['name']}",
                                    "type": "pod",
                                    "description": f"Pod {pod['name']} in namespace {ns_name}"
                                })
                        except Exception as e:
                            logger.error(f"Error getting pods in namespace {ns_name}: {e}")
                        
                        # Deployments
                        deployments = []
                        try:
                            deployments = self.k8s_client.get_deployments(namespace=ns_name)
                            for deployment in deployments:
                                resources.append({
                                    "uri": f"k8s://{ns_name}/deployments/{deployment['name']}",
                                    "name": f"Deployment: {deployment['name']}",
                                    "type": "deployment",
                                    "description": f"Deployment {deployment['name']} in namespace {ns_name}"
                                })
                        except Exception as e:
                            logger.error(f"Error getting deployments in namespace {ns_name}: {e}")
                        
                        # Services
                        services = []
                        try:
                            services = self.k8s_client.get_services(namespace=ns_name)
                            for service in services:
                                resources.append({
                                    "uri": f"k8s://{ns_name}/services/{service['name']}",
                                    "name": f"Service: {service['name']}",
                                    "type": "service",
                                    "description": f"Service {service['name']} in namespace {ns_name}"
                                })
                        except Exception as e:
                            logger.error(f"Error getting services in namespace {ns_name}: {e}")
                        
                        # PVCs
                        pvcs = []
                        try:
                            pvcs = self.k8s_client.get_persistent_volume_claims(namespace=ns_name)
                            for pvc in pvcs:
                                resources.append({
                                    "uri": f"k8s://{ns_name}/persistentvolumeclaims/{pvc['name']}",
                                    "name": f"PVC: {pvc['name']}",
                                    "type": "pvc",
                                    "description": f"PersistentVolumeClaim {pvc['name']} in namespace {ns_name}"
                                })
                        except Exception as e:
                            logger.error(f"Error getting PVCs in namespace {ns_name}: {e}")
                except Exception as e:
                    logger.error(f"Error processing namespaces: {e}")
                
                # Add cluster-wide resources
                resources.append({
                    "uri": "k8s:///nodes",
                    "name": "Nodes",
                    "type": "node_list",
                    "description": "List of all Kubernetes nodes"
                })
                
                resources.append({
                    "uri": "k8s:///persistentvolumes",
                    "name": "PersistentVolumes",
                    "type": "pv_list",
                    "description": "List of all Kubernetes persistent volumes"
                })
                
                # Nodes
                nodes = []
                try:
                    nodes = self.k8s_client.get_nodes()
                    for node in nodes:
                        resources.append({
                            "uri": f"k8s:///nodes/{node['name']}",
                            "name": f"Node: {node['name']}",
                            "type": "node",
                            "description": f"Kubernetes node {node['name']}"
                        })
                except Exception as e:
                    logger.error(f"Error getting nodes: {e}")
                
                # PVs
                pvs = []
                try:
                    pvs = self.k8s_client.get_persistent_volumes()
                    for pv in pvs:
                        resources.append({
                            "uri": f"k8s:///persistentvolumes/{pv['name']}",
                            "name": f"PV: {pv['name']}",
                            "type": "pv",
                            "description": f"Kubernetes persistent volume {pv['name']}"
                        })
                except Exception as e:
                    logger.error(f"Error getting persistent volumes: {e}")
                
                return json.dumps(resources, indent=2)
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return json.dumps({"error": str(e)})
        
        # Namespace list
        @mcp.resource("k8s://namespaces", 
                     name="Kubernetes Namespaces", 
                     description="List of all Kubernetes namespaces",
                     mime_type="application/json")
        def list_namespaces() -> str:
            """List all Kubernetes namespaces."""
            try:
                namespaces = self.k8s_client.get_namespaces()
                return json.dumps(namespaces, indent=2)
            except Exception as e:
                logger.error(f"Error listing namespaces: {e}")
                return json.dumps({"error": str(e)})
        
        # List resources in a namespace
        @mcp.resource("k8s://{namespace}/{resource_type}",
                     name="Resources by Type in Namespace",
                     description="List of resources of a specific type in a namespace",
                     mime_type="application/json")
        def list_namespaced_resources(namespace: str, resource_type: str) -> str:
            """List resources of a specific type in a namespace."""
            try:
                logger.info(f"Listing {resource_type} in namespace {namespace}")
                resources = self._get_namespaced_resources(namespace, resource_type)
                return json.dumps(resources, indent=2)
            except Exception as e:
                logger.error(f"Error listing {resource_type} in {namespace}: {e}")
                return json.dumps({"error": str(e)})
        
        # Get specific namespaced resource
        @mcp.resource("k8s://{namespace}/{resource_type}/{name}",
                     name="Namespaced Resource",
                     description="Detailed information about a specific namespaced resource",
                     mime_type="application/json")
        def get_namespaced_resource(namespace: str, resource_type: str, name: str) -> str:
            """Get a specific namespaced resource."""
            try:
                logger.info(f"Getting {resource_type} {name} in namespace {namespace}")
                resource = self._get_namespaced_resource(resource_type, name, namespace)
                if resource is None:
                    return json.dumps({"error": f"{resource_type} {name} not found in namespace {namespace}"})
                return json.dumps(resource, indent=2)
            except Exception as e:
                logger.error(f"Error getting {resource_type} {name} in {namespace}: {e}")
                return json.dumps({"error": str(e)})
        
        # List cluster-scoped resources
        @mcp.resource("k8s:///{resource_type}",
                     name="Cluster-Scoped Resources",
                     description="List of cluster-scoped resources of a specific type",
                     mime_type="application/json")
        def list_cluster_resources(resource_type: str) -> str:
            """List cluster-scoped resources of a specific type."""
            try:
                logger.info(f"Listing cluster-scoped resources of type {resource_type}")
                resources = self._get_cluster_resources(resource_type)
                return json.dumps(resources, indent=2)
            except Exception as e:
                logger.error(f"Error listing {resource_type}: {e}")
                return json.dumps({"error": str(e)})
        
        # Get specific cluster-scoped resource
        @mcp.resource("k8s:///{resource_type}/{name}",
                     name="Cluster-Scoped Resource",
                     description="Detailed information about a specific cluster-scoped resource",
                     mime_type="application/json")
        def get_cluster_resource(resource_type: str, name: str) -> str:
            """Get a specific cluster-scoped resource."""
            try:
                logger.info(f"Getting cluster-scoped resource {resource_type} {name}")
                resource = self._get_cluster_resource(resource_type, name)
                if resource is None:
                    return json.dumps({"error": f"{resource_type} {name} not found"})
                return json.dumps(resource, indent=2)
            except Exception as e:
                logger.error(f"Error getting {resource_type} {name}: {e}")
                return json.dumps({"error": str(e)})
        
        # Get all resources in a namespace
        @mcp.resource("k8s:///{namespace}",
                     name="Namespace Overview",
                     description="Overview of all resources in a namespace",
                     mime_type="application/json")
        def get_namespace_overview(namespace: str) -> str:
            """Get an overview of all resources in a namespace."""
            try:
                logger.info(f"Getting overview of namespace {namespace}")
                namespace_info = {}
                
                # Get namespace details
                namespaces = self.k8s_client.get_namespaces()
                namespace_info["namespace"] = next((ns for ns in namespaces if ns["name"] == namespace), {})
                
                # Get resources in the namespace
                namespace_info["pods"] = self.k8s_client.get_pods(namespace=namespace)
                namespace_info["deployments"] = self.k8s_client.get_deployments(namespace=namespace)
                namespace_info["services"] = self.k8s_client.get_services(namespace=namespace)
                namespace_info["persistentvolumeclaims"] = self.k8s_client.get_persistent_volume_claims(namespace=namespace)
                
                return json.dumps(namespace_info, indent=2)
            except Exception as e:
                logger.error(f"Error getting namespace overview for {namespace}: {e}")
                return json.dumps({"error": str(e)})
    
    def _get_namespaced_resources(self, namespace: str, resource_type: str) -> List[Dict[str, Any]]:
        """Get resources of a specific type in a namespace."""
        if resource_type == "pods":
            return self.k8s_client.get_pods(namespace=namespace)
        elif resource_type == "deployments":
            return self.k8s_client.get_deployments(namespace=namespace)
        elif resource_type == "services":
            return self.k8s_client.get_services(namespace=namespace)
        elif resource_type == "persistentvolumeclaims":
            return self.k8s_client.get_persistent_volume_claims(namespace=namespace)
        elif resource_type == "events":
            return self.k8s_client.get_events(namespace=namespace)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def _get_namespaced_resource(self, resource_type: str, name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get a specific namespaced resource."""
        if resource_type == "pods":
            return self.k8s_client.get_pod(name, namespace)
        elif resource_type == "deployments":
            return self.k8s_client.get_deployment(name, namespace)
        elif resource_type == "services":
            return self.k8s_client.get_service(name, namespace)
        elif resource_type == "persistentvolumeclaims":
            return self.k8s_client.get_persistent_volume_claim(name, namespace)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def _get_cluster_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """Get cluster-scoped resources of a specific type."""
        if resource_type == "nodes":
            return self.k8s_client.get_nodes()
        elif resource_type == "persistentvolumes":
            return self.k8s_client.get_persistent_volumes()
        elif resource_type == "namespaces":
            return self.k8s_client.get_namespaces()
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def _get_cluster_resource(self, resource_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific cluster-scoped resource."""
        if resource_type == "nodes":
            return self.k8s_client.get_node(name)
        elif resource_type == "persistentvolumes":
            return self.k8s_client.get_persistent_volume(name)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")


def register_cluster_resources(mcp: FastMCP, k8s_client: K8sClient) -> None:
    """Register cluster resources with the MCP server.
    
    Args:
        mcp: MCP server.
        k8s_client: Kubernetes client.
    """
    # Create the resources manager
    resources = KubernetesResources(k8s_client)
    
    # Register the resources with the newer FastMCP resource API
    resources.register_resources(mcp)
    
    # For backward compatibility with tests that expect list_resources and read_resource functions
    if hasattr(mcp, 'register_list_resources_handler') and hasattr(mcp, 'register_read_resource_handler'):
        @mcp.register_list_resources_handler
        def list_resources() -> List[Resource]:
            """List all available resources.
            
            Returns:
                List of resources.
            """
            # Return resources in the expected Resource format
            result = []
            
            # Add namespace-level resources
            # First call to get_namespaces for namespace resources
            try:
                namespaces = k8s_client.get_namespaces()
                for namespace in namespaces:
                    name = namespace["name"]
                    result.append(
                        Resource(
                            uri=f"k8s://namespaces/{name}",
                            name=f"Namespace: {name}",
                            description=f"Kubernetes namespace {name}",
                            mimeType="application/json",
                        )
                    )
            except Exception as e:
                logger.error(f"Error listing namespaces: {e}")
                
            # Second call to get_namespaces for processing namespace-specific resources
            try:
                namespaces = k8s_client.get_namespaces()
                for namespace in namespaces:
                    name = namespace["name"]
                    
                    # Add pod resources
                    try:
                        pods = k8s_client.get_pods(namespace=name)
                        for pod in pods:
                            pod_name = pod["name"]
                            result.append(
                                Resource(
                                    uri=f"k8s://namespaces/{name}/pods/{pod_name}",
                                    name=f"Pod: {pod_name} (ns: {name})",
                                    description=f"Kubernetes pod {pod_name} in namespace {name}",
                                    mimeType="application/json",
                                )
                            )
                    except Exception as e:
                        logger.error(f"Error listing pods in namespace {name}: {e}")
                    
                    # Add deployment resources
                    try:
                        deployments = k8s_client.get_deployments(namespace=name)
                        for deployment in deployments:
                            deploy_name = deployment["name"]
                            result.append(
                                Resource(
                                    uri=f"k8s://namespaces/{name}/deployments/{deploy_name}",
                                    name=f"Deployment: {deploy_name} (ns: {name})",
                                    description=f"Kubernetes deployment {deploy_name} in namespace {name}",
                                    mimeType="application/json",
                                )
                            )
                    except Exception as e:
                        logger.error(f"Error listing deployments in namespace {name}: {e}")
                    
                    # Add service resources
                    try:
                        services = k8s_client.get_services(namespace=name)
                        for service in services:
                            svc_name = service["name"]
                            result.append(
                                Resource(
                                    uri=f"k8s://namespaces/{name}/services/{svc_name}",
                                    name=f"Service: {svc_name} (ns: {name})",
                                    description=f"Kubernetes service {svc_name} in namespace {name}",
                                    mimeType="application/json",
                                )
                            )
                    except Exception as e:
                        logger.error(f"Error listing services in namespace {name}: {e}")
                    
                    # Add persistent volume claim resources
                    try:
                        pvcs = k8s_client.get_persistent_volume_claims(namespace=name)
                        for pvc in pvcs:
                            pvc_name = pvc["name"]
                            result.append(
                                Resource(
                                    uri=f"k8s://namespaces/{name}/persistentvolumeclaims/{pvc_name}",
                                    name=f"PersistentVolumeClaim: {pvc_name} (ns: {name})",
                                    description=f"Kubernetes persistent volume claim {pvc_name} in namespace {name}",
                                    mimeType="application/json",
                                )
                            )
                    except Exception as e:
                        logger.error(f"Error listing persistent volume claims in namespace {name}: {e}")
            except Exception as e:
                logger.error(f"Error processing namespaces: {e}")
            
            # Add node resources
            try:
                nodes = k8s_client.get_nodes()
                for node in nodes:
                    node_name = node["name"]
                    result.append(
                        Resource(
                            uri=f"k8s://nodes/{node_name}",
                            name=f"Node: {node_name}",
                            description=f"Kubernetes node {node_name}",
                            mimeType="application/json",
                        )
                    )
            except Exception as e:
                logger.error(f"Error listing nodes: {e}")
            
            # Add persistent volume resources
            try:
                pvs = k8s_client.get_persistent_volumes()
                for pv in pvs:
                    pv_name = pv["name"]
                    result.append(
                        Resource(
                            uri=f"k8s://persistentvolumes/{pv_name}",
                            name=f"PersistentVolume: {pv_name}",
                            description=f"Kubernetes persistent volume {pv_name}",
                            mimeType="application/json",
                        )
                    )
            except Exception as e:
                logger.error(f"Error listing persistent volumes: {e}")
            
            return result
        
        @mcp.register_read_resource_handler
        def read_resource(uri: str) -> str:
            """Read a resource.
            
            Args:
                uri: Resource URI.
            
            Returns:
                Resource content.
            """
            logger.info(f"Reading resource: {uri}")
            
            # Parse the URI for namespaced resources
            match = re.match(r"k8s://namespaces/([^/]+)/([^/]+)/([^/]+)$", uri)
            if match:
                namespace = match.group(1)
                resource_type = match.group(2)
                name = match.group(3)
                
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
                name = match.group(2)
                
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
                        namespaces = k8s_client.get_namespaces()
                        namespace_info["namespace"] = next((ns for ns in namespaces if ns["name"] == name), {})
                        
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
