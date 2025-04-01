"""
Base module for Kubernetes resource handlers.
Provides common functionality for all resource handler modules.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from modelcontextprotocol.sdk.server import Server
from modelcontextprotocol.sdk.types import ReadResourceResult, ResourceInfo, ResourceTemplate

logger = logging.getLogger(__name__)

class ResourceUriParser:
    """Utility class for parsing and validating resource URIs."""
    
    @staticmethod
    def parse_resource_uri(uri: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Parse a resource URI into components.
        
        Expected format: kubernetes://[resource_type]/[namespace]/[name]
        Or: kubernetes://[resource_type]/all (for all resources of a type)
        Or: kubernetes://[resource_type] (for all resources of a type, alternate form)
        
        Args:
            uri: The resource URI to parse.
        
        Returns:
            Tuple of (resource_type, namespace, name).
            If namespace is None, it means "all namespaces".
            If name is None, it means "all resources of this type in the namespace".
        
        Raises:
            ValueError: If the URI is not in the expected format.
        """
        if not uri.startswith("kubernetes://"):
            raise ValueError(f"Invalid URI scheme: {uri}. Expected kubernetes://")
        
        # Remove scheme
        path = uri[len("kubernetes://"):]
        
        # Split into components
        parts = path.strip("/").split("/")
        
        if not parts or not parts[0]:
            raise ValueError(f"Invalid URI: {uri}. Resource type is required.")
        
        resource_type = parts[0]
        
        if len(parts) == 1:
            # kubernetes://[resource_type] - all resources of type
            return resource_type, None, None
        
        if len(parts) == 2:
            if parts[1].lower() == "all":
                # kubernetes://[resource_type]/all - all resources of type (explicit)
                return resource_type, None, None
            else:
                # kubernetes://[resource_type]/[namespace] - all resources of type in namespace
                return resource_type, parts[1], None
        
        if len(parts) == 3:
            # kubernetes://[resource_type]/[namespace]/[name] - specific resource
            return resource_type, parts[1], parts[2]
        
        raise ValueError(f"Invalid URI format: {uri}")
    
    @staticmethod
    def build_resource_uri(resource_type: str, namespace: Optional[str] = None, name: Optional[str] = None) -> str:
        """
        Build a resource URI from components.
        
        Args:
            resource_type: The type of resource.
            namespace: The namespace of the resource (optional).
            name: The name of the resource (optional).
        
        Returns:
            A properly formatted resource URI.
        """
        if namespace is None:
            return f"kubernetes://{resource_type}"
        
        if name is None:
            return f"kubernetes://{resource_type}/{namespace}"
        
        return f"kubernetes://{resource_type}/{namespace}/{name}"

class BaseResourceHandler:
    """Base class for all Kubernetes resource handlers."""
    
    def __init__(self, server: Server, api_client, kubectl_wrapper):
        """
        Initialize the resource handler.
        
        Args:
            server: The MCP server instance.
            api_client: The Kubernetes API client.
            kubectl_wrapper: The kubectl wrapper.
        """
        self.server = server
        self.api_client = api_client
        self.kubectl_wrapper = kubectl_wrapper
        self.uri_parser = ResourceUriParser()
    
    def register_resources(self) -> None:
        """
        Register resources and resource templates.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement register_resources()")
    
    def get_resource_info(self, resource_type: str, description: str) -> List[ResourceInfo]:
        """
        Get resource info for a specific resource type.
        
        Args:
            resource_type: The type of resource.
            description: Description of the resource.
        
        Returns:
            List of ResourceInfo objects.
        """
        return [
            ResourceInfo(
                uri=self.uri_parser.build_resource_uri(resource_type),
                name=f"All {resource_type} in all namespaces",
                description=f"List of all {description} across all namespaces",
                mime_type="application/json"
            )
        ]
    
    def get_resource_templates(self, resource_type: str, description: str) -> List[ResourceTemplate]:
        """
        Get resource templates for a specific resource type.
        
        Args:
            resource_type: The type of resource.
            description: Description of the resource.
        
        Returns:
            List of ResourceTemplate objects.
        """
        return [
            # Template for all resources of type in a namespace
            ResourceTemplate(
                uri_template=f"kubernetes://{resource_type}/{{namespace}}",
                name=f"All {resource_type} in a namespace",
                description=f"List of all {description} in the specified namespace",
                mime_type="application/json"
            ),
            # Template for a specific resource
            ResourceTemplate(
                uri_template=f"kubernetes://{resource_type}/{{namespace}}/{{name}}",
                name=f"Specific {resource_type}",
                description=f"Details of a specific {description} in the specified namespace",
                mime_type="application/json"
            )
        ]
    
    def format_json_response(self, data: Any) -> str:
        """
        Format data as a JSON string with proper indentation.
        
        Args:
            data: The data to format.
        
        Returns:
            Formatted JSON string.
        """
        return json.dumps(data, indent=2)
    
    def handle_resource_request(self, uri: str, method: str = "get") -> ReadResourceResult:
        """
        Handle a resource request.
        
        Args:
            uri: The resource URI.
            method: The HTTP method (get, post, etc.).
        
        Returns:
            ReadResourceResult with the resource content.
        
        Raises:
            ValueError: If the URI is invalid or the resource is not found.
        """
        raise NotImplementedError("Subclasses must implement handle_resource_request()")
