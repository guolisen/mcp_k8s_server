#!/usr/bin/env python3
"""Test script for direct Kubernetes API access with SSL verification disabled."""

import logging
import os
import sys
import argparse
from kubernetes import client, config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def test_direct_connection(kubeconfig_path, ssl_verify=True):
    """Test direct connection to a Kubernetes cluster.
    
    Args:
        kubeconfig_path: Path to the kubeconfig file.
        ssl_verify: Whether to verify SSL certificates.
    """
    try:
        # Load the kubeconfig
        logger.info(f"Loading kubeconfig from {kubeconfig_path}")
        logger.info(f"SSL verification: {'Enabled' if ssl_verify else 'Disabled'}")
        
        # Load the kubeconfig with SSL verification setting
        config.load_kube_config(
            config_file=os.path.expanduser(kubeconfig_path),
            verify_ssl=ssl_verify
        )
        
        # Create API clients
        core_v1_api = client.CoreV1Api()
        apps_v1_api = client.AppsV1Api()
        
        # Test getting namespaces
        logger.info("Getting namespaces")
        namespaces = core_v1_api.list_namespace()
        logger.info(f"Found {len(namespaces.items)} namespaces")
        for ns in namespaces.items:
            logger.info(f"  - {ns.metadata.name}")
        
        # Test getting nodes
        logger.info("Getting nodes")
        nodes = core_v1_api.list_node()
        logger.info(f"Found {len(nodes.items)} nodes")
        for node in nodes.items:
            logger.info(f"  - {node.metadata.name}")
        
        # Test getting pods
        logger.info("Getting pods in all namespaces")
        pods = core_v1_api.list_pod_for_all_namespaces()
        logger.info(f"Found {len(pods.items)} pods")
        
        logger.info("Direct connection test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test direct Kubernetes API access with SSL verification settings")
    parser.add_argument("--kubeconfig", "-k", default="~/.kube/config",
                        help="Path to the kubeconfig file")
    parser.add_argument("--no-ssl-verify", "-n", action="store_true",
                        help="Disable SSL verification")
    args = parser.parse_args()
    
    success = test_direct_connection(args.kubeconfig, not args.no_ssl_verify)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
