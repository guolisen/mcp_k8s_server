# MCP Kubernetes Server System Overview

The MCP Kubernetes Server is a comprehensive implementation of the Model Context Protocol (MCP) designed to provide LLMs with access to Kubernetes cluster management, monitoring, and diagnostics capabilities.

## Architecture Overview

The system follows a layered architecture that separates concerns and provides a clean interface between components:

1. **MCP Protocol Layer** - Handles communication with LLM clients using the Model Context Protocol
2. **Resource & Tool Interfaces** - Exposes Kubernetes resources and operations through standardized interfaces
3. **Kubernetes Interface Layer** - Abstracts the interaction with Kubernetes through API client and kubectl wrapper
4. **Kubernetes Cluster** - The actual Kubernetes infrastructure being managed

## Key Components

### MCP Server Core
- **KubernetesMcpServer** - Central server component that initializes and coordinates all other components
- **MCP Protocol Handler** - Manages MCP protocol communication, request parsing, and response formatting
- **Configuration System** - Handles loading and parsing of configuration files for server settings

### Server Modes
- **stdio Mode** - Communicates through standard input/output streams (default)
- **Network Mode** - Binds to an IP address and port for network communication

### Resource Interface
- **BaseResourceHandler** - Abstract base class for all resource handlers
- **ResourceUriParser** - Parses and validates Kubernetes resource URIs
- **Resource Handlers** - Specialized handlers for different Kubernetes resource types (Nodes, Deployments, etc.)

### Tool Interface
- **Operations Module** - Tools for performing cluster operations (scaling, restarting, etc.)
- **Monitoring Module** - Tools for monitoring cluster status and resource usage
- **Status Module** - Tools for checking health and diagnosing issues

### Kubernetes Interface
- **KubernetesApiClient** - Direct interface to Kubernetes API using the official client
- **KubectlWrapper** - Command-line interface using kubectl commands

## Communication Flows

### Resource Request Flow
1. LLM Client sends a resource request (e.g., `kubernetes://nodes`)
2. MCP Server parses the URI and delegates to the appropriate Resource Handler
3. Resource Handler uses the Kubernetes Interface to retrieve data
4. Data is formatted and returned to the client

### Tool Request Flow
1. LLM Client sends a tool request (e.g., `scale_deployment`)
2. MCP Server delegates to the appropriate Tool Handler
3. Tool Handler uses the Kubernetes Interface to perform the operation
4. Result is formatted and returned to the client

### Monitoring Flow
1. LLM Client requests monitoring information (e.g., `get_cluster_health`)
2. MCP Server delegates to the Monitoring Tool
3. Monitoring Tool collects data from multiple sources
4. Data is aggregated, formatted, and returned to the client

## Design Principles

1. **Separation of Concerns** - Each component has a single responsibility
2. **Abstraction** - Kubernetes complexity is hidden behind simple interfaces
3. **Extensibility** - New resources and tools can be easily added
4. **Error Handling** - Robust error handling at all levels
5. **Security** - Uses existing Kubernetes authentication mechanisms

## Implementation Details

The server is implemented in Python, using:
- MCP SDK for protocol handling
- Official Kubernetes Python client for API access
- Subprocess module for kubectl command execution
- PyYAML for configuration file parsing
- Standard Python libraries for utility functions

## Configuration

The server can be configured using:
- YAML configuration files for persistent settings
- Command-line arguments for overriding configuration
- Environment variables for sensitive information

Configuration options include:
- Server binding settings (IP, port, mode)
- Kubernetes connection settings
- Logging configuration

All diagrams in this directory provide detailed views of the system architecture from different perspectives:
- `architecture.puml` - High-level system architecture
- `component_diagram.puml` - Logical component structure
- `class_diagram.puml` - Detailed class structure
- `sequence_diagram.puml` - Interaction flows
- `data_flow_diagram.puml` - Data movement through the system
