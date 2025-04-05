#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Configuration module for the MCP Kubernetes server.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import yaml
from pathlib import Path
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    """Server configuration."""
    
    name: str = "mcp-k8s-server"
    transport: str = "sse"  # "stdio" or "sse"
    port: int = 8000
    host: str = "10.121.87.184"


class KubernetesConfig(BaseModel):
    """Kubernetes configuration."""
    
    config_path: str = ""
    context: str = ""
    namespace: str = "default"
    resource_types: List[str] = Field(
        default=[
            "pods", "deployments", "services", "configmaps", "secrets",
            "persistentvolumeclaims", "persistentvolumes", "nodes",
            "namespaces", "events", "ingresses", "statefulsets",
            "daemonsets", "jobs", "cronjobs", "replicasets"
        ]
    )


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    
    enabled: bool = True
    interval: int = 30
    resources: List[str] = Field(default=["pods", "nodes", "deployments"])
    metrics: List[str] = Field(default=["cpu", "memory", "disk", "network"])


class Config(BaseSettings):
    """Main configuration."""
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    model_config = SettingsConfigDict(
        env_prefix="MCP_K8S_SERVER_",
        env_nested_delimiter="__",
    )


def find_config_file() -> Optional[Path]:
    """Find the configuration file."""
    # Check environment variable
    env_config = os.environ.get("MCP_K8S_SERVER_CONFIG")
    if env_config:
        config_path = Path(env_config)
        if config_path.exists():
            return config_path
    
    # Check common locations
    common_locations = [
        Path("./config.yaml"),
        Path("./config/config.yaml"),
        Path("/etc/mcp-k8s-server/config.yaml"),
        Path.home() / ".config" / "mcp-k8s-server" / "config.yaml",
    ]
    
    for location in common_locations:
        if location.exists():
            return location
    
    return None


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from file and environment variables."""
    config = Config()
    
    # Load from file if provided
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
    else:
        path = find_config_file()
    
    # Load from file if found
    if path:
        with open(path, "r") as f:
            file_config = yaml.safe_load(f)
            if file_config:
                # Update config with file values
                for section, values in file_config.items():
                    if hasattr(config, section) and isinstance(values, dict):
                        section_model = getattr(config, section)
                        for key, value in values.items():
                            if hasattr(section_model, key):
                                setattr(section_model, key, value)
    
    return config
