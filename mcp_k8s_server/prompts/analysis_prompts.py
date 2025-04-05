#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: MCP prompts for Kubernetes analysis.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

logger = logging.getLogger(__name__)


def register_analysis_prompts(mcp: FastMCP) -> None:
    """Register analysis prompts with the MCP server.
    
    Args:
        mcp: MCP server.
    """
    
    @mcp.prompt()
    def analyze_cluster_status(context: Optional[str] = None) -> List[PromptMessage]:
        """Create a prompt for analyzing cluster status.
        
        Args:
            context: Optional context information.
        
        Returns:
            List of prompt messages.
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.append(
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Here is the Kubernetes cluster status information:\n\n{context}"
                    )
                )
            )
        
        # Add the main prompt
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""Please analyze the Kubernetes cluster status and provide insights on the following:

1. Overall cluster health assessment
2. Node status and resource utilization
3. Pod distribution and health
4. Deployment status and availability
5. Potential issues or bottlenecks
6. Recommendations for improvement

Please provide a comprehensive analysis with specific details from the provided information."""
                )
            )
        )
        
        return messages
    
    @mcp.prompt()
    def troubleshoot_pod_issues(context: Optional[str] = None) -> List[PromptMessage]:
        """Create a prompt for troubleshooting pod issues.
        
        Args:
            context: Optional context information.
        
        Returns:
            List of prompt messages.
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.append(
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Here is the information about the problematic pod:\n\n{context}"
                    )
                )
            )
        
        # Add the main prompt
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""Please help troubleshoot the issues with this Kubernetes pod by analyzing:

1. Current pod status and phase
2. Container statuses and restart counts
3. Pod conditions and events
4. Resource utilization and limits
5. Common failure patterns that match these symptoms
6. Step-by-step troubleshooting recommendations
7. Potential solutions to resolve the issues

Please be specific and provide actionable recommendations based on the information provided."""
                )
            )
        )
        
        return messages
    
    @mcp.prompt()
    def analyze_resource_usage(context: Optional[str] = None) -> List[PromptMessage]:
        """Create a prompt for analyzing resource usage.
        
        Args:
            context: Optional context information.
        
        Returns:
            List of prompt messages.
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.append(
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Here is the resource usage information for the Kubernetes cluster:\n\n{context}"
                    )
                )
            )
        
        # Add the main prompt
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""Please analyze the resource usage in this Kubernetes cluster and provide insights on:

1. Overall resource utilization (CPU, memory, storage)
2. Nodes with high resource usage or pressure
3. Pods or deployments consuming the most resources
4. Resource efficiency and potential waste
5. Resource bottlenecks or constraints
6. Recommendations for optimizing resource allocation
7. Scaling suggestions based on current usage patterns

Please provide a detailed analysis with specific metrics and actionable recommendations."""
                )
            )
        )
        
        return messages
    
    @mcp.prompt()
    def security_assessment(context: Optional[str] = None) -> List[PromptMessage]:
        """Create a prompt for security assessment.
        
        Args:
            context: Optional context information.
        
        Returns:
            List of prompt messages.
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.append(
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Here is the information about the Kubernetes resources for security assessment:\n\n{context}"
                    )
                )
            )
        
        # Add the main prompt
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""Please perform a security assessment of the Kubernetes resources and provide insights on:

1. Potential security vulnerabilities or misconfigurations
2. Security best practices that are not being followed
3. Pod security context and privilege settings
4. Network policies and exposure
5. Secret management practices
6. RBAC configuration and permissions
7. Container image security considerations
8. Recommendations for improving the security posture

Please provide a comprehensive assessment with specific findings and actionable security recommendations."""
                )
            )
        )
        
        return messages
    
    @mcp.prompt()
    def performance_optimization(context: Optional[str] = None) -> List[PromptMessage]:
        """Create a prompt for performance optimization.
        
        Args:
            context: Optional context information.
        
        Returns:
            List of prompt messages.
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.append(
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Here is the information about the Kubernetes resources for performance optimization:\n\n{context}"
                    )
                )
            )
        
        # Add the main prompt
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""Please analyze the performance of the Kubernetes resources and provide optimization recommendations:

1. Current performance bottlenecks or constraints
2. Resource allocation efficiency
3. Pod scheduling and placement optimization
4. Network performance considerations
5. Storage performance analysis
6. Application-specific optimizations
7. Scaling strategies for improved performance
8. Specific configuration changes to enhance performance

Please provide a detailed analysis with specific performance metrics and actionable optimization recommendations."""
                )
            )
        )
        
        return messages
    
    @mcp.prompt()
    def cost_optimization(context: Optional[str] = None) -> List[PromptMessage]:
        """Create a prompt for cost optimization.
        
        Args:
            context: Optional context information.
        
        Returns:
            List of prompt messages.
        """
        messages = []
        
        # Add context if provided
        if context:
            messages.append(
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Here is the information about the Kubernetes resources for cost optimization:\n\n{context}"
                    )
                )
            )
        
        # Add the main prompt
        messages.append(
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""Please analyze the Kubernetes resources from a cost optimization perspective and provide recommendations:

1. Resource allocation efficiency and potential waste
2. Overprovisioned resources that could be reduced
3. Underutilized nodes or pods
4. Opportunities for using spot instances or preemptible VMs
5. Autoscaling configuration improvements
6. Namespace and label-based cost allocation
7. Storage class and PVC optimization
8. Specific changes to reduce cloud infrastructure costs

Please provide a comprehensive analysis with specific cost-saving opportunities and actionable recommendations."""
                )
            )
        )
        
        return messages
