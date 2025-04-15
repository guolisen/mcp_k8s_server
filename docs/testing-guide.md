# MCP Kubernetes Server Testing Guide

This document provides instructions on how to run tests for the MCP Kubernetes Server.

## Test Structure

The test suite for the MCP Kubernetes Server is organized as follows:

- `tests/test_cluster_resources.py`: Tests for the cluster resources module.
- `tests/test_resource_tools.py`: Tests for the resource tools module.
- `tests/test_operation_tools.py`: Tests for the operation tools module.
- `tests/run_tests.py`: Main test runner that runs all tests.
- `tests/run_operation_tests.py`: Specialized test runner for operation tools tests only.

## Running Tests

### Run All Tests

To run all tests at once, execute the following command from the project root directory:

```bash
cd tests && python run_tests.py
```

This will run all test cases and report any failures.

### Run Tests for a Specific Module

You can run tests for a specific module using Python's unittest module directly. For example:

```bash
# Run operation tools tests
cd tests && python -m unittest test_operation_tools

# Run resource tools tests
cd tests && python -m unittest test_resource_tools

# Run cluster resources tests
cd tests && python -m unittest test_cluster_resources
```

For more verbose output, add the `-v` flag:

```bash
cd tests && python -m unittest -v test_operation_tools
```

### Run Operation Tools Tests Only

There's a dedicated script for running just the operation tools tests:

```bash
cd tests && ./run_operation_tests.py
```

Make sure the script is executable:

```bash
chmod +x tests/run_operation_tests.py
```

## Adding New Tests

When adding new functionality to the MCP Kubernetes Server, follow these guidelines for testing:

1. Create a test file for your module if it doesn't already exist.
2. Use the unittest framework and follow the existing patterns.
3. Mock external dependencies to isolate the unit under test.
4. Test both normal and error cases.
5. Update `run_tests.py` to include your new test file if needed.

## Testing Principles

- **Independence**: Each test should be independent and not rely on the state created by another test.
- **Coverage**: Aim for high code coverage, testing both normal flows and error conditions.
- **Mocking**: Use mocks for external dependencies to ensure tests are isolated and not affected by external systems.
- **Readability**: Write clear test names that describe what is being tested and what the expected outcome is.

## Common Testing Patterns

### Testing MCP Tools

When testing MCP tools, the general pattern is:

1. Mock the `FastMCP` instance and its `tool` decorator.
2. Register the tools with the mock MCP instance.
3. Test each registered function directly.
4. Test both successful execution and error handling.

Example:

```python
def setUp(self):
    self.mcp = MagicMock(spec=FastMCP)
    self.k8s_operations = MagicMock(spec=K8sOperations)
    
    # Store the decorated functions
    self.create_resource_func = None
    
    # Mock the decorator to capture the decorated function
    def mock_tool_decorator(arguments_type=None):
        def decorator(func):
            if func.__name__ == "create_resource":
                self.create_resource_func = func
            return func
        return decorator
    
    # Apply the mock
    self.mcp.tool = mock_tool_decorator
    
    # Register the tools
    register_operation_tools(self.mcp, self.k8s_operations)

def test_create_resource(self):
    # Mock the K8sOperations
    success_response = {
        "success": True,
        "message": "Created Pod test-pod in namespace default",
        "resource": {"kind": "Pod", "metadata": {"name": "test-pod"}}
    }
    self.k8s_operations.create_resource.return_value = success_response
    
    # Call the function
    result = self.create_resource_func(resource_yaml)
    
    # Verify the results
    self.assertIsInstance(result, str)
    parsed_result = json.loads(result)
    self.assertEqual(parsed_result, success_response)
