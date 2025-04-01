"""
Deployment resource handler for Kubernetes deployments.
"""

import logging
from typing import Any, Dict, List, Optional

from modelcontextprotocol.sdk.server import Server
from modelcontextprotocol.sdk.types import ReadResourceResult, ResourceContent, ResourceInfo, ResourceTemplate

from ..k8s.api_client import KubernetesApiClient
from ..k8s.kubectl import KubectlWrapper
from .base import BaseResourceHandler

logger = logging.getLogger(__name__)

class DeploymentResourceHandler(BaseResourceHandler):
    """Handler for Kubernetes deployment resources."""
    
    def __init__(self, server: Server, api_client: KubernetesApiClient, kubectl_wrapper: KubectlWrapper):
        """
        Initialize the deployment resource handler.
        
        Args:
            server: The MCP server instance.
            api_client: The Kubernetes API client.
            kubectl_wrapper: The kubectl wrapper.
        """
        super().__init__(server, api_client, kubectl_wrapper)
    
    def register_resources(self) -> None:
        """Register deployment resources and resource templates."""
        # Register static resources
        self.server.resources.extend(self.get_resource_info("deployments", "Kubernetes deployments"))
        
        # Register resource templates
        self.server.resource_templates.extend(
            self.get_resource_templates("deployments", "Kubernetes deployments")
        )
    
    def handle_resource_request(self, uri: str, method: str = "get") -> ReadResourceResult:
        """
        Handle a deployment resource request.
        
        Args:
            uri: The resource URI.
            method: The HTTP method (get, post, etc.).
        
        Returns:
            ReadResourceResult with the deployment data.
        
        Raises:
            ValueError: If the URI is invalid or the deployment is not found.
        """
        try:
            resource_type, namespace, name = self.uri_parser.parse_resource_uri(uri)
            
            if resource_type != "deployments":
                raise ValueError(f"Invalid resource type: {resource_type}. Expected: deployments")
            
            if name is not None:
                # Get specific deployment
                if namespace is None:
                    raise ValueError("Namespace is required when requesting a specific deployment")
                
                deployments = self.api_client.get_deployments(namespace)
                deployment = next((d for d in deployments if d["name"] == name), None)
                
                if not deployment:
                    raise ValueError(f"Deployment not found: {namespace}/{name}")
                
                response_data = {
                    "kind": "Deployment",
                    "apiVersion": "apps/v1",
                    "metadata": {
                        "name": deployment["name"],
                        "namespace": deployment["namespace"],
                        "creationTimestamp": deployment["creation_timestamp"]
                    },
                    "spec": {
                        "replicas": deployment["replicas"],
                        "selector": {
                            "matchLabels": deployment["selector"]
                        },
                        "strategy": {
                            "type": deployment["strategy"]
                        }
                    },
                    "status": {
                        "availableReplicas": deployment["available_replicas"],
                        "readyReplicas": deployment["ready_replicas"],
                        "updatedReplicas": deployment["updated_replicas"]
                    }
                }
            elif namespace is not None:
                # Get all deployments in a namespace
                deployments = self.api_client.get_deployments(namespace)
                response_data = {
                    "kind": "DeploymentList",
                    "apiVersion": "apps/v1",
                    "items": deployments
                }
            else:
                # Get all deployments in all namespaces
                deployments = self.api_client.get_deployments()
                response_data = {
                    "kind": "DeploymentList",
                    "apiVersion": "apps/v1",
                    "items": deployments
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
            logger.error(f"Error handling deployment resource request: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error handling deployment resource request: {e}")
            raise ValueError(f"Failed to get deployment resource: {str(e)}")
