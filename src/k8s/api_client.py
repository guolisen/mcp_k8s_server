"""
Direct Kubernetes API client using the official Kubernetes Python client.
"""

import os
import yaml
import logging
from typing import Any, Dict, List, Optional, Union

from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesApiClient:
    """Class for interacting with the Kubernetes API directly."""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize the Kubernetes API client.
        
        Args:
            kubeconfig_path: Path to kubeconfig file. If None, tries to load from default locations.
        """
        self.api_client = None
        self.core_v1_api = None
        self.apps_v1_api = None
        self.batch_v1_api = None
        self.networking_v1_api = None
        self.storage_v1_api = None
        self.rbac_v1_api = None
        self.custom_objects_api = None
        
        try:
            if kubeconfig_path and os.path.exists(kubeconfig_path):
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                try:
                    # Try loading from within cluster first (if running in a pod)
                    config.load_incluster_config()
                except config.ConfigException:
                    # Fall back to default kubeconfig
                    config.load_kube_config()
            
            self.api_client = client.ApiClient()
            self.core_v1_api = client.CoreV1Api(self.api_client)
            self.apps_v1_api = client.AppsV1Api(self.api_client)
            self.batch_v1_api = client.BatchV1Api(self.api_client)
            self.networking_v1_api = client.NetworkingV1Api(self.api_client)
            self.storage_v1_api = client.StorageV1Api(self.api_client)
            self.rbac_v1_api = client.RbacAuthorizationV1Api(self.api_client)
            self.custom_objects_api = client.CustomObjectsApi(self.api_client)
            
            logger.info("Successfully initialized Kubernetes API client")
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes API client: {e}")
            raise

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes in the cluster."""
        try:
            nodes = self.core_v1_api.list_node()
            return [self._extract_node_info(node) for node in nodes.items]
        except ApiException as e:
            logger.error(f"Error getting nodes: {e}")
            raise

    def _extract_node_info(self, node) -> Dict[str, Any]:
        """Extract relevant information from a node object."""
        conditions = {cond.type: cond.status for cond in node.status.conditions}
        return {
            "name": node.metadata.name,
            "status": "Ready" if conditions.get("Ready") == "True" else "NotReady",
            "roles": self._get_node_roles(node.metadata.labels),
            "kubelet_version": node.status.node_info.kubelet_version,
            "os_image": node.status.node_info.os_image,
            "cpu_capacity": node.status.capacity.get("cpu"),
            "memory_capacity": node.status.capacity.get("memory"),
            "pods_capacity": node.status.capacity.get("pods"),
            "cpu_allocatable": node.status.allocatable.get("cpu"),
            "memory_allocatable": node.status.allocatable.get("memory"),
            "pods_allocatable": node.status.allocatable.get("pods"),
            "internal_ip": self._get_node_internal_ip(node.status.addresses),
            "external_ip": self._get_node_external_ip(node.status.addresses),
            "conditions": conditions,
            "taints": [{"key": t.key, "value": t.value, "effect": t.effect} 
                       for t in (node.spec.taints or [])]
        }

    def _get_node_roles(self, labels: Dict[str, str]) -> List[str]:
        """Extract node roles from labels."""
        roles = []
        for label in labels:
            if label.startswith("node-role.kubernetes.io/"):
                role = label.split("/")[1]
                roles.append(role)
        return roles or ["worker"]  # Default to worker if no roles found

    def _get_node_internal_ip(self, addresses) -> Optional[str]:
        """Get the internal IP of a node."""
        for address in addresses:
            if address.type == "InternalIP":
                return address.address
        return None

    def _get_node_external_ip(self, addresses) -> Optional[str]:
        """Get the external IP of a node."""
        for address in addresses:
            if address.type == "ExternalIP":
                return address.address
        return None

    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces in the cluster."""
        try:
            namespaces = self.core_v1_api.list_namespace()
            return [
                {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "creation_timestamp": ns.metadata.creation_timestamp.isoformat() 
                        if ns.metadata.creation_timestamp else None,
                    "labels": ns.metadata.labels or {}
                }
                for ns in namespaces.items
            ]
        except ApiException as e:
            logger.error(f"Error getting namespaces: {e}")
            raise

    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get deployments, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get deployments in this namespace.
                       If None, get deployments in all namespaces.
        """
        try:
            if namespace:
                deployments = self.apps_v1_api.list_namespaced_deployment(namespace)
            else:
                deployments = self.apps_v1_api.list_deployment_for_all_namespaces()
            
            return [
                {
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "available_replicas": dep.status.available_replicas,
                    "ready_replicas": dep.status.ready_replicas,
                    "updated_replicas": dep.status.updated_replicas,
                    "strategy": dep.spec.strategy.type,
                    "selector": dep.spec.selector.match_labels if dep.spec.selector else {},
                    "creation_timestamp": dep.metadata.creation_timestamp.isoformat() 
                        if dep.metadata.creation_timestamp else None,
                }
                for dep in deployments.items
            ]
        except ApiException as e:
            logger.error(f"Error getting deployments: {e}")
            raise

    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get services, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get services in this namespace.
                      If None, get services in all namespaces.
        """
        try:
            if namespace:
                services = self.core_v1_api.list_namespaced_service(namespace)
            else:
                services = self.core_v1_api.list_service_for_all_namespaces()
            
            return [
                {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "external_ips": svc.spec.external_i_ps if hasattr(svc.spec, "external_i_ps") else [],
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": port.target_port,
                            "protocol": port.protocol
                        }
                        for port in svc.spec.ports
                    ] if svc.spec.ports else [],
                    "selector": svc.spec.selector or {},
                    "creation_timestamp": svc.metadata.creation_timestamp.isoformat() 
                        if svc.metadata.creation_timestamp else None,
                }
                for svc in services.items
            ]
        except ApiException as e:
            logger.error(f"Error getting services: {e}")
            raise

    def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pods, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get pods in this namespace.
                      If None, get pods in all namespaces.
        """
        try:
            if namespace:
                pods = self.core_v1_api.list_namespaced_pod(namespace)
            else:
                pods = self.core_v1_api.list_pod_for_all_namespaces()
            
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ip": pod.status.pod_ip,
                    "node": pod.spec.node_name,
                    "restart_policy": pod.spec.restart_policy,
                    "containers": [
                        {
                            "name": container.name,
                            "image": container.image,
                            "ready": next(
                                (status.ready for status in pod.status.container_statuses 
                                 if status.name == container.name), 
                                False
                            ),
                            "restart_count": next(
                                (status.restart_count for status in pod.status.container_statuses 
                                 if status.name == container.name), 
                                0
                            ),
                        }
                        for container in pod.spec.containers
                    ] if pod.spec.containers else [],
                    "creation_timestamp": pod.metadata.creation_timestamp.isoformat() 
                        if pod.metadata.creation_timestamp else None,
                }
                for pod in pods.items
            ]
        except ApiException as e:
            logger.error(f"Error getting pods: {e}")
            raise

    def get_config_maps(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ConfigMaps, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get ConfigMaps in this namespace.
                      If None, get ConfigMaps in all namespaces.
        """
        try:
            if namespace:
                config_maps = self.core_v1_api.list_namespaced_config_map(namespace)
            else:
                config_maps = self.core_v1_api.list_config_map_for_all_namespaces()
            
            return [
                {
                    "name": cm.metadata.name,
                    "namespace": cm.metadata.namespace,
                    "data_count": len(cm.data) if cm.data else 0,
                    "creation_timestamp": cm.metadata.creation_timestamp.isoformat() 
                        if cm.metadata.creation_timestamp else None,
                }
                for cm in config_maps.items
            ]
        except ApiException as e:
            logger.error(f"Error getting ConfigMaps: {e}")
            raise

    def get_secrets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Secrets, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get Secrets in this namespace.
                      If None, get Secrets in all namespaces.
        """
        try:
            if namespace:
                secrets = self.core_v1_api.list_namespaced_secret(namespace)
            else:
                secrets = self.core_v1_api.list_secret_for_all_namespaces()
            
            return [
                {
                    "name": secret.metadata.name,
                    "namespace": secret.metadata.namespace,
                    "type": secret.type,
                    "data_count": len(secret.data) if secret.data else 0,
                    "creation_timestamp": secret.metadata.creation_timestamp.isoformat() 
                        if secret.metadata.creation_timestamp else None,
                }
                for secret in secrets.items
            ]
        except ApiException as e:
            logger.error(f"Error getting Secrets: {e}")
            raise

    def get_stateful_sets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get StatefulSets, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get StatefulSets in this namespace.
                      If None, get StatefulSets in all namespaces.
        """
        try:
            if namespace:
                stateful_sets = self.apps_v1_api.list_namespaced_stateful_set(namespace)
            else:
                stateful_sets = self.apps_v1_api.list_stateful_set_for_all_namespaces()
            
            return [
                {
                    "name": sts.metadata.name,
                    "namespace": sts.metadata.namespace,
                    "replicas": sts.spec.replicas,
                    "ready_replicas": sts.status.ready_replicas,
                    "service_name": sts.spec.service_name,
                    "selector": sts.spec.selector.match_labels if sts.spec.selector else {},
                    "creation_timestamp": sts.metadata.creation_timestamp.isoformat() 
                        if sts.metadata.creation_timestamp else None,
                }
                for sts in stateful_sets.items
            ]
        except ApiException as e:
            logger.error(f"Error getting StatefulSets: {e}")
            raise

    def get_daemon_sets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get DaemonSets, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get DaemonSets in this namespace.
                      If None, get DaemonSets in all namespaces.
        """
        try:
            if namespace:
                daemon_sets = self.apps_v1_api.list_namespaced_daemon_set(namespace)
            else:
                daemon_sets = self.apps_v1_api.list_daemon_set_for_all_namespaces()
            
            return [
                {
                    "name": ds.metadata.name,
                    "namespace": ds.metadata.namespace,
                    "desired_number_scheduled": ds.status.desired_number_scheduled,
                    "current_number_scheduled": ds.status.current_number_scheduled,
                    "number_ready": ds.status.number_ready,
                    "selector": ds.spec.selector.match_labels if ds.spec.selector else {},
                    "creation_timestamp": ds.metadata.creation_timestamp.isoformat() 
                        if ds.metadata.creation_timestamp else None,
                }
                for ds in daemon_sets.items
            ]
        except ApiException as e:
            logger.error(f"Error getting DaemonSets: {e}")
            raise

    def get_jobs(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Jobs, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get Jobs in this namespace.
                      If None, get Jobs in all namespaces.
        """
        try:
            if namespace:
                jobs = self.batch_v1_api.list_namespaced_job(namespace)
            else:
                jobs = self.batch_v1_api.list_job_for_all_namespaces()
            
            return [
                {
                    "name": job.metadata.name,
                    "namespace": job.metadata.namespace,
                    "completions": job.spec.completions,
                    "parallelism": job.spec.parallelism,
                    "succeeded": job.status.succeeded if job.status.succeeded else 0,
                    "active": job.status.active if job.status.active else 0,
                    "failed": job.status.failed if job.status.failed else 0,
                    "selector": job.spec.selector.match_labels if job.spec.selector else {},
                    "creation_timestamp": job.metadata.creation_timestamp.isoformat() 
                        if job.metadata.creation_timestamp else None,
                }
                for job in jobs.items
            ]
        except ApiException as e:
            logger.error(f"Error getting Jobs: {e}")
            raise

    def get_cron_jobs(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get CronJobs, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get CronJobs in this namespace.
                      If None, get CronJobs in all namespaces.
        """
        try:
            if namespace:
                cron_jobs = self.batch_v1_api.list_namespaced_cron_job(namespace)
            else:
                cron_jobs = self.batch_v1_api.list_cron_job_for_all_namespaces()
            
            return [
                {
                    "name": cj.metadata.name,
                    "namespace": cj.metadata.namespace,
                    "schedule": cj.spec.schedule,
                    "suspend": cj.spec.suspend if cj.spec.suspend else False,
                    "active_jobs": len(cj.status.active) if cj.status.active else 0,
                    "last_schedule_time": cj.status.last_schedule_time.isoformat() 
                        if cj.status.last_schedule_time else None,
                    "creation_timestamp": cj.metadata.creation_timestamp.isoformat() 
                        if cj.metadata.creation_timestamp else None,
                }
                for cj in cron_jobs.items
            ]
        except ApiException as e:
            logger.error(f"Error getting CronJobs: {e}")
            raise

    def get_ingresses(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Ingresses, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get Ingresses in this namespace.
                      If None, get Ingresses in all namespaces.
        """
        try:
            if namespace:
                ingresses = self.networking_v1_api.list_namespaced_ingress(namespace)
            else:
                ingresses = self.networking_v1_api.list_ingress_for_all_namespaces()
            
            return [
                {
                    "name": ing.metadata.name,
                    "namespace": ing.metadata.namespace,
                    "rules": [
                        {
                            "host": rule.host,
                            "paths": [
                                {
                                    "path": path.path,
                                    "path_type": path.path_type,
                                    "service_name": path.backend.service.name if path.backend.service else None,
                                    "service_port": path.backend.service.port.number if path.backend.service and path.backend.service.port else None,
                                }
                                for path in rule.http.paths
                            ] if rule.http and rule.http.paths else []
                        }
                        for rule in ing.spec.rules
                    ] if ing.spec.rules else [],
                    "tls": [
                        {
                            "hosts": tls.hosts,
                            "secret_name": tls.secret_name,
                        }
                        for tls in ing.spec.tls
                    ] if ing.spec.tls else [],
                    "creation_timestamp": ing.metadata.creation_timestamp.isoformat() 
                        if ing.metadata.creation_timestamp else None,
                }
                for ing in ingresses.items
            ]
        except ApiException as e:
            logger.error(f"Error getting Ingresses: {e}")
            raise

    def get_storage_classes(self) -> List[Dict[str, Any]]:
        """Get all StorageClasses in the cluster."""
        try:
            storage_classes = self.storage_v1_api.list_storage_class()
            return [
                {
                    "name": sc.metadata.name,
                    "provisioner": sc.provisioner,
                    "reclaim_policy": sc.reclaim_policy,
                    "volume_binding_mode": sc.volume_binding_mode,
                    "allow_volume_expansion": sc.allow_volume_expansion,
                    "is_default": sc.metadata.annotations.get("storageclass.kubernetes.io/is-default-class") == "true" 
                        if sc.metadata.annotations else False,
                    "creation_timestamp": sc.metadata.creation_timestamp.isoformat() 
                        if sc.metadata.creation_timestamp else None,
                }
                for sc in storage_classes.items
            ]
        except ApiException as e:
            logger.error(f"Error getting StorageClasses: {e}")
            raise

    def get_persistent_volumes(self) -> List[Dict[str, Any]]:
        """Get all PersistentVolumes in the cluster."""
        try:
            persistent_volumes = self.core_v1_api.list_persistent_volume()
            return [
                {
                    "name": pv.metadata.name,
                    "capacity": pv.spec.capacity.get("storage"),
                    "access_modes": pv.spec.access_modes,
                    "reclaim_policy": pv.spec.persistent_volume_reclaim_policy,
                    "status": pv.status.phase,
                    "claim_ref": f"{pv.spec.claim_ref.namespace}/{pv.spec.claim_ref.name}" 
                        if pv.spec.claim_ref else None,
                    "storage_class": pv.spec.storage_class_name,
                    "creation_timestamp": pv.metadata.creation_timestamp.isoformat() 
                        if pv.metadata.creation_timestamp else None,
                }
                for pv in persistent_volumes.items
            ]
        except ApiException as e:
            logger.error(f"Error getting PersistentVolumes: {e}")
            raise

    def get_persistent_volume_claims(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get PersistentVolumeClaims, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get PVCs in this namespace.
                      If None, get PVCs in all namespaces.
        """
        try:
            if namespace:
                pvcs = self.core_v1_api.list_namespaced_persistent_volume_claim(namespace)
            else:
                pvcs = self.core_v1_api.list_persistent_volume_claim_for_all_namespaces()
            
            return [
                {
                    "name": pvc.metadata.name,
                    "namespace": pvc.metadata.namespace,
                    "status": pvc.status.phase,
                    "volume_name": pvc.spec.volume_name,
                    "storage_class": pvc.spec.storage_class_name,
                    "access_modes": pvc.spec.access_modes,
                    "capacity": pvc.status.capacity.get("storage") if pvc.status.capacity else None,
                    "creation_timestamp": pvc.metadata.creation_timestamp.isoformat() 
                        if pvc.metadata.creation_timestamp else None,
                }
                for pvc in pvcs.items
            ]
        except ApiException as e:
            logger.error(f"Error getting PersistentVolumeClaims: {e}")
            raise

    def get_events(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Events, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get Events in this namespace.
                      If None, get Events in all namespaces.
        """
        try:
            if namespace:
                events = self.core_v1_api.list_namespaced_event(namespace)
            else:
                events = self.core_v1_api.list_event_for_all_namespaces()
            
            return [
                {
                    "name": event.metadata.name,
                    "namespace": event.metadata.namespace,
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "count": event.count,
                    "involved_object": {
                        "kind": event.involved_object.kind,
                        "namespace": event.involved_object.namespace,
                        "name": event.involved_object.name,
                    },
                    "first_timestamp": event.first_timestamp.isoformat() if event.first_timestamp else None,
                    "last_timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None,
                    "creation_timestamp": event.metadata.creation_timestamp.isoformat() 
                        if event.metadata.creation_timestamp else None,
                }
                for event in events.items
            ]
        except ApiException as e:
            logger.error(f"Error getting Events: {e}")
            raise

    def get_resource_quotas(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ResourceQuotas, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get ResourceQuotas in this namespace.
                      If None, get ResourceQuotas in all namespaces.
        """
        try:
            if namespace:
                resource_quotas = self.core_v1_api.list_namespaced_resource_quota(namespace)
            else:
                resource_quotas = self.core_v1_api.list_resource_quota_for_all_namespaces()
            
            return [
                {
                    "name": rq.metadata.name,
                    "namespace": rq.metadata.namespace,
                    "hard": rq.spec.hard,
                    "used": rq.status.used if rq.status.used else {},
                    "creation_timestamp": rq.metadata.creation_timestamp.isoformat() 
                        if rq.metadata.creation_timestamp else None,
                }
                for rq in resource_quotas.items
            ]
        except ApiException as e:
            logger.error(f"Error getting ResourceQuotas: {e}")
            raise

    def get_cluster_role_bindings(self) -> List[Dict[str, Any]]:
        """Get all ClusterRoleBindings in the cluster."""
        try:
            crbs = self.rbac_v1_api.list_cluster_role_binding()
            return [
                {
                    "name": crb.metadata.name,
                    "role_ref": {
                        "kind": crb.role_ref.kind,
                        "name": crb.role_ref.name,
                    },
                    "subjects": [
                        {
                            "kind": subject.kind,
                            "name": subject.name,
                            "namespace": subject.namespace if hasattr(subject, "namespace") else None,
                        }
                        for subject in crb.subjects
                    ] if crb.subjects else [],
                    "creation_timestamp": crb.metadata.creation_timestamp.isoformat() 
                        if crb.metadata.creation_timestamp else None,
                }
                for crb in crbs.items
            ]
        except ApiException as e:
            logger.error(f"Error getting ClusterRoleBindings: {e}")
            raise

    def get_cluster_health(self) -> Dict[str, Any]:
        """Get overall cluster health status."""
        health = {
            "status": "Healthy",
            "components": {},
            "nodes": {},
            "issues": [],
        }
        
        # Check component status
        try:
            # In newer K8s versions, we need to check individual components
            # First check API server
            api_server_health = True
            try:
                # This will throw if API server is not reachable
                self.api_client.call_api('/healthz', 'GET', auth_settings=['BearerToken'])
            except Exception as e:
                api_server_health = False
                health["issues"].append(f"API server health check failed: {str(e)}")
            
            health["components"]["apiServer"] = "Healthy" if api_server_health else "Unhealthy"
            
            # Check nodes
            nodes = self.get_nodes()
            not_ready_nodes = []
            
            for node in nodes:
                if node["status"] != "Ready":
                    not_ready_nodes.append(node["name"])
                    health["nodes"][node["name"]] = "NotReady"
                else:
                    health["nodes"][node["name"]] = "Ready"
            
            if not_ready_nodes:
                health["status"] = "Degraded"
                health["issues"].append(f"Nodes not ready: {', '.join(not_ready_nodes)}")
            
            # Check for pods in non-running state that should be running
            problem_pods = []
            pods = self.get_pods()
            for pod in pods:
                # Skip completed jobs and other pods that are expected to stop
                if pod["status"] not in ["Running", "Succeeded", "Completed"]:
                    problem_pods.append(f"{pod['namespace']}/{pod['name']}")
            
            if problem_pods:
                health["status"] = "Degraded"
                health["issues"].append(f"Problematic pods: {', '.join(problem_pods[:5])}" + 
                                        (f" and {len(problem_pods) - 5} more" if len(problem_pods) > 5 else ""))
            
            return health
            
        except Exception as e:
            health["status"] = "Unknown"
            health["issues"].append(f"Error checking cluster health: {str(e)}")
            return health
