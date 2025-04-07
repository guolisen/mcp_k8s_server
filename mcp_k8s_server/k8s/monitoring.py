#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Kubernetes monitoring module.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import time
import threading
from typing import Any, Dict, List, Optional, Set, Tuple, Callable

from kubernetes import client
from kubernetes.client.rest import ApiException

from mcp_k8s_server.k8s.client import K8sClient
from mcp_k8s_server.config import MonitoringConfig

logger = logging.getLogger(__name__)


class K8sMonitoring:
    """Kubernetes monitoring."""

    def __init__(self, k8s_client: K8sClient, monitoring_config: MonitoringConfig):
        """Initialize the Kubernetes monitoring.
        
        Args:
            k8s_client: Kubernetes client.
            monitoring_config: Monitoring configuration.
        """
        self.client = k8s_client
        self.config = monitoring_config
        self.metrics_api = None
        self._init_metrics_api()
        
        self._running = False
        self._monitor_thread = None
        self._callbacks: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {
            "pods": [],
            "nodes": [],
            "deployments": [],
            "cluster": [],
        }
        
        # Cache for resource status
        self._resource_status: Dict[str, Dict[str, Dict[str, Any]]] = {
            "pods": {},
            "nodes": {},
            "deployments": {},
        }
        
        # Cache for cluster status
        self._cluster_status: Dict[str, Any] = {
            "timestamp": 0,
            "status": "Unknown",
            "nodes": {
                "total": 0,
                "ready": 0,
            },
            "pods": {
                "total": 0,
                "running": 0,
                "pending": 0,
                "failed": 0,
                "succeeded": 0,
                "unknown": 0,
            },
            "deployments": {
                "total": 0,
                "available": 0,
                "unavailable": 0,
            },
        }

    def _init_metrics_api(self) -> None:
        """Initialize the metrics API client."""
        try:
            # Try to load the metrics API
            self.metrics_api = client.CustomObjectsApi()
            logger.info("Metrics API initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize metrics API: {e}")
            self.metrics_api = None

    def start_monitoring(self) -> None:
        """Start monitoring."""
        if not self.config.enabled:
            logger.info("Monitoring is disabled")
            return
        
        if self._running:
            logger.warning("Monitoring is already running")
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Started monitoring")

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        if not self._running:
            logger.warning("Monitoring is not running")
            return
        
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
        logger.info("Stopped monitoring")

    def register_callback(self, resource_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for a resource type.
        
        Args:
            resource_type: Resource type (pods, nodes, deployments, cluster).
            callback: Callback function that takes a status dictionary.
        """
        if resource_type not in self._callbacks:
            logger.warning(f"Unknown resource type: {resource_type}")
            return
        
        self._callbacks[resource_type].append(callback)
        logger.info(f"Registered callback for {resource_type}")

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get the current cluster status.
        
        Returns:
            Dictionary with cluster status.
        """
        return self._cluster_status.copy()

    def get_node_status(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of a node or all nodes.
        
        Args:
            name: Name of the node. If None, returns status of all nodes.
        
        Returns:
            Dictionary with node status.
        """
        if name:
            return self._resource_status["nodes"].get(name, {})
        return {name: status for name, status in self._resource_status["nodes"].items()}

    def get_pod_status(self, name: Optional[str] = None, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of a pod or all pods.
        
        Args:
            name: Name of the pod. If None, returns status of all pods.
            namespace: Namespace of the pod. If None, uses the default namespace.
        
        Returns:
            Dictionary with pod status.
        """
        namespace = namespace or self.client.config.namespace
        
        if name:
            key = f"{namespace}/{name}"
            return self._resource_status["pods"].get(key, {})
        
        if namespace == "all":
            return {name: status for name, status in self._resource_status["pods"].items()}
        
        return {
            name.split("/")[1]: status
            for name, status in self._resource_status["pods"].items()
            if name.startswith(f"{namespace}/")
        }

    def get_deployment_status(self, name: Optional[str] = None, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get the status of a deployment or all deployments.
        
        Args:
            name: Name of the deployment. If None, returns status of all deployments.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            Dictionary with deployment status.
        """
        namespace = namespace or self.client.config.namespace
        
        if name:
            key = f"{namespace}/{name}"
            return self._resource_status["deployments"].get(key, {})
        
        if namespace == "all":
            return {name: status for name, status in self._resource_status["deployments"].items()}
        
        return {
            name.split("/")[1]: status
            for name, status in self._resource_status["deployments"].items()
            if name.startswith(f"{namespace}/")
        }

    def get_resource_metrics(self, kind: str, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for a specific resource.
        
        Args:
            kind: Kind of the resource (e.g., "Pod", "Node").
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            Dictionary with resource metrics.
        """
        # We don't need to check for metrics_api availability here since our implementation now uses
        # the client's list_custom_resources method which is more robust
        
        try:
            namespace = namespace or self.client.config.namespace
            
            if kind.lower() == "pod":
                return self._get_pod_metrics(name, namespace)
            elif kind.lower() == "node":
                return self._get_node_metrics(name)
            else:
                return {"error": f"Unsupported resource type for metrics: {kind}"}
        except ApiException as e:
            logger.error(f"Error getting metrics for {kind} {name}: {e}")
            return {"error": f"Error getting metrics: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error getting metrics for {kind} {name}: {e}")
            return {"error": f"Unexpected error: {e}"}

    def _monitor_loop(self) -> None:
        """Monitoring loop."""
        while self._running:
            try:
                # Update resource status
                if "pods" in self.config.resources:
                    self._update_pods_status()
                
                if "nodes" in self.config.resources:
                    self._update_nodes_status()
                
                if "deployments" in self.config.resources:
                    self._update_deployments_status()
                
                # Update cluster status
                self._update_cluster_status()
                
                # Sleep for the configured interval
                time.sleep(self.config.interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Sleep for a shorter interval on error

    def _update_pods_status(self) -> None:
        """Update the status of all pods."""
        try:
            # Get all pods
            pods = self.client.get_pods(namespace="all")
            
            # Update the status cache
            new_status = {}
            for pod in pods:
                name = pod["name"]
                namespace = pod["namespace"]
                key = f"{namespace}/{name}"
                status = pod.get("status", {})
                phase = status.get("phase", "Unknown")
                
                # Extract container statuses
                container_statuses = []
                cs = status.get("container_statuses", [])
                if cs != None:
                    for container in status.get("container_statuses", []):
                        container_status = {
                            "name": container.get("name"),
                            "ready": container.get("ready", False),
                            "restartCount": container.get("restart_count", 0),
                            "state": next(iter(container.get("state", {}).keys()), "unknown"),
                        }
                        container_statuses.append(container_status)
                
                # Build the pod status
                pod_status = {
                    "name": name,
                    "namespace": namespace,
                    "phase": phase,
                    "conditions": status.get("conditions", []),
                    "containerStatuses": container_statuses,
                    "podIP": status.get("pod_ip"),
                    "hostIP": status.get("host_ip"),
                    "startTime": status.get("start_time"),
                    "qosClass": status.get("qos_class"),
                }
                
                # Add metrics
                try:
                    metrics = self._get_pod_metrics(name, namespace)
                    pod_status["metrics"] = metrics
                except Exception as e:
                    logger.debug(f"Error getting metrics for pod {name}: {e}")
                
                new_status[key] = pod_status
            
            # Update the cache
            self._resource_status["pods"] = new_status
            
            # Notify callbacks
            for callback in self._callbacks["pods"]:
                try:
                    callback(new_status)
                except Exception as e:
                    logger.error(f"Error in pod status callback: {e}")
        except Exception as e:
            logger.error(f"Error updating pod status: {e}")

    def _update_nodes_status(self) -> None:
        """Update the status of all nodes."""
        try:
            # Get all nodes
            nodes = self.client.get_nodes()
            
            # Update the status cache
            new_status = {}
            for node in nodes:
                name = node["name"]
                
                status = node.get("status", {})
                conditions = status.get("conditions", [])
                
                # Check if the node is ready
                ready = False
                for condition in conditions:
                    if condition.get("type") == "Ready":
                        ready = condition.get("status") == "True"
                        break
                
                # Build the node status
                node_status = {
                    "name": name,
                    "ready": ready,
                    "conditions": conditions,
                    "addresses": status.get("addresses", []),
                    "capacity": status.get("capacity", {}),
                    "allocatable": status.get("allocatable", {}),
                    "architecture": status.get("node_info", {}).get("architecture"),
                    "kernelVersion": status.get("node_info", {}).get("kernel_version"),
                    "osImage": status.get("node_info", {}).get("os_image"),
                    "containerRuntimeVersion": status.get("node_info", {}).get("container_runtime_version"),
                    "kubeletVersion": status.get("node_info", {}).get("kubelet_version"),
                }
                
                # Add metrics
                try:
                    metrics = self._get_node_metrics(name)
                    node_status["metrics"] = metrics
                except Exception as e:
                    logger.debug(f"Error getting metrics for node {name}: {e}")
                
                new_status[name] = node_status
            
            # Update the cache
            self._resource_status["nodes"] = new_status
            
            # Notify callbacks
            for callback in self._callbacks["nodes"]:
                try:
                    callback(new_status)
                except Exception as e:
                    logger.error(f"Error in node status callback: {e}")
        except Exception as e:
            logger.error(f"Error updating node status: {e}")

    def _update_deployments_status(self) -> None:
        """Update the status of all deployments."""
        try:
            # Get all deployments
            deployments = self.client.get_deployments(namespace="all")
            
            # Update the status cache
            new_status = {}
            for deployment in deployments:
                name = deployment["name"]
                namespace = deployment["namespace"]
                key = f"{namespace}/{name}"
                
                status = deployment.get("status", {})
                spec = deployment.get("spec", {})
                
                # Build the deployment status
                deployment_status = {
                    "name": name,
                    "namespace": namespace,
                    "replicas": status.get("replicas", 0),
                    "availableReplicas": status.get("available_replicas", 0),
                    "unavailableReplicas": status.get("unavailable_replicas", 0),
                    "updatedReplicas": status.get("updated_replicas", 0),
                    "readyReplicas": status.get("ready_replicas", 0),
                    "conditions": status.get("conditions", []),
                    "strategy": spec.get("strategy", {}).get("type", "RollingUpdate"),
                    "minReadySeconds": spec.get("min_ready_seconds", 0),
                    "revisionHistoryLimit": spec.get("revision_history_limit", 10),
                }
                
                new_status[key] = deployment_status
            
            # Update the cache
            self._resource_status["deployments"] = new_status
            
            # Notify callbacks
            for callback in self._callbacks["deployments"]:
                try:
                    callback(new_status)
                except Exception as e:
                    logger.error(f"Error in deployment status callback: {e}")
        except Exception as e:
            logger.error(f"Error updating deployment status: {e}")

    def _update_cluster_status(self) -> None:
        """Update the cluster status."""
        try:
            # Count nodes
            nodes_total = len(self._resource_status["nodes"])
            nodes_ready = sum(1 for node in self._resource_status["nodes"].values() if node.get("ready", False))
            
            # Count pods
            pods_total = len(self._resource_status["pods"])
            pods_running = sum(1 for pod in self._resource_status["pods"].values() if pod.get("phase") == "Running")
            pods_pending = sum(1 for pod in self._resource_status["pods"].values() if pod.get("phase") == "Pending")
            pods_failed = sum(1 for pod in self._resource_status["pods"].values() if pod.get("phase") == "Failed")
            pods_succeeded = sum(1 for pod in self._resource_status["pods"].values() if pod.get("phase") == "Succeeded")
            pods_unknown = pods_total - pods_running - pods_pending - pods_failed - pods_succeeded
            
            # Count deployments
            deployments_total = len(self._resource_status["deployments"])
            deployments_available = sum(
                1 for deployment in self._resource_status["deployments"].values()
                if deployment.get("availableReplicas", 0) == deployment.get("replicas", 0)
            )
            deployments_unavailable = deployments_total - deployments_available
            
            # Determine cluster status
            status = "Healthy"
            if nodes_ready < nodes_total:
                status = "Degraded"
            if nodes_ready == 0:
                status = "Critical"
            if pods_failed > 0 or pods_pending > 0:
                status = "Warning"
            
            # Build the cluster status
            cluster_status = {
                "timestamp": time.time(),
                "status": status,
                "nodes": {
                    "total": nodes_total,
                    "ready": nodes_ready,
                },
                "pods": {
                    "total": pods_total,
                    "running": pods_running,
                    "pending": pods_pending,
                    "failed": pods_failed,
                    "succeeded": pods_succeeded,
                    "unknown": pods_unknown,
                },
                "deployments": {
                    "total": deployments_total,
                    "available": deployments_available,
                    "unavailable": deployments_unavailable,
                },
            }
            
            # Update the cache
            self._cluster_status = cluster_status
            
            # Notify callbacks
            for callback in self._callbacks["cluster"]:
                try:
                    callback(cluster_status)
                except Exception as e:
                    logger.error(f"Error in cluster status callback: {e}")
        except Exception as e:
            logger.error(f"Error updating cluster status: {e}")

    def _get_pod_metrics(self, name: str, namespace: str) -> Dict[str, Any]:
        """Get metrics for a pod.
        
        Args:
            name: Name of the pod.
            namespace: Namespace of the pod.
        
        Returns:
            Dictionary with pod metrics.
        """
        try:
            # Use list_custom_resources instead of direct get_namespaced_custom_object
            metrics_list = self.client.list_custom_resources(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="pods",
                namespace=namespace
            )
            
            # Find the specific pod in the list
            pod_metrics = None
            for item in metrics_list:
                if item.get("metadata", {}).get("name") == name:
                    pod_metrics = item
                    break
                    
            if not pod_metrics:
                logger.debug(f"Metrics not found for pod {name}")
                return {}
                
            # Extract container metrics
            container_metrics = {}
            for container in pod_metrics.get("containers", []):
                container_name = container.get("name")
                usage = container.get("usage", {})
                
                cpu = usage.get("cpu", "0")
                memory = usage.get("memory", "0")
                
                # Convert CPU to millicores
                if cpu.endswith("n"):
                    cpu_millicores = int(cpu[:-1]) / 1000000
                elif cpu.endswith("u"):
                    cpu_millicores = int(cpu[:-1]) / 1000
                elif cpu.endswith("m"):
                    cpu_millicores = int(cpu[:-1])
                else:
                    cpu_millicores = int(cpu) * 1000
                
                # Convert memory to MiB
                if memory.endswith("Ki"):
                    memory_mib = int(memory[:-2]) / 1024
                elif memory.endswith("Mi"):
                    memory_mib = int(memory[:-2])
                elif memory.endswith("Gi"):
                    memory_mib = int(memory[:-2]) * 1024
                else:
                    memory_mib = int(memory) / (1024 * 1024)
                
                container_metrics[container_name] = {
                    "cpu": {
                        "raw": cpu,
                        "millicores": cpu_millicores,
                    },
                    "memory": {
                        "raw": memory,
                        "mib": memory_mib,
                    },
                }
            
            return {
                "timestamp": pod_metrics.get("timestamp"),
                "window": pod_metrics.get("window"),
                "containers": container_metrics,
            }
        except ApiException as e:
            if e.status == 404:
                logger.debug(f"Metrics not found for pod {name}")
                return {}
            logger.warning(f"Error fetching metrics for pod {name}: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Unexpected error fetching metrics for pod {name}: {e}")
            return {}

    def _get_node_metrics(self, name: str) -> Dict[str, Any]:
        """Get metrics for a node.
        
        Args:
            name: Name of the node.
        
        Returns:
            Dictionary with node metrics.
        """
        try:
            # Use list_custom_resources instead of direct get_cluster_custom_object
            metrics_list = self.client.list_custom_resources(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes",
                namespace=None  # Nodes are cluster-scoped, not namespaced
            )
            
            # Find the specific node in the list
            node_metrics = None
            for item in metrics_list:
                if item.get("metadata", {}).get("name") == name:
                    node_metrics = item
                    break
                    
            if not node_metrics:
                logger.debug(f"Metrics not found for node {name}")
                return {}
            
            usage = node_metrics.get("usage", {})
            
            cpu = usage.get("cpu", "0")
            memory = usage.get("memory", "0")
            
            # Convert CPU to millicores
            if cpu.endswith("n"):
                cpu_millicores = int(cpu[:-1]) / 1000000
            elif cpu.endswith("u"):
                cpu_millicores = int(cpu[:-1]) / 1000
            elif cpu.endswith("m"):
                cpu_millicores = int(cpu[:-1])
            else:
                cpu_millicores = int(cpu) * 1000
            
            # Convert memory to MiB
            if memory.endswith("Ki"):
                memory_mib = int(memory[:-2]) / 1024
            elif memory.endswith("Mi"):
                memory_mib = int(memory[:-2])
            elif memory.endswith("Gi"):
                memory_mib = int(memory[:-2]) * 1024
            else:
                memory_mib = int(memory) / (1024 * 1024)
            
            return {
                "timestamp": node_metrics.get("timestamp"),
                "window": node_metrics.get("window"),
                "cpu": {
                    "raw": cpu,
                    "millicores": cpu_millicores,
                },
                "memory": {
                    "raw": memory,
                    "mib": memory_mib,
                },
            }
        except ApiException as e:
            if e.status == 404:
                logger.debug(f"Metrics not found for node {name}")
                return {}
            logger.warning(f"Error fetching metrics for node {name}: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Unexpected error fetching metrics for node {name}: {e}")
            return {}
