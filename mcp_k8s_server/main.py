"""Main entry point for the MCP Kubernetes server."""

import asyncio
import logging
import sys
from typing import Optional

import click

from .config import load_config
from .server import run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


@click.command()
@click.option("--config", "-c", help="Path to config file")
@click.option("--transport", "-t", 
              type=click.Choice(["stdio", "sse", "both"]), 
              help="Transport type (stdio, sse, or both)")
@click.option("--port", "-p", type=int, help="Port for SSE transport")
@click.option("--host", "-h", help="Host for SSE transport")
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
def main(config: Optional[str] = None, 
         transport: Optional[str] = None, 
         port: Optional[int] = None, 
         host: Optional[str] = None,
         debug: bool = False) -> None:
    """Run the MCP Kubernetes server."""
    # Set log level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Load configuration
    try:
        config_obj = load_config(config)
        logger.info(f"Loaded configuration: {config_obj}")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Run the server
    try:
        asyncio.run(run_server(
            config=config_obj,
            transport=transport,  # type: ignore
            port=port,
            host=host,
        ))
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
