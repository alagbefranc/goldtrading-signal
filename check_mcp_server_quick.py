#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quick test to check if the MetaTrader 5 MCP Server is accessible
"""

import requests
import time
import socket

def is_port_open(host, port, timeout=2):
    """Check if a port is open on a host"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

# Check if port 8000 is open
print("Checking if port 8000 is open...")
if is_port_open("127.0.0.1", 8000):
    print("✓ Port 8000 is OPEN - server is likely running")
    
    # Try to connect to health endpoint
    try:
        print("\nTrying to connect to MCP server health endpoint...")
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print("\n✓ Successfully connected to MCP server!")
    except Exception as e:
        print(f"\n✗ Failed to connect to health endpoint: {e}")
else:
    print("✗ Port 8000 is CLOSED - server is not running")
    
    # Suggest solution
    print("\nSuggested solutions:")
    print("1. Make sure the MCP server is running in a separate terminal")
    print("2. Check the MCP server logs for any errors")
    print("3. Try restarting the MCP server using the run_mcp_server.bat file")
