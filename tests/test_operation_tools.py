#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Lewis Guo. All rights reserved.
# Author: Lewis Guo <guolisen@gmail.com>
# Created: April 15, 2025
#
# Description: Tests for the operation tools module.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from mcp_k8s_server.k8s.operations import K8sOperations
from mcp_k8s_server.tools.operation_tools import register_operation_tools, DateTimeEncoder


class TestOperationTools(unittest.TestCase):
    """Test cases for operation tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = MagicMock(spec=FastMCP)
        self.k8s_operations = MagicMock(spec=K8sOperations)
        
        # Store the decorated functions
        self.create_resource_func = None
        self.update_resource_func = None
        self.delete_resource_func = None
        self.scale_deployment_func = None
        self.restart_deployment_func = None
        self.execute_command_on_pod_func = None
        
        # Mock the decorator to capture the decorated function
        def mock_tool_decorator(arguments_type=None):
            def decorator(func):
                # Store the function based on its name
                if func.__name__ == "create_resource":
                    self.create_resource_func = func
                elif func.__name__ == "update_resource":
                    self.update_resource_func = func
                elif func.__name__ == "delete_resource":
                    self.delete_resource_func = func
                elif func.__name__ == "scale_deployment":
                    self.scale_deployment_func = func
                elif func.__name__ == "restart_deployment":
                    self.restart_deployment_func = func
                elif func.__name__ == "execute_command_on_pod":
                    self.execute_command_on_pod_func = func
                return func
            return decorator
        
        # Apply the mock
        self.mcp.tool = mock_tool_decorator
        
        # Register the tools
        register_operation_tools(self.mcp, self.k8s_operations)

    def test_tools_registration(self):
        """Test that all tools are registered with the MCP server."""
        self.assertIsNotNone(self.create_resource_func, "create_resource function was not registered")
        self.assertIsNotNone(self.update_resource_func, "update_resource function was not registered")
        self.assertIsNotNone(self.delete_resource_func, "delete_resource function was not registered")
        self.assertIsNotNone(self.scale_deployment_func, "scale_deployment function was not registered")
        self.assertIsNotNone(self.restart_deployment_func, "restart_deployment function was not registered")
        self.assertIsNotNone(self.execute_command_on_pod_func, "execute_command_on_pod function was not registered")

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
        
        # Test with a non-datetime object
        other_obj = object()
        encoder = DateTimeEncoder()
        
        # This should raise TypeError as the default method doesn't handle arbitrary objects
        with self.assertRaises(TypeError):
            encoder.default(other_obj)

    def test_create_resource(self):
        """Test creating a resource."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Created Pod test-pod in namespace default",
            "resource": {"kind": "Pod", "metadata": {"name": "test-pod"}}
        }
        self.k8s_operations.create_resource.return_value = success_response
        
        # Sample YAML resource
        resource_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:latest
"""
        
        # Call the function
        result = self.create_resource_func(resource_yaml)
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.create_resource.assert_called_once_with(resource_yaml)

    def test_create_resource_error(self):
        """Test creating a resource with an error."""
        # Mock the K8sOperations to raise an exception
        self.k8s_operations.create_resource.side_effect = Exception("Failed to create resource")
        
        # Sample YAML resource
        resource_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:latest
"""
        
        # Call the function
        result = self.create_resource_func(resource_yaml)
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Failed to create resource")

    def test_update_resource(self):
        """Test updating a resource."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Updated Pod test-pod in namespace default",
            "resource": {"kind": "Pod", "metadata": {"name": "test-pod"}}
        }
        self.k8s_operations.update_resource.return_value = success_response
        
        # Sample YAML resource
        resource_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:1.19
"""
        
        # Call the function
        result = self.update_resource_func(resource_yaml)
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.update_resource.assert_called_once_with(resource_yaml)

    def test_update_resource_error(self):
        """Test updating a resource with an error."""
        # Mock the K8sOperations to raise an exception
        self.k8s_operations.update_resource.side_effect = Exception("Failed to update resource")
        
        # Sample YAML resource
        resource_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:1.19
"""
        
        # Call the function
        result = self.update_resource_func(resource_yaml)
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Failed to update resource")

    def test_delete_resource(self):
        """Test deleting a resource."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Deleted Pod test-pod in namespace default",
        }
        self.k8s_operations.delete_resource.return_value = success_response
        
        # Call the function
        result = self.delete_resource_func("Pod", "test-pod", "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.delete_resource.assert_called_once_with("Pod", "test-pod", "default")

    def test_delete_resource_with_default_namespace(self):
        """Test deleting a resource with default namespace."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Deleted Pod test-pod in namespace default",
        }
        self.k8s_operations.delete_resource.return_value = success_response
        
        # Call the function without specifying namespace
        result = self.delete_resource_func("Pod", "test-pod")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.delete_resource.assert_called_once_with("Pod", "test-pod", None)

    def test_delete_resource_error(self):
        """Test deleting a resource with an error."""
        # Mock the K8sOperations to raise an exception
        self.k8s_operations.delete_resource.side_effect = Exception("Failed to delete resource")
        
        # Call the function
        result = self.delete_resource_func("Pod", "test-pod", "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Failed to delete resource")

    def test_scale_deployment(self):
        """Test scaling a deployment."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Scaled deployment test-deployment to 3 replicas in namespace default",
        }
        self.k8s_operations.scale_deployment.return_value = success_response
        
        # Call the function
        result = self.scale_deployment_func("test-deployment", 3, "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.scale_deployment.assert_called_once_with("test-deployment", 3, "default")

    def test_scale_deployment_with_default_namespace(self):
        """Test scaling a deployment with default namespace."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Scaled deployment test-deployment to 3 replicas in namespace default",
        }
        self.k8s_operations.scale_deployment.return_value = success_response
        
        # Call the function without specifying namespace
        result = self.scale_deployment_func("test-deployment", 3)
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.scale_deployment.assert_called_once_with("test-deployment", 3, None)

    def test_scale_deployment_error(self):
        """Test scaling a deployment with an error."""
        # Mock the K8sOperations to raise an exception
        self.k8s_operations.scale_deployment.side_effect = Exception("Failed to scale deployment")
        
        # Call the function
        result = self.scale_deployment_func("test-deployment", 3, "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Failed to scale deployment")

    def test_restart_deployment(self):
        """Test restarting a deployment."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Restarted deployment test-deployment in namespace default",
        }
        self.k8s_operations.restart_deployment.return_value = success_response
        
        # Call the function
        result = self.restart_deployment_func("test-deployment", "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.restart_deployment.assert_called_once_with("test-deployment", "default")

    def test_restart_deployment_with_default_namespace(self):
        """Test restarting a deployment with default namespace."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Restarted deployment test-deployment in namespace default",
        }
        self.k8s_operations.restart_deployment.return_value = success_response
        
        # Call the function without specifying namespace
        result = self.restart_deployment_func("test-deployment")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.restart_deployment.assert_called_once_with("test-deployment", None)

    def test_restart_deployment_error(self):
        """Test restarting a deployment with an error."""
        # Mock the K8sOperations to raise an exception
        self.k8s_operations.restart_deployment.side_effect = Exception("Failed to restart deployment")
        
        # Call the function
        result = self.restart_deployment_func("test-deployment", "default")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Failed to restart deployment")

    def test_execute_command_on_pod(self):
        """Test executing a command on a pod."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Executed command in pod test-pod in namespace default",
            "output": "command output"
        }
        self.k8s_operations.execute_command.return_value = success_response
        
        # Call the function
        result = self.execute_command_on_pod_func(
            pod_name="test-pod",
            command="ls -la",
            namespace="default",
            container="main"
        )
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.execute_command.assert_called_once_with(
            "test-pod", ["ls", "-la"], "default", "main"
        )

    def test_execute_command_on_pod_with_default_values(self):
        """Test executing a command on a pod with default values."""
        # Mock the K8sOperations
        success_response = {
            "success": True,
            "message": "Executed command in pod test-pod in namespace default",
            "output": "command output"
        }
        self.k8s_operations.execute_command.return_value = success_response
        
        # Call the function without specifying namespace and container
        result = self.execute_command_on_pod_func(
            pod_name="test-pod",
            command="ls -la"
        )
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, success_response)
        
        # Verify that the K8s operations method was called with the correct arguments
        self.k8s_operations.execute_command.assert_called_once_with(
            "test-pod", ["ls", "-la"], None, None
        )

    def test_execute_command_on_pod_missing_pod_name(self):
        """Test executing a command on a pod with missing pod name."""
        # Call the function without pod_name
        result = self.execute_command_on_pod_func(
            command="ls -la",
            namespace="default"
        )
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Missing required parameter: pod_name")

    def test_execute_command_on_pod_missing_command(self):
        """Test executing a command on a pod with missing command."""
        # Call the function without command
        result = self.execute_command_on_pod_func(
            pod_name="test-pod",
            namespace="default"
        )
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Missing required parameter: command")

    def test_execute_command_on_pod_with_value_parameter(self):
        """Test executing a command on a pod with value parameter."""
        # Call the function with a value parameter (should handle error)
        result = self.execute_command_on_pod_func(value=123)
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertIn("Invalid arguments: expected dictionary", parsed_result["message"])

    def test_execute_command_on_pod_with_string_value(self):
        """Test executing a command on a pod with string value parameter."""
        # Call the function with a string value parameter (should handle error)
        result = self.execute_command_on_pod_func(value="ls -la")
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertIn("Invalid arguments: missing 'pod_name'", parsed_result["message"])

    def test_execute_command_on_pod_error(self):
        """Test executing a command on a pod with an error."""
        # Mock the K8sOperations to raise an exception
        self.k8s_operations.execute_command.side_effect = Exception("Failed to execute command")
        
        # Call the function
        result = self.execute_command_on_pod_func(
            pod_name="test-pod",
            command="ls -la",
            namespace="default"
        )
        
        # Verify the results
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["success"], False)
        self.assertEqual(parsed_result["message"], "Failed to execute command")


if __name__ == "__main__":
    unittest.main()
