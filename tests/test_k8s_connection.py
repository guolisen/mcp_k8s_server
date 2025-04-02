#!/usr/bin/env python3
"""Test script for connecting to a Kubernetes cluster with different SSL verification settings."""

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


def test_connection(config_path):
    """Test connecting to a Kubernetes cluster with the specified configuration.
    
    Args:
        config_path: Path to the configuration file.
    """
    try:
        # Load the configuration
        logger.info(f"Loading configuration from {config_path}")
        config = load_config(config_path)
        
        # Log SSL verification setting
        logger.info(f"SSL verification: {'Enabled' if config.kubernetes.ssl_verify else 'Disabled'}")
        
        # Create the Kubernetes client
        logger.info("Creating Kubernetes client")
        k8s_client = K8sClient(config.kubernetes)
        
        # Test getting namespaces
        logger.info("Getting namespaces")
        namespaces = k8s_client.get_namespaces()
        logger.info(f"Found {len(namespaces)} namespaces")
        for ns in namespaces:
            logger.info(f"  - {ns['name']}")
        
        # Test getting nodes
        logger.info("Getting nodes")
        nodes = k8s_client.get_nodes()
        logger.info(f"Found {len(nodes)} nodes")
        for node in nodes:
            logger.info(f"  - {node['name']}")
        
        # Test getting pods
        logger.info("Getting pods in all namespaces")
        pods = k8s_client.get_pods(namespace="all")
        logger.info(f"Found {len(pods)} pods")
        
        logger.info("Connection test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Kubernetes connection with different SSL verification settings")
    parser.add_argument("--config", "-c", default="config/test_config_no_ssl_verify.yaml",
                        help="Path to the configuration file")
    args = parser.parse_args()
    
    success = test_connection(args.config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
