#!/usr/bin/env python3
"""Test script for SSL verification settings in the MCP Kubernetes server."""

import logging
import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_k8s_server.config import load_config, KubernetesConfig
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


class TestSSLVerification(unittest.TestCase):
    """Test cases for SSL verification settings."""

    def setUp(self):
        """Set up test environment."""
        # Ensure the config directory exists
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Create test config files if they don't exist
        self.create_test_configs()

    def create_test_configs(self):
        """Create test configuration files if they don't exist."""
        # Test config with SSL verification enabled (default)
        self.ssl_verify_config_path = self.config_dir / "test_config_ssl_verify.yaml"
        if not self.ssl_verify_config_path.exists():
            with open(self.ssl_verify_config_path, "w") as f:
                f.write("""
# Test configuration with SSL verification enabled (default)
server:
  name: mcp-k8s-server
  transport: sse
  port: 8001
  host: 127.0.0.1

kubernetes:
  config_path: "~/.kube/config"
  context: ""
  namespace: default
  ssl_verify: true
  resource_types:
    - pods
    - deployments
    - services
    - nodes
    - namespaces

monitoring:
  enabled: false
""")
        
        # Test config with SSL verification disabled
        self.no_ssl_verify_config_path = self.config_dir / "test_config_no_ssl_verify.yaml"
        if not self.no_ssl_verify_config_path.exists():
            with open(self.no_ssl_verify_config_path, "w") as f:
                f.write("""
# Test configuration with SSL verification disabled
server:
  name: mcp-k8s-server
  transport: sse
  port: 8002
  host: 127.0.0.1

kubernetes:
  config_path: "~/.kube/config"
  context: ""
  namespace: default
  ssl_verify: false
  resource_types:
    - pods
    - deployments
    - services
    - nodes
    - namespaces

monitoring:
  enabled: false
""")

    def test_ssl_verify_enabled(self):
        """Test that SSL verification is enabled by default."""
        # Create a default KubernetesConfig
        k8s_config = KubernetesConfig()
        
        # Check that SSL verification is enabled by default
        self.assertTrue(k8s_config.ssl_verify, "SSL verification should be enabled by default")
        
        # Load the test config with SSL verification enabled
        config = load_config(self.ssl_verify_config_path)
        
        # Check that SSL verification is enabled in the loaded config
        self.assertTrue(config.kubernetes.ssl_verify, "SSL verification should be enabled in the loaded config")
        
        logger.info("SSL verification is correctly enabled by default")

    def test_ssl_verify_disabled(self):
        """Test that SSL verification can be disabled."""
        # Load the test config with SSL verification disabled
        config = load_config(self.no_ssl_verify_config_path)
        
        # Check that SSL verification is disabled in the loaded config
        self.assertFalse(config.kubernetes.ssl_verify, "SSL verification should be disabled in the loaded config")
        
        logger.info("SSL verification is correctly disabled in the test config")

    def test_client_initialization(self):
        """Test that the client is initialized with the correct SSL verification setting."""
        # This test doesn't actually connect to a Kubernetes cluster
        # It just verifies that the client initialization code handles the SSL verification setting
        
        # Create a KubernetesConfig with SSL verification disabled
        k8s_config = KubernetesConfig(ssl_verify=False)
        
        # Create a K8sClient with the config
        # This should not raise an exception
        try:
            client = K8sClient(k8s_config)
            logger.info("Client initialized successfully with SSL verification disabled")
        except Exception as e:
            self.fail(f"Client initialization failed: {e}")


if __name__ == "__main__":
    unittest.main()
