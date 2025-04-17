#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 5, 2025
#
# Description: Script to add code headers to all code files in the project.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import re
import datetime
from typing import Dict, List, Optional, Tuple, Union

# Current date for the headers
CURRENT_DATE = datetime.datetime.now().strftime("%B %d, %Y")

# Header templates for different file types
PYTHON_HEADER = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: {date}
#
# Description: {description}
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

SH_HEADER = """#!/bin/bash
#
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: {date}
#
# Description: {description}
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

YAML_HEADER = """# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: {date}
#
# Description: {description}
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

DOCKERFILE_HEADER = """# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: {date}
#
# Description: {description}
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

# File descriptions dictionary - provide custom descriptions for specific files
FILE_DESCRIPTIONS: Dict[str, str] = {
    "mcp_k8s_server/main.py": "Main entry point for the MCP Kubernetes server.",
    "mcp_k8s_server/server.py": "MCP server implementation for Kubernetes.",
    "mcp_k8s_server/config.py": "Configuration management for the MCP Kubernetes server.",
    "mcp_k8s_server/k8s/client.py": "Kubernetes client for the MCP server.",
    "mcp_k8s_server/k8s/operations.py": "Kubernetes operations implementation.",
    "mcp_k8s_server/k8s/monitoring.py": "Kubernetes monitoring implementation.",
    "mcp_k8s_server/tools/resource_tools.py": "MCP tools for Kubernetes resource management.",
    "mcp_k8s_server/tools/operation_tools.py": "MCP tools for Kubernetes operations.",
    "mcp_k8s_server/tools/monitoring_tools.py": "MCP tools for Kubernetes monitoring.",
    "setup.py": "Setup script for the MCP Kubernetes server package.",
    "test_server.py": "Test server for the MCP Kubernetes server.",
}

# Functions to add headers to different file types
def add_header_to_python_file(file_path: str) -> None:
    """Add header to a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Detect if file already has a header
    has_header = bool(re.search(r"# Copyright.*Lewis Guo", content))
    if has_header:
        print(f"File {file_path} already has a header. Skipping.")
        return
    
    # Detect if file starts with shebang or encoding
    has_shebang = content.startswith("#!/")
    has_encoding = bool(re.search(r"^# -\*- coding:.*-\*-", content, re.MULTILINE))
    
    # Get description for the file
    description = FILE_DESCRIPTIONS.get(file_path, f"Python module for the MCP Kubernetes server: {os.path.basename(file_path)}")
    
    # Format the header
    header = PYTHON_HEADER.format(date=CURRENT_DATE, description=description)
    
    # Remove shebang and encoding from header if they're already in the file
    if has_shebang:
        header = "\n".join(header.split("\n")[1:])
    if has_encoding:
        header = re.sub(r"# -\*- coding:.*-\*-\n", "", header)
    
    # Handle module docstrings
    docstring_match = re.match(r'(#!/.*\n)?(# -\*- coding:.*-\*-\n)?(""".+?""")\n', content, re.DOTALL)
    
    if docstring_match:
        # Extract docstring content and add it to the description
        docstring = docstring_match.group(3).strip('"""').strip()
        description = docstring if docstring else description
        
        # Format the header with the updated description
        header = PYTHON_HEADER.format(date=CURRENT_DATE, description=description)
        
        # Remove shebang and encoding from header if they're already in the file
        if has_shebang:
            header = "\n".join(header.split("\n")[1:])
        if has_encoding:
            header = re.sub(r"# -\*- coding:.*-\*-\n", "", header)
        
        # Replace the docstring with the header
        if has_shebang or has_encoding:
            # Keep shebang and encoding
            prefix = ""
            if has_shebang:
                prefix += docstring_match.group(1)
            if has_encoding:
                prefix += docstring_match.group(2)
            content = prefix + header + content[docstring_match.end():]
        else:
            # Remove docstring and add header
            content = header + content[docstring_match.end():]
    else:
        # No docstring, just add header at the top
        content = header + "\n" + content
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Added header to {file_path}")

def add_header_to_sh_file(file_path: str) -> None:
    """Add header to a shell script file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Detect if file already has a header
    has_header = bool(re.search(r"# Copyright.*Lewis Guo", content))
    if has_header:
        print(f"File {file_path} already has a header. Skipping.")
        return
    
    # Detect if file starts with shebang
    has_shebang = content.startswith("#!/")
    
    # Get description for the file
    description = FILE_DESCRIPTIONS.get(file_path, f"Shell script for the MCP Kubernetes server: {os.path.basename(file_path)}")
    
    # Format the header
    header = SH_HEADER.format(date=CURRENT_DATE, description=description)
    
    # Remove shebang from header if it's already in the file
    if has_shebang:
        header = "\n".join(header.split("\n")[1:])
        
        # Extract the existing shebang
        shebang = content.split("\n")[0] + "\n"
        
        # Add header after shebang
        content = shebang + header + content[len(shebang):]
    else:
        # Add header at the top
        content = header + "\n" + content
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Added header to {file_path}")

def add_header_to_yaml_file(file_path: str) -> None:
    """Add header to a YAML file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Detect if file already has a header
    has_header = bool(re.search(r"# Copyright.*Lewis Guo", content))
    if has_header:
        print(f"File {file_path} already has a header. Skipping.")
        return
    
    # Get description for the file
    description = FILE_DESCRIPTIONS.get(file_path, f"YAML configuration for the MCP Kubernetes server: {os.path.basename(file_path)}")
    
    # Format the header
    header = YAML_HEADER.format(date=CURRENT_DATE, description=description)
    
    # Add header at the top
    content = header + "\n" + content
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Added header to {file_path}")

def add_header_to_dockerfile(file_path: str) -> None:
    """Add header to a Dockerfile."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Detect if file already has a header
    has_header = bool(re.search(r"# Copyright.*Lewis Guo", content))
    if has_header:
        print(f"File {file_path} already has a header. Skipping.")
        return
    
    # Get description for the file
    description = FILE_DESCRIPTIONS.get(file_path, "Dockerfile for building the MCP Kubernetes server container image.")
    
    # Format the header
    header = DOCKERFILE_HEADER.format(date=CURRENT_DATE, description=description)
    
    # Add header at the top
    content = header + "\n" + content
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Added header to {file_path}")

def main() -> None:
    """Main function."""
    # Root directory of the project
    root_dir = "."
    
    # Process Python files
    python_files = []
    
    # Find all Python files in the mcp_k8s_server directory
    for root, _, files in os.walk(os.path.join(root_dir, "mcp_k8s_server")):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    # Find all Python files in the tests directory
    for root, _, files in os.walk(os.path.join(root_dir, "tests")):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    # Find all Python files in the config directory
    for root, _, files in os.walk(os.path.join(root_dir, "config")):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    # Find Python files in the root directory
    for file in os.listdir(root_dir):
        if file.endswith(".py"):
            python_files.append(os.path.join(root_dir, file))
    
    # Process Python files
    print(f"Processing {len(python_files)} Python files...")
    for file in python_files:
        add_header_to_python_file(file)
    
    # Process shell script files
    sh_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".sh"):
                sh_files.append(os.path.join(root, file))
    
    print(f"Processing {len(sh_files)} shell script files...")
    for file in sh_files:
        add_header_to_sh_file(file)
    
    # Process YAML files
    yaml_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                yaml_files.append(os.path.join(root, file))
    
    print(f"Processing {len(yaml_files)} YAML files...")
    for file in yaml_files:
        add_header_to_yaml_file(file)
    
    # Process Dockerfiles
    dockerfiles = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file == "Dockerfile":
                dockerfiles.append(os.path.join(root, file))
    
    print(f"Processing {len(dockerfiles)} Dockerfiles...")
    for file in dockerfiles:
        add_header_to_dockerfile(file)
    
    print("Done!")

if __name__ == "__main__":
    main()
