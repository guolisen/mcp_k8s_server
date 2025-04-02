#!/usr/bin/env python3
"""Script to run all tests for the MCP Kubernetes server."""

import os
import sys
import unittest
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def run_all_tests():
    """Run all tests in the tests directory."""
    logger.info("Running all tests")
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return success or failure
    return result.wasSuccessful()


def run_ssl_verify_tests():
    """Run SSL verification tests."""
    logger.info("Running SSL verification tests")
    
    # Run the SSL verification unit tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromName("tests.test_ssl_verify")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return success or failure
    return result.wasSuccessful()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for the MCP Kubernetes server")
    parser.add_argument("--ssl-verify", action="store_true",
                        help="Run only SSL verification tests")
    args = parser.parse_args()
    
    if args.ssl_verify:
        success = run_ssl_verify_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
