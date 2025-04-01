from setuptools import setup, find_packages

setup(
    name="mcp_k8s_server",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "modelcontextprotocol==0.1.0",
        "kubernetes==29.0.0",
        "PyYAML==6.0.1",
        "prometheus-client==0.17.1",
        "tabulate==0.9.0",
        "rich==13.6.0",
    ],
    python_requires=">=3.8",
    description="MCP server for Kubernetes cluster management",
    author="Cline",
    entry_points={
        "console_scripts": [
            "mcp-k8s-server=mcp_k8s_server.server:main",
        ],
    },
)
