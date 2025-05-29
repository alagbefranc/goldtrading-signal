#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Detailed MCP Server connection test
"""

import socket
import requests
import time
import sys

def check_port(host, port, timeout=2):
    """Check if a port is open using raw socket connection"""
    print(f"Checking if port {port} is open on {host} using socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"✓ Port {port} is OPEN on {host}")
        return True
    else:
        print(f"✗ Port {port} is CLOSED on {host} (error code: {result})")
        return False

def test_http_endpoint(url, timeout=5):
    """Test an HTTP endpoint with detailed information"""
    print(f"\nTesting HTTP endpoint: {url}")
    try:
        print("Sending request...")
        response = requests.get(url, timeout=timeout)
        print(f"Response received. Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        return True
    except requests.exceptions.Timeout:
        print(f"✗ Request timed out after {timeout} seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    
    print("=== Detailed MCP Server Connection Test ===\n")
    
    # Check if port is open
    if check_port(host, port):
        # Test health endpoint
        test_http_endpoint(f"http://{host}:{port}/health")
        
        # Test initialize endpoint
        test_http_endpoint(f"http://{host}:{port}/initialize")
    else:
        print("\nSuggested fixes:")
        print("1. Make sure the MCP server process is running")
        print("2. Check if another process is using port 8000")
        print("3. Try starting the server with a different port")
        print("4. Check for any error messages in the server terminal")
        
    print("\nTest completed.")
