#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Check MCP Server with timeout - keeps trying for a specified duration
"""

import socket
import requests
import time
import sys

def check_port(host, port, timeout=2):
    """Check if a port is open using raw socket connection"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def main(max_attempts=10, delay=2):
    """Check if MCP server is running with multiple attempts"""
    host = "127.0.0.1"
    port = 8000
    
    print(f"Checking if MCP server is running at {host}:{port}")
    print(f"Will make {max_attempts} attempts with {delay} seconds between each")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt}/{max_attempts}:")
        
        if check_port(host, port):
            print(f"✓ Success! Port {port} is open - server is running")
            
            # Try to access health endpoint
            try:
                print(f"Checking health endpoint...")
                response = requests.get(f"http://{host}:{port}/health", timeout=5)
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
                print("\nMCP server is running and responding!")
                return True
            except Exception as e:
                print(f"Error accessing health endpoint: {e}")
        else:
            print(f"✗ Port {port} is not open - server is not running")
        
        if attempt < max_attempts:
            print(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print("\nFailed to connect to MCP server after all attempts")
    return False

if __name__ == "__main__":
    main()
