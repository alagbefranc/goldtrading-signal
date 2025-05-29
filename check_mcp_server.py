#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to check if the MetaTrader 5 MCP Server is running
"""

import os
import sys
import socket
import requests
import time
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_port_open(host, port, timeout=2):
    """Check if a port is open on a host"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def check_mcp_server():
    """Check if the MCP server is running"""
    host = "127.0.0.1"
    port = 8000
    
    print(f"Checking if port {port} is open on {host}...")
    port_open = check_port_open(host, port)
    print(f"Port {port} {'is' if port_open else 'is not'} open on {host}")
    
    if port_open:
        # Try to get the health status
        print(f"\nTrying to connect to http://{host}:{port}/health...")
        try:
            response = requests.get(f"http://{host}:{port}/health", timeout=5)
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response body: {response.text}")
                return True
            else:
                print(f"Response error: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to MCP server: {e}")
            return False
    else:
        print("MCP server is not running")
        return False

if __name__ == "__main__":
    print("Checking MetaTrader 5 MCP Server status...")
    check_mcp_server()
