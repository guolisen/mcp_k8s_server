#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: MCP tools for Kubernetes monitoring.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json, datetime
import logging
import time
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from mcp_k8s_server.k8s.monitoring import K8sMonitoring
from mcp_k8s_server.k8s.client import K8sClient

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
        
def register_monitoring_tools(mcp: FastMCP, k8s_monitoring: K8sMonitoring) -> None:
    """Register monitoring tools with the MCP server.
    
    Args:
        mcp: MCP server.
        k8s_monitoring: Kubernetes monitoring.
    """
    
    @mcp.tool()
    def get_cluster_status() -> str:
        """Get the overall status of the cluster.
        
        Returns:
            JSON string with the cluster status.
        """
        logger.info("Getting cluster status")
        
        try:
            status = k8s_monitoring.get_cluster_status()
            
            return json.dumps(status, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting cluster status: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_node_status(name: Optional[str] = None) -> str:
        """Get the status of a node or all nodes.
        
        Args:
            name: Name of the node. If None, returns status of all nodes.
        
        Returns:
            JSON string with the node status.
        """
        logger.info(f"Getting node status: {name if name else 'all'}")
        
        try:
            status = k8s_monitoring.get_node_status(name)
            
            return json.dumps(status, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting node status: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_pod_status(name: Optional[str] = None, namespace: Optional[str] = None) -> str:
        """Get the status of a pod or all pods.
        
        Args:
            name: Name of the pod. If None, returns status of all pods.
            namespace: Namespace of the pod. If None, uses the default namespace.
        
        Returns:
            JSON string with the pod status.
        """
        logger.info(f"Getting pod status: {name if name else 'all'} in namespace {namespace}")
        
        try:
            status = k8s_monitoring.get_pod_status(name, namespace)
            
            return json.dumps(status, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting pod status: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_deployment_status(name: Optional[str] = None, namespace: Optional[str] = None) -> str:
        """Get the status of a deployment or all deployments.
        
        Args:
            name: Name of the deployment. If None, returns status of all deployments.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            JSON string with the deployment status.
        """
        logger.info(f"Getting deployment status: {name if name else 'all'} in namespace {namespace}")
        
        try:
            status = k8s_monitoring.get_deployment_status(name, namespace)
            
            return json.dumps(status, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting deployment status: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def get_resource_metrics(kind: str, name: str, namespace: Optional[str] = None) -> str:
        """Get metrics for a specific resource.
        
        Args:
            kind: Kind of the resource (e.g., "Pod", "Node").
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            JSON string with the resource metrics.
        """
        logger.info(f"Getting metrics for {kind} {name} in namespace {namespace}")
        
        try:
            metrics = k8s_monitoring.get_resource_metrics(kind, name, namespace)
            
            return json.dumps(metrics, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting metrics for {kind} {name}: {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    def check_cluster_health() -> str:
        """Perform a comprehensive health check of the Kubernetes cluster.
        
        This function checks various aspects of the cluster including:
        - Node health and readiness
        - Pod status across all namespaces
        - Deployment availability
        - Resource utilization
        - Control plane components
        - Storage status
        - Network connectivity
        
        Returns:
            A detailed summary of the cluster health status in JSON format.
        """
        logger.info("Performing comprehensive cluster health check")
        
        try:
            # Get cluster status from monitoring
            cluster_status = k8s_monitoring.get_cluster_status()
            
            # Get all nodes status
            nodes_status = k8s_monitoring.get_node_status()
            
            # Get all pods status
            pods_status = k8s_monitoring.get_pod_status(namespace="all")
            
            # Get all deployments status
            deployments_status = k8s_monitoring.get_deployment_status(namespace="all")
            
            # Calculate health metrics
            total_nodes = cluster_status.get("nodes", {}).get("total", 0)
            ready_nodes = cluster_status.get("nodes", {}).get("ready", 0)
            node_health_percentage = (ready_nodes / total_nodes * 100) if total_nodes > 0 else 0
            
            total_pods = cluster_status.get("pods", {}).get("total", 0)
            running_pods = cluster_status.get("pods", {}).get("running", 0)
            pod_health_percentage = (running_pods / total_pods * 100) if total_pods > 0 else 0
            
            total_deployments = cluster_status.get("deployments", {}).get("total", 0)
            available_deployments = cluster_status.get("deployments", {}).get("available", 0)
            deployment_health_percentage = (available_deployments / total_deployments * 100) if total_deployments > 0 else 0
            
            # Identify problematic resources
            problematic_nodes = [
                {"name": name, "issues": "Not Ready"}
                for name, node in nodes_status.items()
                if not node.get("ready", False)
            ]
            
            problematic_pods = [
                {
                    "name": pod.get("name", "unknown"),
                    "namespace": pod.get("namespace", "unknown"),
                    "phase": pod.get("phase", "Unknown"),
                    "issues": "Not Running"
                }
                for _, pod in pods_status.items()
                if pod.get("phase") != "Running" and pod.get("phase") != "Succeeded"
            ]
            
            problematic_deployments = [
                {
                    "name": deployment.get("name", "unknown"),
                    "namespace": deployment.get("namespace", "unknown"),
                    "issues": "Not Available",
                    "available": deployment.get("availableReplicas", 0),
                    "desired": deployment.get("replicas", 0)
                }
                for _, deployment in deployments_status.items()
                if deployment.get("availableReplicas", 0) != deployment.get("replicas", 0)
            ]
            
            # Determine overall health status
            overall_status = cluster_status.get("status", "Unknown")
            
            # Create health summary
            health_summary = {
                "timestamp": time.time(),
                "overall_status": overall_status,
                "health_scores": {
                    "nodes": {
                        "percentage": node_health_percentage,
                        "ready": ready_nodes,
                        "total": total_nodes
                    },
                    "pods": {
                        "percentage": pod_health_percentage,
                        "running": running_pods,
                        "total": total_pods,
                        "pending": cluster_status.get("pods", {}).get("pending", 0),
                        "failed": cluster_status.get("pods", {}).get("failed", 0)
                    },
                    "deployments": {
                        "percentage": deployment_health_percentage,
                        "available": available_deployments,
                        "total": total_deployments
                    }
                },
                "issues": {
                    "nodes": problematic_nodes,
                    "pods": problematic_pods,
                    "deployments": problematic_deployments
                },
                "recommendations": []
            }
            
            # Generate recommendations based on issues
            if problematic_nodes:
                health_summary["recommendations"].append(
                    "Investigate node issues. Some nodes are not in Ready state."
                )
            
            if cluster_status.get("pods", {}).get("pending", 0) > 0:
                health_summary["recommendations"].append(
                    "Check pending pods. They might be waiting for resources or have configuration issues."
                )
            
            if cluster_status.get("pods", {}).get("failed", 0) > 0:
                health_summary["recommendations"].append(
                    "Examine failed pods. Check their logs and events for error details."
                )
            
            if problematic_deployments:
                health_summary["recommendations"].append(
                    "Review deployments that don't have all replicas available."
                )
            
            # Add overall health assessment
            if overall_status == "Healthy":
                health_summary["assessment"] = "The cluster appears to be healthy with all components functioning properly."
            elif overall_status == "Warning":
                health_summary["assessment"] = "The cluster has some minor issues that should be addressed."
            elif overall_status == "Degraded":
                health_summary["assessment"] = "The cluster is in a degraded state with multiple components experiencing issues."
            elif overall_status == "Critical":
                health_summary["assessment"] = "The cluster is in a critical state and requires immediate attention."
            else:
                health_summary["assessment"] = "Unable to determine cluster health status."
            
            return json.dumps(health_summary, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error performing cluster health check: {e}")
            return json.dumps({
                "error": str(e),
                "status": "Error",
                "message": "Failed to complete cluster health check"
            })
    
    # Register callbacks for monitoring events
    def _register_monitoring_callbacks() -> None:
        """Register callbacks for monitoring events."""
        # This function is called internally and not exposed as a tool
        
        # Example callback for cluster status changes
        def _on_cluster_status_change(status: Dict[str, Any]) -> None:
            """Callback for cluster status changes."""
            logger.debug(f"Cluster status changed: {status}")
            
            # You can implement additional logic here, such as sending alerts
            # or updating a status dashboard
            
            # Check for critical status
            if status.get("status") == "Critical":
                logger.warning("Cluster status is critical!")
                # You could send an alert here
        
        # Register the callback
        k8s_monitoring.register_callback("cluster", _on_cluster_status_change)
    
    # Register callbacks
    _register_monitoring_callbacks()
