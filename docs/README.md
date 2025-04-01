# MCP Kubernetes Server Architecture Diagrams

This directory contains PlantUML diagram scripts that visualize the architecture and design of the MCP Kubernetes Server.

## Diagrams

1. **Architecture Overview** (`architecture.puml`) - High-level system architecture showing main components and their interactions
2. **Class Diagram** (`class_diagram.puml`) - Detailed class structure showing relationships between classes
3. **Sequence Diagram** (`sequence_diagram.puml`) - Flow of interactions between components for key operations
4. **Component Diagram** (`component_diagram.puml`) - Logical component structure showing dependencies and interfaces

## Generating Diagrams

These are PlantUML source files. To generate the actual diagrams, you can use one of the following methods:

### Online PlantUML Server

1. Visit the [PlantUML Online Server](https://www.plantuml.com/plantuml/uml/)
2. Copy the content of any .puml file and paste it into the text area
3. The diagram will be rendered automatically

### VS Code Extension

If you're using VS Code, you can install the "PlantUML" extension:

1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search for "PlantUML"
3. Install the extension by jebbs
4. Open any .puml file and use Alt+D to preview the diagram

### Local Installation

To render diagrams locally:

1. Install Java Runtime Environment (JRE)
2. Install PlantUML jar file
3. Run: `java -jar plantuml.jar file.puml`

## Design Overview

### Architecture

The MCP Kubernetes Server provides a bridge between LLM clients and Kubernetes clusters using the Model Context Protocol. It exposes Kubernetes resources and operations through standardized interfaces.

### Main Components

- **KubernetesMcpServer**: Central server component managing all interactions
- **Kubernetes API Interface**: Provides direct and kubectl-based access to the K8s API
- **Resource Handlers**: Handle resource requests via URI-based interface
- **Tool Handlers**: Provide operational tools for cluster management and monitoring

### Communication Flows

- **Resource Flow**: LLM Client → MCP Server → Resource Handler → K8s API → K8s Cluster
- **Tool Flow**: LLM Client → MCP Server → Tool Handler → K8s API → K8s Cluster
- **Monitoring Flow**: LLM Client → MCP Server → Monitoring Tool → K8s API → K8s Cluster
