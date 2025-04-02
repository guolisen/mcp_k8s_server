#!/usr/bin/env python3
"""Test runner for MCP Kubernetes server tests."""

import unittest
import sys
import os

# Add the parent directory to the path so that imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests.test_cluster_resources import TestClusterResources
from tests.test_resource_tools import TestResourceTools

if __name__ == "__main__":
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestClusterResources))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceTools))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero status if there were failures
    sys.exit(not result.wasSuccessful())
