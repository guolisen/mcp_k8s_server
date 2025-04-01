"""
Node resource handler for Kubernetes nodes.
"""

import logging
from typing import Any, Dict, List, Optional

from modelcontextprotocol.sdk.server import Server
from modelcontextprotocol.sdk.types import ReadResourceResult, ResourceContent, ResourceInfo, ResourceTemplate

from ..k8s.api_client import KubernetesApiClient
from ..k8s.kubectl import KubectlWrapper
from .base import BaseResourceHandler

logger = logging.getLogger(__name__)

class NodeResourceHandler(BaseResourceHandler):
    """Handler for Kubernetes node resources."""
    
    def __init__(self, server: Server, api_client: KubernetesApiClient, kubectl_wrapper: KubectlWrapper):
        """
        Initialize the node resource handler.
        
        Args:
            server: The MCP server instance.
            api_client: The Kubernetes API client.
            kubectl_wrapper: The kubectl wrapper.
        """
        super().__init__(server, api_client, kubectl_wrapper)
    
    def register_resources(self) -> None:
        """Register node resources and resource templates."""
        # Register static resources
        self.server.resources.extend(self.get_resource_info("nodes", "Kubernetes nodes"))
        
        # Register resource template for specific node
        self.server.resource_templates.extend([
            ResourceTemplate(
                uri_template="kubernetes://nodes/{name}",
                name="Specific node",
                description="Details of a specific Kubernetes node",
                mime_type="application/json"
            )
        ])
    
    def handle_resource_request(self, uri: str, method: str = "get") -> ReadResourceResult:
        """
        Handle a node resource request.
        
        Args:
            uri: The resource URI.
            method: The HTTP method (get, post, etc.).
        
        Returns:
            ReadResourceResult with the node data.
        
        Raises:
            ValueError: If the URI is invalid or the node is not found.
        """
        try:
            resource_type, namespace, name = self.uri_parser.parse_resource_uri(uri)
            
            if resource_type != "nodes":
                raise ValueError(f"Invalid resource type: {resource_type}. Expected: nodes")
            
            # Nodes are cluster-level resources, so namespace is ignored if provided
            
            if name is None:
                # Get all nodes
                nodes = self.api_client.get_nodes()
                response_data = {
                    "kind": "NodeList",
                    "apiVersion": "v1",
                    "items": nodes
                }
            else:
                # Get specific node - find it in the list
                nodes = self.api_client.get_nodes()
                node = next((n for n in nodes if n["name"] == name), None)
                
                if not node:
                    raise ValueError(f"Node not found: {name}")
                
                response_data = {
                    "kind": "Node",
                    "apiVersion": "v1",
                    "metadata": {
                        "name": node["name"]
                    },
                    "spec": {},
                    "status": {
                        "capacity": {
                            "cpu": node["cpu_capacity"],
                            "memory": node["memory_capacity"],
                            "pods": node["pods_capacity"]
                        },
                        "allocatable": {
                            "cpu": node["cpu_allocatable"],
                            "memory": node["memory_allocatable"],
                            "pods": node["pods_allocatable"]
                        },
                        "conditions": [
                            {
                                "type": cond_type,
                                "status": status
                            }
                            for cond_type, status in node["conditions"].items()
                        ],
                        "addresses": [
                            {
                                "type": "InternalIP",
                                "address": node["internal_ip"]
                            }
                        ] + ([
                            {
                                "type": "ExternalIP",
                                "address": node["external_ip"]
                            }
                        ] if node["external_ip"] else []),
                        "nodeInfo": {
                            "kubeletVersion": node["kubelet_version"],
                            "osImage": node["os_image"]
                        }
                    }
                }
            
            return ReadResourceResult(
                contents=[
                    ResourceContent(
                        uri=uri,
                        mime_type="application/json",
                        text=self.format_json_response(response_data)
                    )
                ]
            )
        
        except ValueError as e:
            logger.error(f"Error handling node resource request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error handling node resource request: {e}")
            raise ValueError(f"Failed to get node resource: {str(e)}")
