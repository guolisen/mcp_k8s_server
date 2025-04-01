"""
Configuration module for the Kubernetes MCP server.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("mcp_k8s_server")

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "bind_ip": "10.121.87.184",  # Default to localhost
        "bind_port": 8080,       # Default port
        "mode": "network",         # "network" or "stdio"
    },
    "kubernetes": {
        "kubeconfig_path": None,  # Use default if None
    },
    "logging": {
        "level": "INFO",
        "file": None,  # Log to stderr if None
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file. If None, uses default config.
        
    Returns:
        Dict containing the configuration.
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    
                if file_config:
                    # Update the default config with values from the file
                    _update_config_recursive(config, file_config)
                    logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.warning(f"Configuration file not found: {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
    
    return config


def _update_config_recursive(base_config: Dict[str, Any], new_config: Dict[str, Any]) -> None:
    """
    Recursively update a nested dictionary with values from another dictionary.
    
    Args:
        base_config: The base configuration to update.
        new_config: The new configuration values.
    """
    for key, value in new_config.items():
        if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
            _update_config_recursive(base_config[key], value)
        else:
            base_config[key] = value


def get_server_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the server configuration section.
    
    Args:
        config: The full configuration dictionary.
        
    Returns:
        Dict containing the server configuration.
    """
    return config.get("server", DEFAULT_CONFIG["server"])


def get_kubernetes_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the Kubernetes configuration section.
    
    Args:
        config: The full configuration dictionary.
        
    Returns:
        Dict containing the Kubernetes configuration.
    """
    return config.get("kubernetes", DEFAULT_CONFIG["kubernetes"])


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the logging configuration section.
    
    Args:
        config: The full configuration dictionary.
        
    Returns:
        Dict containing the logging configuration.
    """
    return config.get("logging", DEFAULT_CONFIG["logging"])


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging based on the configuration.
    
    Args:
        config: The full configuration dictionary.
    """
    logging_config = get_logging_config(config)
    
    # Set log level
    level_name = logging_config.get("level", "INFO")
    level = getattr(logging, level_name, logging.INFO)
    
    # Set up handlers
    handlers = [logging.StreamHandler()]
    
    # Add file handler if specified
    log_file = logging_config.get("file")
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            handlers.append(file_handler)
        except Exception as e:
            logger.error(f"Error setting up log file: {e}")
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
