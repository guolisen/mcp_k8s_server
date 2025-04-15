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
        
        # Mock the decorator to capture the decorated function
        def mock_tool_decorator(arguments_type=None):
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

    def test_datetime_encoder(self):
        """Test the DateTimeEncoder class."""
        # Create a datetime object
        dt = datetime(2023, 1, 1, 12, 0, 0)
        date_only = datetime(2023, 1, 1).date()
        
        # Create a dictionary with the datetime objects
        data = {"timestamp": dt, "date": date_only}
        
        # Encode the dictionary
        encoded = json.dumps(data, cls=DateTimeEncoder)
        
        # Decode the JSON
        decoded = json.loads(encoded)
        
        # Verify the results
        self.assertEqual(decoded["timestamp"], "2023-01-01 12:00:00")
        self.assertEqual(decoded["date"], "2023-01-01")

    def test_get_resources(self):
        """Test getting resources."""
        # Mock the K8sClient methods
        pods_data = [{"name": "pod1"}, {"name": "pod2"}]
        self.k8s_client.get_pods.return_value = pods_data
        
        # Call the function directly with parameters
        result = self.get_resources_func("pods", "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, pods_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pods.assert_called_once_with("default")

    def test_get_resources_unsupported_type(self):
        """Test getting resources with unsupported type."""
        # Call the function with unsupported resource type
        result = self.get_resources_func("unsupported")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Unsupported resource type: unsupported")

    def test_get_resources_with_error(self):
        """Test getting resources when the K8s client method raises an exception."""
        # Mock the K8sClient methods to raise an exception
        self.k8s_client.get_pods.side_effect = Exception("Failed to get pods")
        
        # Call the function
        result = self.get_resources_func("pods")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertIn("error", parsed_result)
        self.assertEqual(parsed_result["error"], "Failed to get pods")

    def test_get_resource(self):
        """Test getting a resource."""
        # Mock the K8sClient methods
        pod_data = {"name": "test-pod", "namespace": "default", "status": {"phase": "Running"}}
        self.k8s_client.get_pod.return_value = pod_data
        
        # Call the function
        result = self.get_resource_func("pod", "test-pod", "default")
        
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
        result = self.get_resource_func("pod", "nonexistent-pod", "default")
        
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
        result = self.get_resource_status_func("pod", "test-pod", "default")
        
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
        result = self.get_resource_events_func("pod", "test-pod", "default")
        
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
        result = self.get_pod_logs_func("test-pod", "default", "main", 10)
        
        # Verify the results
        self.assertEqual(result, logs_data)
        
        # Verify that the K8s client method was called with the correct arguments
        self.k8s_client.get_pod_logs.assert_called_once_with("test-pod", "default", "main", 10)


if __name__ == "__main__":
    unittest.main()
