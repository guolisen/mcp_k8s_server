#!/usr/bin/env python3
"""Test script for the MCP Kubernetes server with SSL verification disabled."""

import logging
import os
import sys
import argparse
import asyncio
import signal
import subprocess
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_k8s_server.config import load_config
from mcp_k8s_server.server import create_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


async def test_server(config_path):
    """Test the MCP Kubernetes server with the specified configuration.
    
    Args:
        config_path: Path to the configuration file.
    """
    try:
        # Load the configuration
        logger.info(f"Loading configuration from {config_path}")
        config = load_config(config_path)
        
        # Log SSL verification setting
        logger.info(f"SSL verification: {'Enabled' if config.kubernetes.ssl_verify else 'Disabled'}")
        
        # Create the MCP server
        logger.info("Creating MCP server")
        mcp = await create_server(config)
        
        # Start the server in a separate process
        logger.info("Starting MCP server in a separate process")
        server_process = subprocess.Popen(
            [sys.executable, "-m", "mcp_k8s_server.main", "--config", config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # Wait for the server to start
        logger.info("Waiting for the server to start")
        time.sleep(2)
        
        # Check if the server is running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            logger.error(f"Server failed to start: {stderr}")
            return False
        
        # Server is running
        logger.info("Server started successfully")
        
        # Wait for a moment to allow the server to initialize
        time.sleep(2)
        
        # Stop the server
        logger.info("Stopping the server")
        server_process.send_signal(signal.SIGINT)
        server_process.wait()
        
        logger.info("Server test completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test MCP Kubernetes server with SSL verification settings")
    parser.add_argument("--config", "-c", default="config/test_config_no_ssl_verify.yaml",
                        help="Path to the configuration file")
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_server(args.config))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
