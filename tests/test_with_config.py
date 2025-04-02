#!/usr/bin/env python3
"""Test script for the MCP Kubernetes server with different configuration files."""

import logging
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_k8s_server.config import load_config
from mcp_k8s_server.k8s.client import K8sClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def test_with_config(config_path):
    """Test the Kubernetes client with the specified configuration file.
    
    Args:
        config_path: Path to the configuration file.
    """
    try:
        # Load the configuration
        logger.info(f"Loading configuration from {config_path}")
        config = load_config(config_path)
        
        # Log configuration details
        logger.info(f"Server name: {config.server.name}")
        logger.info(f"Server transport: {config.server.transport}")
        logger.info(f"Server port: {config.server.port}")
        logger.info(f"Server host: {config.server.host}")
        logger.info(f"Kubernetes config path: {config.kubernetes.config_path}")
        logger.info(f"Kubernetes context: {config.kubernetes.context}")
        logger.info(f"Kubernetes namespace: {config.kubernetes.namespace}")
        logger.info(f"SSL verification: {'Enabled' if config.kubernetes.ssl_verify else 'Disabled'}")
        
        # Create the Kubernetes client
        logger.info("Creating Kubernetes client")
        k8s_client = K8sClient(config.kubernetes)
        
        # Test getting namespaces
        logger.info("Getting namespaces")
        namespaces = k8s_client.get_namespaces()
        logger.info(f"Found {len(namespaces)} namespaces")
        
        logger.info("Test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test with different configuration files")
    parser.add_argument("--config", "-c", required=True,
                        help="Path to the configuration file")
    args = parser.parse_args()
    
    success = test_with_config(args.config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
