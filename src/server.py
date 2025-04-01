#!/usr/bin/env python
"""
Main entry point for the Kubernetes MCP server.
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Add the parent directory to the Python path to make relative imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
# Use our custom TCP server implementation
from src.tcp_server import tcp_server
from mcp.types import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    ListResourcesRequest,
    ListResourceTemplatesRequest,
    ListToolsRequest,
    ErrorData,
    ReadResourceRequest,
)
from mcp.shared.exceptions import McpError

import kubernetes.client
from kubernetes import client, config
from kubernetes.client.rest import ApiException

try:
    # When imported as part of the package
    from mcp_k8s_server.k8s.api_client import KubernetesApiClient
    from mcp_k8s_server.k8s.kubectl import KubectlWrapper
    from mcp_k8s_server.resources.base import ResourceUriParser
    from mcp_k8s_server.resources.nodes import NodeResourceHandler
    from mcp_k8s_server.resources.deployments import DeploymentResourceHandler
    from mcp_k8s_server.tools.operations import KubernetesOperations
    from mcp_k8s_server.tools.monitoring import KubernetesMonitoring
    from mcp_k8s_server.tools.status import KubernetesStatus
    from mcp_k8s_server.utils.config import load_config, get_server_config, get_kubernetes_config, setup_logging
    from mcp_k8s_server.tcp_server import tcp_server
except ImportError:
    # When run directly
    from src.k8s.api_client import KubernetesApiClient
    from src.k8s.kubectl import KubectlWrapper
    from src.resources.base import ResourceUriParser
    from src.resources.nodes import NodeResourceHandler
    from src.resources.deployments import DeploymentResourceHandler
    from src.tools.operations import KubernetesOperations
    from src.tools.monitoring import KubernetesMonitoring
    from src.tools.status import KubernetesStatus
    from src.utils.config import load_config, get_server_config, get_kubernetes_config, setup_logging
    # Already imported above for direct execution

logger = logging.getLogger("mcp_k8s_server")

class KubernetesMcpServer:
    """
    Model Context Protocol server for Kubernetes.
    Provides resources and tools for interacting with Kubernetes clusters.
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize the Kubernetes MCP server.
        
        Args:
            kubeconfig_path: Path to kubeconfig file. If None, uses the default.
        """
        # Set server information
        self.server_name = "kubernetes-mcp-server"
        self.server_version = "0.1.0"
        
        # Initialize the server
        self.server = Server(self.server_name)
        
        # Error handling
        self.server.onerror = self._handle_error
        
        # Initialize Kubernetes clients
        self.api_client = KubernetesApiClient(kubeconfig_path)
        self.kubectl_wrapper = KubectlWrapper(kubeconfig_path)
        
        # URI parser
        self.uri_parser = ResourceUriParser()
        
        # Initialize resource handlers
        self.resource_handlers = {
            "nodes": NodeResourceHandler(self.server, self.api_client, self.kubectl_wrapper),
            "deployments": DeploymentResourceHandler(self.server, self.api_client, self.kubectl_wrapper),
            # Add more resource handlers here
        }
        
        # Initialize tool handlers
        self.operations = KubernetesOperations(self.server, self.api_client, self.kubectl_wrapper)
        self.monitoring = KubernetesMonitoring(self.server, self.api_client, self.kubectl_wrapper)
        self.status = KubernetesStatus(self.server, self.api_client, self.kubectl_wrapper)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register all resource and request handlers."""
        # Register resource handlers
        for handler in self.resource_handlers.values():
            handler.register_resources()
        
        # Set request handlers
        self.server.request_handlers[ReadResourceRequest] = self._handle_read_resource
    
    def _handle_error(self, error: Exception) -> None:
        """
        Handle errors that occur during server operation.
        
        Args:
            error: The error that occurred.
        """
        logger.error(f"MCP server error: {error}")
    
    def _handle_read_resource(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a read_resource request.
        
        Args:
            request: The read_resource request.
        
        Returns:
            The resource content.
        
        Raises:
            McpError: If the resource is not found or an error occurs.
        """
        uri = request["params"]["uri"]
        
        try:
            resource_type, namespace, name = self.uri_parser.parse_resource_uri(uri)
            
            if resource_type in self.resource_handlers:
                return self.resource_handlers[resource_type].handle_resource_request(uri)
            else:
                raise McpError(
                    ErrorData(
                        code=METHOD_NOT_FOUND,  # Using METHOD_NOT_FOUND as a substitute for NOT_FOUND
                        message=f"Resource type not supported: {resource_type}"
                    )
                )
        
        except ValueError as e:
            raise McpError(
                ErrorData(
                    code=INVALID_REQUEST,
                    message=f"Invalid resource URI: {uri}. {str(e)}"
                )
            )
        
        except Exception as e:
            logger.error(f"Error handling resource request: {e}")
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Error handling resource request: {str(e)}"
                )
            )
    
    async def run(self, config: Dict[str, Any]) -> None:
        """
        Run the MCP server.
        
        Args:
            config: The server configuration.
        """
        # Create initialization options
        init_options = {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "capabilities": {
                "resources": True,
                "tools": True
            }
        }
        
        # Get server configuration
        server_config = get_server_config(config)
        server_mode = server_config.get("mode", "stdio")
        
        if server_mode == "network":
            # Use TCP server
            bind_ip = server_config.get("bind_ip", "127.0.0.1")
            bind_port = server_config.get("bind_port", 8080)
            
            logger.info(f"Starting Kubernetes MCP server in network mode on {bind_ip}:{bind_port}")
            async with tcp_server(bind_ip, bind_port) as (read_stream, write_stream):
                logger.info(f"Kubernetes MCP server running on {bind_ip}:{bind_port}")
                await self.server.run(read_stream, write_stream, init_options)
        else:
            # Use stdio server (default)
            logger.info("Starting Kubernetes MCP server in stdio mode")
            async with stdio_server() as (read_stream, write_stream):
                logger.info("Kubernetes MCP server running on stdio")
                await self.server.run(read_stream, write_stream, init_options)

def prepareKubeConfig():
    configuration = client.Configuration()
    config.load_incluster_config(client_configuration=configuration)
    configuration.verify_ssl = False
    v1 = client.CoreV1Api(client.ApiClient(configuration))
    return v1, configuration

def main() -> None:
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description="Kubernetes MCP Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--kubeconfig", help="Path to kubeconfig file (overrides config file)")
    parser.add_argument("--bind-ip", help="IP address to bind to (overrides config file)")
    parser.add_argument("--bind-port", type=int, help="Port to bind to (overrides config file)")
    parser.add_argument("--mode", choices=["stdio", "network"], help="Server mode (overrides config file)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up logging
    setup_logging(config)
    
    # Override config with command line arguments
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server_config = get_server_config(config)
    if args.bind_ip:
        server_config["bind_ip"] = args.bind_ip
    if args.bind_port:
        server_config["bind_port"] = args.bind_port
    if args.mode:
        server_config["mode"] = args.mode
    
    kubernetes_config = get_kubernetes_config(config)
    if args.kubeconfig:
        kubernetes_config["kubeconfig_path"] = args.kubeconfig
    
    # Use the provided kubeconfig path, or the default
    kubeconfig_path = kubernetes_config.get("kubeconfig_path") or os.environ.get("KUBECONFIG")
    
    # Create and run the server
    server = KubernetesMcpServer(kubeconfig_path)
    try:
        asyncio.run(server.run(config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
