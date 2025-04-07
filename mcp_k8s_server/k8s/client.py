#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Kubernetes client wrapper.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

from mcp_k8s_server.config import KubernetesConfig

logger = logging.getLogger(__name__)


def prepareKubeConfig(config_path: Optional[str] = None, context: Optional[str] = None):
    """Prepare Kubernetes configuration.
    
    Args:
        config_path: Path to the kubeconfig file. If None, uses the default path.
        context: Kubernetes context to use. If None, uses the current context.
    
    Returns:
        Tuple of (CoreV1Api, Configuration)
    """
    configuration = client.Configuration()
    try:
        config.load_incluster_config(client_configuration=configuration)
        logger.info("Using in-cluster Kubernetes configuration")
    except config.ConfigException:
        # Fall back to kubeconfig
        if not config_path:
            config_path = os.path.expanduser("~/.kube/config")
        
        logger.info(f"Using kubeconfig from {config_path}")
        config.load_kube_config(
            config_file=config_path,
            context=None,
            client_configuration=configuration
        )
    
    configuration.verify_ssl = False
    v1 = client.CoreV1Api(client.ApiClient(configuration))
    return v1, configuration

class K8sClient:
    """Kubernetes client wrapper."""

    def __init__(self, k8s_config: KubernetesConfig):
        """Initialize the Kubernetes client.
        
        Args:
            k8s_config: Kubernetes configuration.
        """
        self.config = k8s_config
        self.core_v1_api = None
        self.apps_v1_api = None
        self.batch_v1_api = None
        self.networking_v1_api = None
        self.storage_v1_api = None
        self.custom_objects_api = None
        self.configuration = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the Kubernetes client."""
        # Use prepareKubeConfig to get the configuration
        config_path = self._get_kubeconfig_path()
        v1, configuration = prepareKubeConfig(config_path=config_path, context=self.config.context)
        self.configuration = configuration
        
        # Initialize API clients with the shared configuration
        api_client = client.ApiClient(configuration)
        self.core_v1_api = v1  # Already initialized by prepareKubeConfig
        self.apps_v1_api = client.AppsV1Api(api_client)
        self.batch_v1_api = client.BatchV1Api(api_client)
        self.networking_v1_api = client.NetworkingV1Api(api_client)
        self.storage_v1_api = client.StorageV1Api(api_client)
        self.custom_objects_api = client.CustomObjectsApi(api_client)
        
    def _get_kubeconfig_path(self) -> str:
        """Get the path to the kubeconfig file.
        
        Returns:
            Path to the kubeconfig file.
        """
        if self.config.config_path:
            return self.config.config_path
        
        # Default to ~/.kube/config
        return os.path.expanduser("~/.kube/config")

    def list_custom_resources(self, group: str, version: str, plural: str, 
                             namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """List custom resources.
        
        Args:
            group: API group of the custom resource.
            version: API version of the custom resource.
            plural: Plural name of the custom resource.
            namespace: Namespace of the custom resource. If None, uses the default namespace.
        
        Returns:
            List of custom resources.
        """
        return []
        try:
            namespace = namespace or self.config.namespace
            logger.info(f"Listing custom resources: {group}/{version}/{plural} in namespace {namespace}")
            
            with client.ApiClient(self.configuration) as api_client:
                api_instance = client.CustomObjectsApi(api_client)
                try:
                    if namespace == "all" or namespace is None:
                        api_response = api_instance.list_cluster_custom_object(group, version, plural)
                    else:
                        api_response = api_instance.list_namespaced_custom_object(
                            group, version, namespace, plural
                        )
                    return api_response.get("items", [])
                except ApiException as e:
                    logger.error(f"Exception when calling CustomObjectsApi to list resources: {e}")
                    return []
        except Exception as e:
            logger.error(f"Error listing custom resources: {e}")
            return []

    def get_custom_resource(self, group: str, version: str, plural: str, name: str, 
                           namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a custom resource.
        
        Args:
            group: API group of the custom resource.
            version: API version of the custom resource.
            plural: Plural name of the custom resource.
            name: Name of the custom resource.
            namespace: Namespace of the custom resource. If None, uses the default namespace.
        
        Returns:
            Custom resource or None if not found.
        """
        try:
            namespace = namespace or self.config.namespace
            logger.info(f"Getting custom resource: {group}/{version}/{plural}/{name} in namespace {namespace}")
            
            with client.ApiClient(self.configuration) as api_client:
                api_instance = client.CustomObjectsApi(api_client)
                try:
                    if namespace == "all" or namespace is None:
                        api_response = api_instance.get_cluster_custom_object(group, version, plural, name)
                    else:
                        api_response = api_instance.get_namespaced_custom_object(
                            group, version, namespace, plural, name
                        )
                    return api_response
                except ApiException as e:
                    logger.error(f"Exception when calling CustomObjectsApi: {e}")
                    return None
        except Exception as e:
            logger.error(f"Error getting custom resource: {e}")
            return None

    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces.
        
        Returns:
            List of namespaces.
        """
        try:
            namespaces = self.core_v1_api.list_namespace()
            return [self._extract_resource_info(ns) for ns in namespaces.items]
        except ApiException as e:
            logger.error(f"Error getting namespaces: {e}")
            return []

    def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pods in a namespace.
        
        Args:
            namespace: Namespace to get pods from. If None, uses the default namespace.
        
        Returns:
            List of pods.
        """
        try:
            namespace = namespace or self.config.namespace
            if namespace == "all":
                pods = self.core_v1_api.list_pod_for_all_namespaces()
            else:
                pods = self.core_v1_api.list_namespaced_pod(namespace)
            return [self._extract_resource_info(pod) for pod in pods.items]
        except ApiException as e:
            logger.error(f"Error getting pods: {e}")
            return []

    def get_pod(self, name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a pod by name.
        
        Args:
            name: Name of the pod.
            namespace: Namespace of the pod. If None, uses the default namespace.
        
        Returns:
            Pod information or None if not found.
        """
        try:
            namespace = namespace or self.config.namespace
            pod = self.core_v1_api.read_namespaced_pod(name, namespace)
            return self._extract_resource_info(pod, detailed=True)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Pod {name} not found in namespace {namespace}")
            else:
                logger.error(f"Error getting pod {name}: {e}")
            return None

    def get_pod_logs(self, name: str, namespace: Optional[str] = None, container: Optional[str] = None, 
                     tail_lines: int = 100) -> str:
        """Get logs for a pod.
        
        Args:
            name: Name of the pod.
            namespace: Namespace of the pod. If None, uses the default namespace.
            container: Name of the container. If None, uses the first container.
            tail_lines: Number of lines to return from the end of the logs.
        
        Returns:
            Pod logs.
        """
        try:
            namespace = namespace or self.config.namespace
            return self.core_v1_api.read_namespaced_pod_log(
                name, namespace, container=container, tail_lines=tail_lines
            )
        except ApiException as e:
            logger.error(f"Error getting logs for pod {name}: {e}")
            return f"Error getting logs: {e}"

    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all deployments in a namespace.
        
        Args:
            namespace: Namespace to get deployments from. If None, uses the default namespace.
        
        Returns:
            List of deployments.
        """
        try:
            namespace = namespace or self.config.namespace
            if namespace == "all":
                deployments = self.apps_v1_api.list_deployment_for_all_namespaces()
            else:
                deployments = self.apps_v1_api.list_namespaced_deployment(namespace)
            return [self._extract_resource_info(deployment) for deployment in deployments.items]
        except ApiException as e:
            logger.error(f"Error getting deployments: {e}")
            return []

    def get_deployment(self, name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a deployment by name.
        
        Args:
            name: Name of the deployment.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            Deployment information or None if not found.
        """
        try:
            namespace = namespace or self.config.namespace
            deployment = self.apps_v1_api.read_namespaced_deployment(name, namespace)
            return self._extract_resource_info(deployment, detailed=True)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Deployment {name} not found in namespace {namespace}")
            else:
                logger.error(f"Error getting deployment {name}: {e}")
            return None

    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all services in a namespace.
        
        Args:
            namespace: Namespace to get services from. If None, uses the default namespace.
        
        Returns:
            List of services.
        """
        try:
            namespace = namespace or self.config.namespace
            if namespace == "all":
                services = self.core_v1_api.list_service_for_all_namespaces()
            else:
                services = self.core_v1_api.list_namespaced_service(namespace)
            return [self._extract_resource_info(service) for service in services.items]
        except ApiException as e:
            logger.error(f"Error getting services: {e}")
            return []

    def get_service(self, name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a service by name.
        
        Args:
            name: Name of the service.
            namespace: Namespace of the service. If None, uses the default namespace.
        
        Returns:
            Service information or None if not found.
        """
        try:
            namespace = namespace or self.config.namespace
            service = self.core_v1_api.read_namespaced_service(name, namespace)
            return self._extract_resource_info(service, detailed=True)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Service {name} not found in namespace {namespace}")
            else:
                logger.error(f"Error getting service {name}: {e}")
            return None

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes.
        
        Returns:
            List of nodes.
        """
        try:
            nodes = self.core_v1_api.list_node()
            return [self._extract_resource_info(node) for node in nodes.items]
        except ApiException as e:
            logger.error(f"Error getting nodes: {e}")
            return []

    def get_node(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a node by name.
        
        Args:
            name: Name of the node.
        
        Returns:
            Node information or None if not found.
        """
        try:
            node = self.core_v1_api.read_node(name)
            return self._extract_resource_info(node, detailed=True)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Node {name} not found")
            else:
                logger.error(f"Error getting node {name}: {e}")
            return None

    def get_persistent_volumes(self) -> List[Dict[str, Any]]:
        """Get all persistent volumes.
        
        Returns:
            List of persistent volumes.
        """
        try:
            pvs = self.core_v1_api.list_persistent_volume()
            return [self._extract_resource_info(pv) for pv in pvs.items]
        except ApiException as e:
            logger.error(f"Error getting persistent volumes: {e}")
            return []

    def get_persistent_volume(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a persistent volume by name.
        
        Args:
            name: Name of the persistent volume.
        
        Returns:
            Persistent volume information or None if not found.
        """
        try:
            pv = self.core_v1_api.read_persistent_volume(name)
            return self._extract_resource_info(pv, detailed=True)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Persistent volume {name} not found")
            else:
                logger.error(f"Error getting persistent volume {name}: {e}")
            return None

    def get_persistent_volume_claims(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all persistent volume claims in a namespace.
        
        Args:
            namespace: Namespace to get persistent volume claims from. If None, uses the default namespace.
        
        Returns:
            List of persistent volume claims.
        """
        try:
            namespace = namespace or self.config.namespace
            if namespace == "all":
                pvcs = self.core_v1_api.list_persistent_volume_claim_for_all_namespaces()
            else:
                pvcs = self.core_v1_api.list_namespaced_persistent_volume_claim(namespace)
            return [self._extract_resource_info(pvc) for pvc in pvcs.items]
        except ApiException as e:
            logger.error(f"Error getting persistent volume claims: {e}")
            return []

    def get_persistent_volume_claim(self, name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a persistent volume claim by name.
        
        Args:
            name: Name of the persistent volume claim.
            namespace: Namespace of the persistent volume claim. If None, uses the default namespace.
        
        Returns:
            Persistent volume claim information or None if not found.
        """
        try:
            namespace = namespace or self.config.namespace
            pvc = self.core_v1_api.read_namespaced_persistent_volume_claim(name, namespace)
            return self._extract_resource_info(pvc, detailed=True)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Persistent volume claim {name} not found in namespace {namespace}")
            else:
                logger.error(f"Error getting persistent volume claim {name}: {e}")
            return None

    def get_events(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all events in a namespace.
        
        Args:
            namespace: Namespace to get events from. If None, uses the default namespace.
        
        Returns:
            List of events.
        """
        try:
            namespace = namespace or self.config.namespace
            if namespace == "all":
                events = self.core_v1_api.list_event_for_all_namespaces()
            else:
                events = self.core_v1_api.list_namespaced_event(namespace)
            return [self._extract_resource_info(event) for event in events.items]
        except ApiException as e:
            logger.error(f"Error getting events: {e}")
            return []

    def get_resource_events(self, kind: str, name: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events for a specific resource.
        
        Args:
            kind: Kind of the resource (e.g., "Pod", "Deployment").
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            List of events for the resource.
        """
        try:
            namespace = namespace or self.config.namespace
            field_selector = f"involvedObject.name={name},involvedObject.kind={kind}"
            if namespace != "all":
                events = self.core_v1_api.list_namespaced_event(
                    namespace, field_selector=field_selector
                )
            else:
                events = self.core_v1_api.list_event_for_all_namespaces(
                    field_selector=field_selector
                )
            return [self._extract_resource_info(event) for event in events.items]
        except ApiException as e:
            logger.error(f"Error getting events for {kind} {name}: {e}")
            return []

    def _extract_resource_info(self, resource: Any, detailed: bool = False) -> Dict[str, Any]:
        """Extract information from a Kubernetes resource.
        
        Args:
            resource: Kubernetes resource.
            detailed: Whether to include detailed information.
        
        Returns:
            Dictionary with resource information.
        """
        # Convert to dict and remove unnecessary fields
        resource_dict = resource.to_dict()
        
        # Extract basic info
        result = {
            "kind": resource.kind,
            "apiVersion": resource_dict.get("api_version"),
            "name": resource_dict.get("metadata", {}).get("name"),
            "namespace": resource_dict.get("metadata", {}).get("namespace"),
            "creationTimestamp": resource_dict.get("metadata", {}).get("creation_timestamp"),
        }
        
        # Add labels and annotations if they exist
        metadata = resource_dict.get("metadata", {})
        if labels := metadata.get("labels"):
            result["labels"] = labels
        if annotations := metadata.get("annotations"):
            result["annotations"] = annotations
        
        # Add status if it exists
        if status := resource_dict.get("status"):
            result["status"] = status
        
        # Add spec if detailed
        if detailed and (spec := resource_dict.get("spec")):
            result["spec"] = spec
        
        return result
