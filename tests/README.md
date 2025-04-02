# MCP Kubernetes Server Tests

This directory contains test scripts for the MCP Kubernetes server.

## SSL Verification Tests

The following tests are available for testing SSL verification settings:

### Unit Tests

- `test_ssl_verify.py`: Unit tests for SSL verification settings
  ```bash
  python -m unittest tests/test_ssl_verify.py
  ```

### Integration Tests

- `test_k8s_connection.py`: Test connecting to a Kubernetes cluster with different SSL verification settings
  ```bash
  # Test with SSL verification disabled
  python tests/test_k8s_connection.py --config config/test_config_no_ssl_verify.yaml
  
  # Test with SSL verification enabled
  python tests/test_k8s_connection.py --config config/config.yaml
  ```

- `test_k8s_direct.py`: Test direct Kubernetes API access with SSL verification disabled
  ```bash
  # Test with SSL verification disabled
  python tests/test_k8s_direct.py --no-ssl-verify
  
  # Test with SSL verification enabled
  python tests/test_k8s_direct.py
  ```

- `test_mcp_server.py`: Test the MCP Kubernetes server with SSL verification disabled
  ```bash
  # Test with SSL verification disabled
  python tests/test_mcp_server.py --config config/test_config_no_ssl_verify.yaml
  
  # Test with SSL verification enabled
  python tests/test_mcp_server.py --config config/config.yaml
  ```

- `test_with_config.py`: Test with different configuration files
  ```bash
  # Test with SSL verification disabled
  python tests/test_with_config.py --config config/test_config_no_ssl_verify.yaml
  
  # Test with SSL verification enabled
  python tests/test_with_config.py --config config/config.yaml
  
  # Test with SSL verification disabled but hostname specified
  python tests/test_with_config.py --config config/test_config_no_ssl_with_hostname.yaml
  
  # Test with SSL verification disabled and no hostname specified
  python tests/test_with_config.py --config config/test_config_no_ssl_no_hostname.yaml
  ```

## Configuration Files

The following configuration files are available for testing:

- `config/config.yaml`: Default configuration with SSL verification enabled
- `config/test_config_no_ssl_verify.yaml`: Configuration with SSL verification disabled
- `config/test_config_no_ssl_with_hostname.yaml`: Configuration with SSL verification disabled but hostname specified
- `config/test_config_no_ssl_no_hostname.yaml`: Configuration with SSL verification disabled and no hostname specified

## Running All Tests

To run all tests, you can use the following command:

```bash
python -m unittest discover tests
```

Or run individual tests as shown above.
