#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Kubernetes operations module.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import yaml
from typing import Any, Dict, List, Optional, Union

from kubernetes import client
from kubernetes.client.rest import ApiException

from mcp_k8s_server.k8s.client import K8sClient

logger = logging.getLogger(__name__)


class K8sOperations:
    """Kubernetes operations."""

    def __init__(self, k8s_client: K8sClient):
        """Initialize the Kubernetes operations.
        
        Args:
            k8s_client: Kubernetes client.
        """
        self.client = k8s_client

    def create_resource(self, resource_yaml: str) -> Dict[str, Any]:
        """Create a resource from YAML.
        
        Args:
            resource_yaml: YAML representation of the resource.
        
        Returns:
            Dictionary with the result of the operation.
        """
        try:
            # Parse the YAML
            resource = yaml.safe_load(resource_yaml)
            
            # Get the resource kind and API version
            kind = resource.get("kind")
            api_version = resource.get("apiVersion")
            
            if not kind or not api_version:
                return {
                    "success": False,
                    "message": "Invalid resource: missing kind or apiVersion",
                }
            
            # Get the resource name and namespace
            metadata = resource.get("metadata", {})
            name = metadata.get("name")
            namespace = metadata.get("namespace", self.client.config.namespace)
            
            if not name:
                return {
                    "success": False,
                    "message": "Invalid resource: missing metadata.name",
                }
            
            # Create the resource
            result = self._create_resource(resource, kind, api_version, namespace)
            
            return {
                "success": True,
                "message": f"Created {kind} {name} in namespace {namespace}",
                "resource": result,
            }
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            return {
                "success": False,
                "message": f"Error parsing YAML: {e}",
            }
        except ApiException as e:
            logger.error(f"Error creating resource: {e}")
            return {
                "success": False,
                "message": f"Error creating resource: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error creating resource: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {e}",
            }

    def update_resource(self, resource_yaml: str) -> Dict[str, Any]:
        """Update a resource from YAML.
        
        Args:
            resource_yaml: YAML representation of the resource.
        
        Returns:
            Dictionary with the result of the operation.
        """
        try:
            # Parse the YAML
            resource = yaml.safe_load(resource_yaml)
            
            # Get the resource kind and API version
            kind = resource.get("kind")
            api_version = resource.get("apiVersion")
            
            if not kind or not api_version:
                return {
                    "success": False,
                    "message": "Invalid resource: missing kind or apiVersion",
                }
            
            # Get the resource name and namespace
            metadata = resource.get("metadata", {})
            name = metadata.get("name")
            namespace = metadata.get("namespace", self.client.config.namespace)
            
            if not name:
                return {
                    "success": False,
                    "message": "Invalid resource: missing metadata.name",
                }
            
            # Update the resource
            result = self._update_resource(resource, kind, api_version, namespace)
            
            return {
                "success": True,
                "message": f"Updated {kind} {name} in namespace {namespace}",
                "resource": result,
            }
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            return {
                "success": False,
                "message": f"Error parsing YAML: {e}",
            }
        except ApiException as e:
            logger.error(f"Error updating resource: {e}")
            return {
                "success": False,
                "message": f"Error updating resource: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error updating resource: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {e}",
            }

    def delete_resource(self, kind: str, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Delete a resource.
        
        Args:
            kind: Kind of the resource.
            name: Name of the resource.
            namespace: Namespace of the resource. If None, uses the default namespace.
        
        Returns:
            Dictionary with the result of the operation.
        """
        try:
            namespace = namespace or self.client.config.namespace
            
            # Delete the resource
            self._delete_resource(kind, name, namespace)
            
            return {
                "success": True,
                "message": f"Deleted {kind} {name} in namespace {namespace}",
            }
        except ApiException as e:
            logger.error(f"Error deleting resource: {e}")
            return {
                "success": False,
                "message": f"Error deleting resource: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error deleting resource: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {e}",
            }

    def scale_deployment(self, name: str, replicas: int, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Scale a deployment.
        
        Args:
            name: Name of the deployment.
            replicas: Number of replicas.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            Dictionary with the result of the operation.
        """
        try:
            namespace = namespace or self.client.config.namespace
            
            # Scale the deployment
            self.client.apps_v1_api.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}},
            )
            
            return {
                "success": True,
                "message": f"Scaled deployment {name} to {replicas} replicas in namespace {namespace}",
            }
        except ApiException as e:
            logger.error(f"Error scaling deployment: {e}")
            return {
                "success": False,
                "message": f"Error scaling deployment: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error scaling deployment: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {e}",
            }

    def restart_deployment(self, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Restart a deployment.
        
        Args:
            name: Name of the deployment.
            namespace: Namespace of the deployment. If None, uses the default namespace.
        
        Returns:
            Dictionary with the result of the operation.
        """
        try:
            namespace = namespace or self.client.config.namespace
            
            # Restart the deployment by adding a restart annotation
            now = client.V1Time().to_dict()
            patch = {
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "kubectl.kubernetes.io/restartedAt": now
                            }
                        }
                    }
                }
            }
            
            self.client.apps_v1_api.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=patch,
            )
            
            return {
                "success": True,
                "message": f"Restarted deployment {name} in namespace {namespace}",
            }
        except ApiException as e:
            logger.error(f"Error restarting deployment: {e}")
            return {
                "success": False,
                "message": f"Error restarting deployment: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error restarting deployment: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {e}",
            }

    def execute_command(self, pod_name: str, command: List[str], namespace: Optional[str] = None, 
                        container: Optional[str] = None) -> Dict[str, Any]:
        """Execute a command in a pod.
        
        Args:
            pod_name: Name of the pod.
            command: Command to execute.
            namespace: Namespace of the pod. If None, uses the default namespace.
            container: Name of the container. If None, uses the first container.
        
        Returns:
            Dictionary with the result of the operation.
        """
        try:
            namespace = namespace or self.client.config.namespace
            
            # Execute the command
            response = client.CoreV1Api().connect_get_namespaced_pod_exec(
                name=pod_name,
                namespace=namespace,
                container=container,
                command=command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            
            return {
                "success": True,
                "message": f"Executed command in pod {pod_name} in namespace {namespace}",
                "output": response,
            }
        except ApiException as e:
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "message": f"Error executing command: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error executing command: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {e}",
            }

    def _create_resource(self, resource: Dict[str, Any], kind: str, api_version: str, 
                         namespace: str) -> Dict[str, Any]:
        """Create a resource.
        
        Args:
            resource: Resource to create.
            kind: Kind of the resource.
            api_version: API version of the resource.
            namespace: Namespace of the resource.
        
        Returns:
            Created resource.
        """
        # Handle different resource types
        if api_version == "v1" and kind == "Pod":
            return self.client.core_v1_api.create_namespaced_pod(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "Service":
            return self.client.core_v1_api.create_namespaced_service(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "ConfigMap":
            return self.client.core_v1_api.create_namespaced_config_map(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "Secret":
            return self.client.core_v1_api.create_namespaced_secret(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "PersistentVolumeClaim":
            return self.client.core_v1_api.create_namespaced_persistent_volume_claim(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "PersistentVolume":
            return self.client.core_v1_api.create_persistent_volume(
                body=resource,
            ).to_dict()
        elif api_version == "apps/v1" and kind == "Deployment":
            return self.client.apps_v1_api.create_namespaced_deployment(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "apps/v1" and kind == "StatefulSet":
            return self.client.apps_v1_api.create_namespaced_stateful_set(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "apps/v1" and kind == "DaemonSet":
            return self.client.apps_v1_api.create_namespaced_daemon_set(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "batch/v1" and kind == "Job":
            return self.client.batch_v1_api.create_namespaced_job(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "batch/v1" and kind == "CronJob":
            return self.client.batch_v1_api.create_namespaced_cron_job(
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "networking.k8s.io/v1" and kind == "Ingress":
            return self.client.networking_v1_api.create_namespaced_ingress(
                namespace=namespace,
                body=resource,
            ).to_dict()
        else:
            # Use dynamic client for other resource types
            group, version = self._parse_api_version(api_version)
            plural = self._get_plural(kind)
            
            if group:
                return self.client.custom_objects_api.create_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=plural,
                    body=resource,
                )
            else:
                raise ValueError(f"Unsupported resource type: {api_version}/{kind}")

    def _update_resource(self, resource: Dict[str, Any], kind: str, api_version: str, 
                         namespace: str) -> Dict[str, Any]:
        """Update a resource.
        
        Args:
            resource: Resource to update.
            kind: Kind of the resource.
            api_version: API version of the resource.
            namespace: Namespace of the resource.
        
        Returns:
            Updated resource.
        """
        name = resource["metadata"]["name"]
        
        # Handle different resource types
        if api_version == "v1" and kind == "Pod":
            return self.client.core_v1_api.replace_namespaced_pod(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "Service":
            return self.client.core_v1_api.replace_namespaced_service(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "ConfigMap":
            return self.client.core_v1_api.replace_namespaced_config_map(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "Secret":
            return self.client.core_v1_api.replace_namespaced_secret(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "PersistentVolumeClaim":
            return self.client.core_v1_api.replace_namespaced_persistent_volume_claim(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "v1" and kind == "PersistentVolume":
            return self.client.core_v1_api.replace_persistent_volume(
                name=name,
                body=resource,
            ).to_dict()
        elif api_version == "apps/v1" and kind == "Deployment":
            return self.client.apps_v1_api.replace_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "apps/v1" and kind == "StatefulSet":
            return self.client.apps_v1_api.replace_namespaced_stateful_set(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "apps/v1" and kind == "DaemonSet":
            return self.client.apps_v1_api.replace_namespaced_daemon_set(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "batch/v1" and kind == "Job":
            return self.client.batch_v1_api.replace_namespaced_job(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "batch/v1" and kind == "CronJob":
            return self.client.batch_v1_api.replace_namespaced_cron_job(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        elif api_version == "networking.k8s.io/v1" and kind == "Ingress":
            return self.client.networking_v1_api.replace_namespaced_ingress(
                name=name,
                namespace=namespace,
                body=resource,
            ).to_dict()
        else:
            # Use dynamic client for other resource types
            group, version = self._parse_api_version(api_version)
            plural = self._get_plural(kind)
            
            if group:
                return self.client.custom_objects_api.replace_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=plural,
                    name=name,
                    body=resource,
                )
            else:
                raise ValueError(f"Unsupported resource type: {api_version}/{kind}")

    def _delete_resource(self, kind: str, name: str, namespace: str) -> None:
        """Delete a resource.
        
        Args:
            kind: Kind of the resource.
            name: Name of the resource.
            namespace: Namespace of the resource.
        """
        # Handle different resource types
        if kind == "Pod":
            self.client.core_v1_api.delete_namespaced_pod(
                name=name,
                namespace=namespace,
            )
        elif kind == "Service":
            self.client.core_v1_api.delete_namespaced_service(
                name=name,
                namespace=namespace,
            )
        elif kind == "ConfigMap":
            self.client.core_v1_api.delete_namespaced_config_map(
                name=name,
                namespace=namespace,
            )
        elif kind == "Secret":
            self.client.core_v1_api.delete_namespaced_secret(
                name=name,
                namespace=namespace,
            )
        elif kind == "PersistentVolumeClaim":
            self.client.core_v1_api.delete_namespaced_persistent_volume_claim(
                name=name,
                namespace=namespace,
            )
        elif kind == "PersistentVolume":
            self.client.core_v1_api.delete_persistent_volume(
                name=name,
            )
        elif kind == "Deployment":
            self.client.apps_v1_api.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
            )
        elif kind == "StatefulSet":
            self.client.apps_v1_api.delete_namespaced_stateful_set(
                name=name,
                namespace=namespace,
            )
        elif kind == "DaemonSet":
            self.client.apps_v1_api.delete_namespaced_daemon_set(
                name=name,
                namespace=namespace,
            )
        elif kind == "Job":
            self.client.batch_v1_api.delete_namespaced_job(
                name=name,
                namespace=namespace,
            )
        elif kind == "CronJob":
            self.client.batch_v1_api.delete_namespaced_cron_job(
                name=name,
                namespace=namespace,
            )
        elif kind == "Ingress":
            self.client.networking_v1_api.delete_namespaced_ingress(
                name=name,
                namespace=namespace,
            )
        else:
            # Try to guess the API version and group
            if kind in ["Deployment", "StatefulSet", "DaemonSet", "ReplicaSet"]:
                group = "apps"
                version = "v1"
            elif kind in ["Job", "CronJob"]:
                group = "batch"
                version = "v1"
            elif kind in ["Ingress"]:
                group = "networking.k8s.io"
                version = "v1"
            else:
                raise ValueError(f"Unsupported resource type: {kind}")
            
            plural = self._get_plural(kind)
            
            self.client.custom_objects_api.delete_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
            )

    def _parse_api_version(self, api_version: str) -> tuple[str, str]:
        """Parse API version into group and version.
        
        Args:
            api_version: API version string (e.g., "apps/v1").
        
        Returns:
            Tuple of (group, version).
        """
        if "/" in api_version:
            return api_version.split("/", 1)
        return "", api_version

    def _get_plural(self, kind: str) -> str:
        """Get the plural form of a resource kind.
        
        Args:
            kind: Resource kind (e.g., "Pod").
        
        Returns:
            Plural form of the resource kind.
        """
        # Common pluralization rules for Kubernetes resources
        if kind.endswith("s"):
            return kind.lower() + "es"
        elif kind.endswith("y"):
            return kind[:-1].lower() + "ies"
        else:
            return kind.lower() + "s"
