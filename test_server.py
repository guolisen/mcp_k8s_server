"""Test script for the MCP Kubernetes server."""

import sys
from mcp_k8s_server.server import run_server

if __name__ == "__main__":
    try:
        # Don't await run_server - it's not an async function
        # Use "sse" or "stdio" instead of "both"
        # Use a different port to avoid conflicts
        run_server(transport="sse", port=8001)
        print("Server started successfully!")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
