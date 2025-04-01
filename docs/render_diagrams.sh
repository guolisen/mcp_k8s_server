#!/bin/bash
# Script to generate diagram URLs for PlantUML online server

# Base URL for PlantUML server
PLANTUML_SERVER="https://www.plantuml.com/plantuml/uml"

# Function to encode PlantUML content for URL
encode_for_url() {
    # This is a simplified version; the actual PlantUML server uses a more complex encoding
    # For demonstration purposes, we'll just create the command to open the URL
    echo "To view this diagram online, copy the content of $1 and paste it into:"
    echo "$PLANTUML_SERVER"
    echo ""
}

# Print header
echo "========================================"
echo "MCP Kubernetes Server Diagram Renderer"
echo "========================================"
echo ""
echo "Use these commands to view the diagrams online:"
echo ""

# Process each diagram
for diagram in architecture.puml class_diagram.puml sequence_diagram.puml component_diagram.puml; do
    if [ -f "$diagram" ]; then
        echo "## $diagram ##"
        encode_for_url "$diagram"
        echo ""
    fi
done

echo "Alternatively, you can install a PlantUML viewer extension in your IDE or use:"
echo "- VS Code: PlantUML extension by jebbs"
echo "- IntelliJ: PlantUML integration plugin"
echo "- Online: $PLANTUML_SERVER"
