"""Test script for the MCP Kubernetes server."""

import asyncio
import sys
from mcp_k8s_server.server import run_server

async def main():
    """Run the server with 'both' transport type."""
    try:
        await run_server(transport="both")
        print("Server started successfully!")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error running main: {e}")
        sys.exit(1)
