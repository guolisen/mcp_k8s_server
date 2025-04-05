#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Tests for the cluster resources module.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from unittest.mock import MagicMock, patch

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource

from mcp_k8s_server.k8s.client import K8sClient
from mcp_k8s_server.resources.cluster_resources import register_cluster_resources


class TestClusterResources(unittest.TestCase):
    """Test cases for cluster resources."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = MagicMock(spec=FastMCP)
        self.k8s_client = MagicMock(spec=K8sClient)
        
        # Mock the register methods
        self.list_resources_func = None
        self.read_resource_func = None
        
        def mock_register_list_resources_handler(func):
            self.list_resources_func = func
        
        def mock_register_read_resource_handler(func):
            self.read_resource_func = func
        
        # Apply the mocks
        self.mcp.register_list_resources_handler = mock_register_list_resources_handler
        self.mcp.register_read_resource_handler = mock_register_read_resource_handler
        
        # Register the resources
        register_cluster_resources(self.mcp, self.k8s_client)

    def test_list_resources_registration(self):
        """Test that list_resources is registered with the MCP server."""
        self.assertIsNotNone(self.list_resources_func, "list_resources function was not registered")

    def test_read_resource_registration(self):
        """Test that read_resource is registered with the MCP server."""
        self.assertIsNotNone(self.read_resource_func, "read_resource function was not registered")

    def test_list_resources(self):
        """Test listing resources."""
        # Mock the K8sClient methods
        self.k8s_client.get_namespaces.return_value = [{"name": "default"}, {"name": "kube-system"}]
        self.k8s_client.get_nodes.return_value = [{"name": "node1"}, {"name": "node2"}]
        self.k8s_client.get_persistent_volumes.return_value = [{"name": "pv1"}, {"name": "pv2"}]
        self.k8s_client.get_pods.return_value = [{"name": "pod1"}, {"name": "pod2"}]
        self.k8s_client.get_deployments.return_value = [{"name": "deploy1"}, {"name": "deploy2"}]
        self.k8s_client.get_services.return_value = [{"name": "svc1"}, {"name": "svc2"}]
        self.k8s_client.get_persistent_volume_claims.return_value = [{"name": "pvc1"}, {"name": "pvc2"}]
        
        # Call the function
        resources = self.list_resources_func()
        
        # Verify the results
        self.assertIsInstance(resources, list)
        self.assertGreater(len(resources), 0)
        
        # Check that all resources are of the correct type
        for resource in resources:
            self.assertIsInstance(resource, Resource)
            self.assertTrue(str(resource.uri).startswith("k8s://"))
            self.assertIsNotNone(resource.name)
            self.assertIsNotNone(resource.description)
            self.assertEqual(resource.mimeType, "application/json")
        
        # Verify that the expected resources are included
        resource_uris = [str(r.uri) for r in resources]
        
        # Check namespaces
        self.assertIn("k8s://namespaces/default", resource_uris)
        self.assertIn("k8s://namespaces/kube-system", resource_uris)
        
        # Check nodes
        self.assertIn("k8s://nodes/node1", resource_uris)
        self.assertIn("k8s://nodes/node2", resource_uris)
        
        # Check persistent volumes
        self.assertIn("k8s://persistentvolumes/pv1", resource_uris)
        self.assertIn("k8s://persistentvolumes/pv2", resource_uris)
        
        # Check namespace-specific resources
        self.assertIn("k8s://namespaces/default/pods/pod1", resource_uris)
        self.assertIn("k8s://namespaces/default/pods/pod2", resource_uris)
        self.assertIn("k8s://namespaces/default/deployments/deploy1", resource_uris)
        self.assertIn("k8s://namespaces/default/deployments/deploy2", resource_uris)
        self.assertIn("k8s://namespaces/default/services/svc1", resource_uris)
        self.assertIn("k8s://namespaces/default/services/svc2", resource_uris)
        self.assertIn("k8s://namespaces/default/persistentvolumeclaims/pvc1", resource_uris)
        self.assertIn("k8s://namespaces/default/persistentvolumeclaims/pvc2", resource_uris)
        
        # Verify that the K8s client methods were called
        # get_namespaces is called twice: once for listing namespace resources and once for processing namespace-specific resources
        self.assertEqual(self.k8s_client.get_namespaces.call_count, 2)
        self.k8s_client.get_nodes.assert_called_once()
        self.k8s_client.get_persistent_volumes.assert_called_once()
        
        # These should be called twice (once for each namespace)
        self.assertEqual(self.k8s_client.get_pods.call_count, 2)
        self.assertEqual(self.k8s_client.get_deployments.call_count, 2)
        self.assertEqual(self.k8s_client.get_services.call_count, 2)
        self.assertEqual(self.k8s_client.get_persistent_volume_claims.call_count, 2)

    def test_list_resources_with_errors(self):
        """Test listing resources when some K8s client methods raise exceptions."""
        # Mock the K8sClient methods
        self.k8s_client.get_namespaces.return_value = [{"name": "default"}]
        self.k8s_client.get_nodes.side_effect = Exception("Failed to get nodes")
        self.k8s_client.get_persistent_volumes.return_value = [{"name": "pv1"}]
        self.k8s_client.get_pods.return_value = [{"name": "pod1"}]
        self.k8s_client.get_deployments.side_effect = Exception("Failed to get deployments")
        self.k8s_client.get_services.return_value = [{"name": "svc1"}]
        self.k8s_client.get_persistent_volume_claims.return_value = [{"name": "pvc1"}]
        
        # Call the function
        resources = self.list_resources_func()
        
        # Verify the results
        self.assertIsInstance(resources, list)
        self.assertGreater(len(resources), 0)
        
        # Check that all resources are of the correct type
        for resource in resources:
            self.assertIsInstance(resource, Resource)
        
        # Verify that the expected resources are included
        resource_uris = [str(r.uri) for r in resources]
        
        # Check namespaces
        self.assertIn("k8s://namespaces/default", resource_uris)
        
        # Check persistent volumes
        self.assertIn("k8s://persistentvolumes/pv1", resource_uris)
        
        # Check namespace-specific resources
        self.assertIn("k8s://namespaces/default/pods/pod1", resource_uris)
        self.assertIn("k8s://namespaces/default/services/svc1", resource_uris)
        self.assertIn("k8s://namespaces/default/persistentvolumeclaims/pvc1", resource_uris)
        
        # Check that nodes and deployments are not included (due to errors)
        self.assertNotIn("k8s://nodes/node1", resource_uris)
        self.assertNotIn("k8s://namespaces/default/deployments/deploy1", resource_uris)

    def test_read_resource_namespaced(self):
        """Test reading a namespaced resource."""
        # Mock the K8sClient methods
        pod_data = {"name": "test-pod", "namespace": "default", "status": {"phase": "Running"}}
        self.k8s_client.get_pod.return_value = pod_data
        
        # Call the function
        result = self.read_resource_func("k8s://namespaces/default/pods/test-pod")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, pod_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod.assert_called_once_with("test-pod", "default")

    def test_read_resource_non_namespaced(self):
        """Test reading a non-namespaced resource."""
        # Mock the K8sClient methods
        node_data = {"name": "test-node", "status": {"capacity": {"cpu": "4"}}}
        self.k8s_client.get_node.return_value = node_data
        
        # Call the function
        result = self.read_resource_func("k8s://nodes/test-node")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, node_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_node.assert_called_once_with("test-node")

    def test_read_resource_namespace(self):
        """Test reading a namespace resource."""
        # Mock the K8sClient methods
        namespace_data = [{"name": "test-namespace"}]
        pods_data = [{"name": "pod1"}, {"name": "pod2"}]
        deployments_data = [{"name": "deploy1"}, {"name": "deploy2"}]
        services_data = [{"name": "svc1"}, {"name": "svc2"}]
        pvcs_data = [{"name": "pvc1"}, {"name": "pvc2"}]
        
        self.k8s_client.get_namespaces.return_value = namespace_data
        self.k8s_client.get_pods.return_value = pods_data
        self.k8s_client.get_deployments.return_value = deployments_data
        self.k8s_client.get_services.return_value = services_data
        self.k8s_client.get_persistent_volume_claims.return_value = pvcs_data
        
        # Call the function
        result = self.read_resource_func("k8s://namespaces/test-namespace")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        
        # Check that the namespace info is included
        self.assertIn("namespace", parsed_result)
        self.assertEqual(parsed_result["namespace"], {"name": "test-namespace"})
        
        # Check that the pods are included
        self.assertIn("pods", parsed_result)
        self.assertEqual(parsed_result["pods"], pods_data)
        
        # Check that the deployments are included
        self.assertIn("deployments", parsed_result)
        self.assertEqual(parsed_result["deployments"], deployments_data)
        
        # Check that the services are included
        self.assertIn("services", parsed_result)
        self.assertEqual(parsed_result["services"], services_data)
        
        # Check that the persistent volume claims are included
        self.assertIn("persistentvolumeclaims", parsed_result)
        self.assertEqual(parsed_result["persistentvolumeclaims"], pvcs_data)
        
        # Verify that the K8s client methods were called with the correct arguments
        self.k8s_client.get_namespaces.assert_called_once()
        self.k8s_client.get_pods.assert_called_once_with(namespace="test-namespace")
        self.k8s_client.get_deployments.assert_called_once_with(namespace="test-namespace")
        self.k8s_client.get_services.assert_called_once_with(namespace="test-namespace")
        self.k8s_client.get_persistent_volume_claims.assert_called_once_with(namespace="test-namespace")

    def test_read_resource_invalid_uri(self):
        """Test reading a resource with an invalid URI."""
        # Call the function with an invalid URI
        result = self.read_resource_func("invalid://uri")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Invalid resource URI: invalid://uri")

    def test_read_resource_not_found(self):
        """Test reading a resource that doesn't exist."""
        # Mock the K8sClient methods
        self.k8s_client.get_pod.return_value = None
        
        # Call the function
        result = self.read_resource_func("k8s://namespaces/default/pods/nonexistent-pod")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "pods nonexistent-pod not found in namespace default")
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod.assert_called_once_with("nonexistent-pod", "default")

    def test_read_resource_unsupported_type(self):
        """Test reading a resource with an unsupported type."""
        # Call the function with an unsupported resource type
        result = self.read_resource_func("k8s://namespaces/default/unsupported/test")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Unsupported resource type: unsupported")

    def test_read_resource_with_error(self):
        """Test reading a resource when the K8s client method raises an exception."""
        # Mock the K8sClient methods
        self.k8s_client.get_pod.side_effect = Exception("Failed to get pod")
        
        # Call the function
        result = self.read_resource_func("k8s://namespaces/default/pods/test-pod")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Failed to get pod")
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod.assert_called_once_with("test-pod", "default")


if __name__ == "__main__":
    unittest.main()
