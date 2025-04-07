# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Python module for the MCP Kubernetes server: setup.py
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="mcp-k8s-server",
        version="0.1.1",
        license="MIT",
        packages=[
            "mcp_k8s_server",
            "mcp_k8s_server.k8s",
            "mcp_k8s_server.tools",
            "mcp_k8s_server.prompts",
            "mcp_k8s_server.resources",
        ],
        package_dir={"": "."},
        exclude_package_data={
            "": ["k8s/*", "config/*", "docs/*"],
        },
        include_package_data=True,
        install_requires=[
            "mcp>=1.6.0",
            "kubernetes>=30.0.0",
            "pyyaml>=6.0.1",
            "httpx>=0.28.1",
            "click>=8.1.8",
            "pydantic>=2.11.1",
            "pydantic-settings>=2.8.1",
            "pip>=25.0.1",
        ],
        entry_points={
            "console_scripts": [
                "mcp-k8s-server=mcp_k8s_server.main:main",
            ],
        },
        python_requires=">=3.13",
    )
