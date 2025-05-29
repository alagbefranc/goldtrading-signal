#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for MT5 MCP Server connection
"""

import os
import sys
import time
import logging
import requests
import json
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_mcp_connection():
    """Test connection to MT5 MCP Server"""
    print("Testing connection to MT5 MCP Server...")
    
    server_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        print(f"Testing health endpoint: {server_url}/health")
        response = requests.get(f"{server_url}/health", timeout=5)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("Health endpoint is working!")
        else:
            print(f"Health endpoint returned non-200 status: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to health endpoint: {e}")
    
    # Test initialize endpoint
    try:
        print(f"\nTesting initialize endpoint: {server_url}/initialize")
        response = requests.post(f"{server_url}/initialize", headers={"Content-Type": "application/json"})
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("Initialize endpoint is working!")
            print(f"Response: {response.json()}")
        else:
            print(f"Initialize endpoint returned non-200 status: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to initialize endpoint: {e}")
    
    # Test login endpoint
    try:
        print(f"\nTesting login endpoint: {server_url}/login")
        
        # Get MT5 credentials from environment variables
        account = os.getenv("MT5_ACCOUNT", "210053016")
        password = os.getenv("MT5_PASSWORD", "Korede16@@")
        server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
        
        data = {
            "account": account,
            "password": password,
            "server": server
        }
        
        print(f"Login data: account={account}, server={server}")
        
        response = requests.post(
            f"{server_url}/login", 
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            print("Login endpoint is working!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Login endpoint returned non-200 status: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Error connecting to login endpoint: {e}")
    
    print("\nConnection test completed!")

if __name__ == "__main__":
    test_mcp_connection()
