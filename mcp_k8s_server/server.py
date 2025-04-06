#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: MCP server for Kubernetes.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio
import logging
import sys
from typing import Any, Dict, Optional, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import ClientRequest, CallToolRequest

from mcp_k8s_server.config import Config, load_config
from mcp_k8s_server.k8s.client import K8sClient
from mcp_k8s_server.k8s.operations import K8sOperations
from mcp_k8s_server.k8s.monitoring import K8sMonitoring
from mcp_k8s_server.tools.resource_tools import register_resource_tools
from mcp_k8s_server.tools.operation_tools import register_operation_tools
from mcp_k8s_server.tools.monitoring_tools import register_monitoring_tools
from mcp_k8s_server.prompts.analysis_prompts import register_analysis_prompts
from mcp_k8s_server.resources.cluster_resources import register_cluster_resources

logger = logging.getLogger(__name__)


def create_server(config: Optional[Config] = None) -> FastMCP:
    """Create an MCP server for Kubernetes.
    
    Args:
        config: Server configuration. If None, loads configuration from file.
    
    Returns:
        MCP server.
    """
    # Load configuration if not provided
    if config is None:
        config = load_config()
    
    # Create the MCP server with initialization timeout
    # This helps prevent "Received request before initialization was complete" errors
    # by automatically closing connections that don't initialize properly
    mcp = FastMCP(
        config.server.name,
        host=config.server.host,
        port=config.server.port,
        settings={
            "initialization_timeout": 10.0, # 10 second timeout
            "log_level": "debug"
        }  
    )
    
    # Create the Kubernetes client
    k8s_client = K8sClient(config.kubernetes)
    
    # Create the Kubernetes operations
    k8s_operations = K8sOperations(k8s_client)
    
    # Create the Kubernetes monitoring
    k8s_monitoring = K8sMonitoring(k8s_client, config.monitoring)
    
    # Register tools
    register_resource_tools(mcp, k8s_client)
    register_operation_tools(mcp, k8s_operations)
    register_monitoring_tools(mcp, k8s_monitoring)
    
    # Register prompts
    register_analysis_prompts(mcp)
    
    # Register resources
    register_cluster_resources(mcp, k8s_client)
    
    # Start monitoring
    if config.monitoring.enabled:
        k8s_monitoring.start_monitoring()
    
    return mcp


def run_server(config: Optional[Config] = None, 
              transport: Optional[str] = None,
              port: Optional[int] = None,
              host: Optional[str] = None) -> None:
    """Run the MCP server.
    
    Args:
        config: Server configuration. If None, loads configuration from file.
        transport: Transport type. If None, uses the value from the configuration.
        port: Port for SSE transport. If None, uses the value from the configuration.
        host: Host for SSE transport. If None, uses the value from the configuration.
    """
    # Load configuration if not provided
    if config is None:
        config = load_config()
    
    # Override configuration with provided values
    if transport is not None:
        config.server.transport = transport
    
    if port is not None:
        config.server.port = port
    
    if host is not None:
        config.server.host = host
    
    # Create the MCP server
    mcp = create_server(config)
    
    # Run the server
    try:        
        if config.server.transport == "stdio":
            logger.info("Starting MCP server with stdio transport")
            mcp.run(transport="stdio")
        elif config.server.transport == "sse":
            logger.info(f"Starting MCP server with SSE transport on {config.server.host}:{config.server.port}")
            mcp.run(transport="sse")
        else:
            # 'both' transport is not supported, so we treat it as an invalid transport type
            logger.error(f"Invalid transport type: {config.server.transport}")
            logger.info("Supported transport types are 'stdio' and 'sse'")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Stopping MCP server")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        sys.exit(1)
