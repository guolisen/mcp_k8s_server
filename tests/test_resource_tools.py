#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 05, 2025
#
# Description: Tests for the resource tools module.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from mcp_k8s_server.k8s.client import K8sClient
from mcp_k8s_server.tools.resource_tools import register_resource_tools, DateTimeEncoder


class TestResourceTools(unittest.TestCase):
    """Test cases for resource tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = MagicMock(spec=FastMCP)
        self.k8s_client = MagicMock(spec=K8sClient)
        
        # Store the decorated functions
        self.get_resources_func = None
        self.get_resource_func = None
        self.get_resource_status_func = None
        self.get_resource_events_func = None
        self.get_pod_logs_func = None
        self.list_custom_resources_func = None
        self.get_custom_resource_func = None
        
        # Mock the decorator to capture the decorated function
        def mock_tool_decorator(arguments_type="dict"):
            def decorator(func):
                # Store the function based on its name
                if func.__name__ == "get_resources":
                    self.get_resources_func = func
                elif func.__name__ == "get_resource":
                    self.get_resource_func = func
                elif func.__name__ == "get_resource_status":
                    self.get_resource_status_func = func
                elif func.__name__ == "get_resource_events":
                    self.get_resource_events_func = func
                elif func.__name__ == "get_pod_logs":
                    self.get_pod_logs_func = func
                elif func.__name__ == "list_custom_resources":
                    self.list_custom_resources_func = func
                elif func.__name__ == "get_custom_resource":
                    self.get_custom_resource_func = func
                return func
            return decorator
        
        # Apply the mock
        self.mcp.tool = mock_tool_decorator
        
        # Register the tools
        register_resource_tools(self.mcp, self.k8s_client)

    def test_tools_registration(self):
        """Test that all tools are registered with the MCP server."""
        self.assertIsNotNone(self.get_resources_func, "get_resources function was not registered")
        self.assertIsNotNone(self.get_resource_func, "get_resource function was not registered")
        self.assertIsNotNone(self.get_resource_status_func, "get_resource_status function was not registered")
        self.assertIsNotNone(self.get_resource_events_func, "get_resource_events function was not registered")
        self.assertIsNotNone(self.get_pod_logs_func, "get_pod_logs function was not registered")
        self.assertIsNotNone(self.list_custom_resources_func, "list_custom_resources function was not registered")
        self.assertIsNotNone(self.get_custom_resource_func, "get_custom_resource function was not registered")

    def test_datetime_encoder(self):
        """Test the DateTimeEncoder class."""
        # Create a datetime object
        dt = datetime(2023, 1, 1, 12, 0, 0)
        
        # Create a dictionary with the datetime object
        data = {"timestamp": dt}
        
        # Encode the dictionary
        encoded = json.dumps(data, cls=DateTimeEncoder)
        
        # Decode the JSON
        decoded = json.loads(encoded)
        
        # Verify the results
        self.assertEqual(decoded["timestamp"], "2023-01-01T12:00:00")

    def test_get_resources(self):
        """Test getting resources."""
        # Mock the K8sClient methods
        pods_data = [{"name": "pod1"}, {"name": "pod2"}]
        self.k8s_client.get_pods.return_value = pods_data
        
        # Call the function
        result = self.get_resources_func({"resource_type": "pods", "namespace": "default"})
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, pods_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pods.assert_called_once_with("default")

    def test_get_resources_invalid_arguments(self):
        """Test getting resources with invalid arguments."""
        # Call the function with invalid arguments
        result = self.get_resources_func("invalid")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Invalid arguments: expected dictionary, got str")
        self.assertEqual(parsed_result["success"], False)

    def test_get_resources_missing_required_parameter(self):
        """Test getting resources with missing required parameter."""
        # Call the function with missing required parameter
        result = self.get_resources_func({})
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Missing required parameter: resource_type")
        self.assertEqual(parsed_result["success"], False)

    def test_get_resources_invalid_parameter_type(self):
        """Test getting resources with invalid parameter type."""
        # Call the function with invalid parameter type
        result = self.get_resources_func({"resource_type": 123})
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Invalid resource_type: expected string, got int")
        self.assertEqual(parsed_result["success"], False)

    def test_get_resources_unsupported_type(self):
        """Test getting resources with unsupported type."""
        # Call the function with unsupported resource type
        result = self.get_resources_func({"resource_type": "unsupported"})
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Unsupported resource type: unsupported")

    def test_get_resources_with_error(self):
        """Test getting resources when the K8s client method raises an exception."""
        # Mock the K8sClient methods
        self.k8s_client.get_pods.side_effect = Exception("Failed to get pods")
        
        # Call the function
        result = self.get_resources_func({"resource_type": "pods"})
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Error getting pods: Failed to get pods")
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["errorType"], "Exception")

    def test_get_resource(self):
        """Test getting a resource."""
        # Mock the K8sClient methods
        pod_data = {"name": "test-pod", "namespace": "default", "status": {"phase": "Running"}}
        self.k8s_client.get_pod.return_value = pod_data
        
        # Call the function
        result = self.get_resource_func({
            "resource_type": "pod",
            "name": "test-pod",
            "namespace": "default"
        })
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, pod_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod.assert_called_once_with("test-pod", "default")

    def test_get_resource_not_found(self):
        """Test getting a resource that doesn't exist."""
        # Mock the K8sClient methods
        self.k8s_client.get_pod.return_value = None
        
        # Call the function
        result = self.get_resource_func({
            "resource_type": "pod",
            "name": "nonexistent-pod",
            "namespace": "default"
        })
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "pod nonexistent-pod not found")

    def test_get_resource_status(self):
        """Test getting a resource status."""
        # Mock the K8sClient methods
        pod_data = {
            "name": "test-pod",
            "namespace": "default",
            "status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]}
        }
        self.k8s_client.get_pod.return_value = pod_data
        
        # Call the function
        result = self.get_resource_status_func({
            "resource_type": "pod",
            "name": "test-pod",
            "namespace": "default"
        })
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, pod_data["status"])
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod.assert_called_once_with("test-pod", "default")

    def test_get_resource_events(self):
        """Test getting resource events."""
        # Mock the K8sClient methods
        events_data = [
            {"type": "Normal", "reason": "Started", "message": "Started container"},
            {"type": "Warning", "reason": "Unhealthy", "message": "Liveness probe failed"}
        ]
        self.k8s_client.get_resource_events.return_value = events_data
        
        # Call the function
        result = self.get_resource_events_func({
            "resource_type": "pod",
            "name": "test-pod",
            "namespace": "default"
        })
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, events_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_resource_events.assert_called_once_with("pod", "test-pod", "default")

    def test_get_pod_logs(self):
        """Test getting pod logs."""
        # Mock the K8sClient methods
        logs_data = "Line 1\nLine 2\nLine 3"
        self.k8s_client.get_pod_logs.return_value = logs_data
        
        # Call the function
        result = self.get_pod_logs_func({
            "name": "test-pod",
            "namespace": "default",
            "container": "main",
            "tail_lines": 10
        })
        
        # Verify the results
        self.assertEqual(result, logs_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod_logs.assert_called_once_with("test-pod", "default", "main", 10)

    def test_list_custom_resources(self):
        """Test listing custom resources."""
        # Mock the K8sClient methods
        custom_resources_data = [
            {"name": "cr1", "spec": {"replicas": 3}},
            {"name": "cr2", "spec": {"replicas": 2}}
        ]
        self.k8s_client.list_custom_resources.return_value = custom_resources_data
        
        # Call the function
        result = self.list_custom_resources_func({
            "group": "example.com",
            "version": "v1",
            "plural": "examples",
            "namespace": "default"
        })
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, custom_resources_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.list_custom_resources.assert_called_once_with(
            "example.com", "v1", "examples", "default"
        )

    def test_get_custom_resource(self):
        """Test getting a custom resource."""
        # Mock the K8sClient methods
        custom_resource_data = {"name": "test-cr", "spec": {"replicas": 3}}
        self.k8s_client.get_custom_resource.return_value = custom_resource_data
        
        # Call the function
        result = self.get_custom_resource_func({
            "group": "example.com",
            "version": "v1",
            "plural": "examples",
            "name": "test-cr",
            "namespace": "default"
        })
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, custom_resource_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_custom_resource.assert_called_once_with(
            "example.com", "v1", "examples", "test-cr", "default"
        )


if __name__ == "__main__":
    unittest.main()
