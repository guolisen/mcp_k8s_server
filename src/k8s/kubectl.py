"""
Kubectl command wrapper for executing kubectl commands directly.
"""

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class KubectlWrapper:
    """Class for interacting with Kubernetes via kubectl commands."""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize the kubectl wrapper.
        
        Args:
            kubeconfig_path: Path to kubeconfig file. If None, uses the default.
        """
        self.kubeconfig_path = kubeconfig_path
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test connection to the Kubernetes cluster."""
        try:
            self.execute_command(["version", "--client"])
            logger.info("Successfully connected to kubectl client")
            
            # Test server connection
            server_version = self.execute_command(["version", "-o", "json"])
            if "serverVersion" in server_version:
                logger.info(f"Successfully connected to Kubernetes server version {server_version.get('serverVersion', {}).get('gitVersion', 'unknown')}")
            else:
                logger.warning("Connected to kubectl client but couldn't connect to server")
        except Exception as e:
            logger.error(f"Failed to initialize kubectl wrapper: {e}")
            raise
    
    def execute_command(self, args: List[str], namespace: Optional[str] = None, capture_output: bool = True) -> Any:
        """
        Execute a kubectl command.
        
        Args:
            args: List of command arguments to pass to kubectl.
            namespace: Namespace to execute the command in.
            capture_output: Whether to capture and return the command output.
                           If False, output goes to stdout/stderr.
        
        Returns:
            Command output as parsed JSON if the output is JSON,
            or as a string if not JSON or if parsing fails.
        """
        cmd = ["kubectl"]
        
        # Add kubeconfig if specified
        if self.kubeconfig_path:
            cmd.extend(["--kubeconfig", self.kubeconfig_path])
        
        # Add namespace if specified
        if namespace:
            cmd.extend(["-n", namespace])
        
        # Add command arguments
        cmd.extend(args)
        
        logger.debug(f"Executing kubectl command: {' '.join(cmd)}")
        
        if capture_output:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                output = result.stdout.strip()
                
                # Try to parse as JSON
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return output
            except subprocess.CalledProcessError as e:
                logger.error(f"kubectl command failed: {e.stderr}")
                raise RuntimeError(f"kubectl command failed: {e.stderr}")
        else:
            # Just execute the command without capturing output
            try:
                subprocess.run(cmd, check=True)
                return None
            except subprocess.CalledProcessError as e:
                logger.error(f"kubectl command failed with exit code {e.returncode}")
                raise RuntimeError(f"kubectl command failed with exit code {e.returncode}")
    
    # Resource retrieval methods
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes in the cluster."""
        return self.execute_command(["get", "nodes", "-o", "json"])["items"]
    
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces in the cluster."""
        return self.execute_command(["get", "namespaces", "-o", "json"])["items"]
    
    def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pods, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get pods in this namespace.
                      If None, get pods in all namespaces.
        """
        if namespace:
            return self.execute_command(["get", "pods", "-o", "json"], namespace=namespace)["items"]
        else:
            return self.execute_command(["get", "pods", "-A", "-o", "json"])["items"]
    
    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get deployments, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get deployments in this namespace.
                      If None, get deployments in all namespaces.
        """
        if namespace:
            return self.execute_command(["get", "deployments", "-o", "json"], namespace=namespace)["items"]
        else:
            return self.execute_command(["get", "deployments", "-A", "-o", "json"])["items"]
    
    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get services, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get services in this namespace.
                      If None, get services in all namespaces.
        """
        if namespace:
            return self.execute_command(["get", "services", "-o", "json"], namespace=namespace)["items"]
        else:
            return self.execute_command(["get", "services", "-A", "-o", "json"])["items"]
    
    def get_events(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get events, optionally filtered by namespace.
        
        Args:
            namespace: If provided, only get events in this namespace.
                      If None, get events in all namespaces.
        """
        if namespace:
            return self.execute_command(["get", "events", "-o", "json"], namespace=namespace)["items"]
        else:
            return self.execute_command(["get", "events", "-A", "-o", "json"])["items"]
    
    # Cluster operations
    
    def create_resource(self, yaml_file: str) -> str:
        """
        Create a resource from a YAML file.
        
        Args:
            yaml_file: Path to the YAML file defining the resource.
        
        Returns:
            Command output.
        """
        return self.execute_command(["apply", "-f", yaml_file])
    
    def delete_resource(self, resource_type: str, resource_name: str, namespace: Optional[str] = None) -> str:
        """
        Delete a resource.
        
        Args:
            resource_type: Type of resource (e.g., "pod", "deployment").
            resource_name: Name of the resource.
            namespace: Namespace the resource is in.
        
        Returns:
            Command output.
        """
        return self.execute_command(["delete", resource_type, resource_name], namespace=namespace)
    
    def scale_deployment(self, deployment_name: str, replicas: int, namespace: Optional[str] = None) -> str:
        """
        Scale a deployment to a specified number of replicas.
        
        Args:
            deployment_name: Name of the deployment.
            replicas: Number of replicas to scale to.
            namespace: Namespace the deployment is in.
        
        Returns:
            Command output.
        """
        return self.execute_command(["scale", "deployment", deployment_name, f"--replicas={replicas}"], namespace=namespace)
    
    def exec_command_in_pod(
        self, pod_name: str, container_name: Optional[str], command: List[str], namespace: Optional[str] = None
    ) -> str:
        """
        Execute a command in a pod container.
        
        Args:
            pod_name: Name of the pod.
            container_name: Name of the container in the pod.
            command: Command to execute.
            namespace: Namespace the pod is in.
        
        Returns:
            Command output.
        """
        exec_cmd = ["exec", pod_name]
        if container_name:
            exec_cmd.extend(["-c", container_name])
        exec_cmd.extend(["--", *command])
        
        return self.execute_command(exec_cmd, namespace=namespace)
    
    def get_logs(
        self, pod_name: str, container_name: Optional[str] = None, 
        tail: Optional[int] = None, namespace: Optional[str] = None
    ) -> str:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod.
            container_name: Name of the container in the pod.
            tail: If specified, return this many lines from the end.
            namespace: Namespace the pod is in.
        
        Returns:
            Log output.
        """
        logs_cmd = ["logs", pod_name]
        if container_name:
            logs_cmd.extend(["-c", container_name])
        if tail:
            logs_cmd.extend(["--tail", str(tail)])
        
        return self.execute_command(logs_cmd, namespace=namespace)
    
    def describe_resource(self, resource_type: str, resource_name: str, namespace: Optional[str] = None) -> str:
        """
        Describe a resource.
        
        Args:
            resource_type: Type of resource (e.g., "pod", "deployment").
            resource_name: Name of the resource.
            namespace: Namespace the resource is in.
        
        Returns:
            Description of the resource.
        """
        return self.execute_command(["describe", resource_type, resource_name], namespace=namespace)
    
    def get_resource_usage(self) -> str:
        """
        Get resource usage across the cluster.
        
        Returns:
            Resource usage information.
        """
        return self.execute_command(["top", "nodes"])
    
    def get_pod_resource_usage(self, namespace: Optional[str] = None) -> str:
        """
        Get resource usage for pods.
        
        Args:
            namespace: If provided, only get pod resource usage in this namespace.
        
        Returns:
            Pod resource usage information.
        """
        if namespace:
            return self.execute_command(["top", "pods"], namespace=namespace)
        else:
            return self.execute_command(["top", "pods", "-A"])
    
    def restart_deployment(self, deployment_name: str, namespace: Optional[str] = None) -> str:
        """
        Restart a deployment.
        
        Args:
            deployment_name: Name of the deployment.
            namespace: Namespace the deployment is in.
        
        Returns:
            Command output.
        """
        # There's no direct kubectl command to restart a deployment
        # A common practice is to use a null patch
        return self.execute_command([
            "rollout", "restart", "deployment", deployment_name
        ], namespace=namespace)
    
    def get_rollout_status(self, resource_type: str, resource_name: str, namespace: Optional[str] = None) -> str:
        """
        Get rollout status of a resource.
        
        Args:
            resource_type: Type of resource (e.g., "deployment", "statefulset").
            resource_name: Name of the resource.
            namespace: Namespace the resource is in.
        
        Returns:
            Rollout status.
        """
        return self.execute_command(["rollout", "status", resource_type, resource_name], namespace=namespace)
    
    def create_namespace(self, namespace: str) -> str:
        """
        Create a new namespace.
        
        Args:
            namespace: Name of the namespace to create.
        
        Returns:
            Command output.
        """
        return self.execute_command(["create", "namespace", namespace])
    
    def get_cluster_info(self) -> str:
        """
        Get information about the cluster.
        
        Returns:
            Cluster information.
        """
        return self.execute_command(["cluster-info"])
    
    def get_component_statuses(self) -> List[Dict[str, Any]]:
        """
        Get component statuses.
        
        Returns:
            Component status information.
        """
        try:
            # This may not be available in newer Kubernetes versions
            return self.execute_command(["get", "componentstatuses", "-o", "json"])["items"]
        except Exception as e:
            logger.warning(f"Failed to get component statuses: {e}")
            return []
    
    def get_all_resources(self, namespace: Optional[str] = None) -> str:
        """
        Get all resources of all types.
        
        Args:
            namespace: If provided, only get resources in this namespace.
        
        Returns:
            Information about all resources.
        """
        return self.execute_command(["get", "all"], namespace=namespace)
    
    def get_api_resources(self) -> List[Dict[str, Any]]:
        """
        Get all API resources supported by the server.
        
        Returns:
            List of API resources.
        """
        result = self.execute_command(["api-resources", "-o", "wide", "--verbs=list", "-o", "json"])
        if isinstance(result, str):
            # If the output is not JSON, parse the table output
            resources = []
            lines = result.strip().split('\n')
            if len(lines) > 1:  # Skip if just the header
                header = lines[0]
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        resources.append({
                            "name": parts[0],
                            "shortNames": parts[1].split(",") if parts[1] != "<none>" else [],
                            "apiGroup": parts[2] if parts[2] != "<none>" else "",
                            "namespaced": parts[3] == "true",
                            "kind": parts[4] if len(parts) > 4 else "",
                            "verbs": parts[5].split(",") if len(parts) > 5 else []
                        })
            return resources
        return result["resources"] if "resources" in result else []
