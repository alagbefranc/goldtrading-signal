#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for MetaTrader 5 MCP Server connection
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

def test_mcp_connection(max_retries=5):
    """Test connection to MetaTrader 5 MCP Server with retries"""
    print("Testing connection to MT5 MCP Server...")
    
    server_url = os.getenv("MT5_SERVER_URL", "http://127.0.0.1:8000")
    
    # Get MT5 credentials from environment variables
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"Using MCP Server URL: {server_url}")
    print(f"MT5 Account: {account}")
    print(f"MT5 Server: {server}")
    
    # Try to connect with retries
    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt}/{max_retries}:")
        
        # Step 1: Test if server is responding
        try:
            print("\nChecking if server is responding...")
            response = requests.get(f"{server_url}/health", timeout=5)
            print(f"Health endpoint response status: {response.status_code}")
            if response.status_code == 200:
                print("Server is responding!")
            else:
                print(f"Server returned non-200 status: {response.status_code}")
                if attempt < max_retries:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
        except Exception as e:
            print(f"Error connecting to server: {e}")
            if attempt < max_retries:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
                continue
        
        # Step 2: Initialize MT5
        try:
            print("\nInitializing MT5...")
            response = requests.post(
                f"{server_url}/initialize", 
                headers={"Content-Type": "application/json"}
            )
            print(f"Initialize endpoint response status: {response.status_code}")
            if response.status_code == 200:
                print("MT5 initialized successfully!")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"MT5 initialization failed with status: {response.status_code}")
                if hasattr(response, 'text'):
                    print(f"Response text: {response.text}")
                if attempt < max_retries:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
        except Exception as e:
            print(f"Error initializing MT5: {e}")
            if attempt < max_retries:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
                continue
        
        # Step 3: Login to MT5 account
        try:
            print("\nLogging in to MT5 account...")
            
            data = {
                "account": account,
                "password": password,
                "server": server
            }
            
            response = requests.post(
                f"{server_url}/login", 
                headers={"Content-Type": "application/json"},
                json=data
            )
            
            print(f"Login endpoint response status: {response.status_code}")
            if response.status_code == 200:
                print("Login successful!")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                
                # Success - we've connected and logged in
                return True
            else:
                print(f"Login failed with status: {response.status_code}")
                if hasattr(response, 'text'):
                    print(f"Response text: {response.text}")
                if attempt < max_retries:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
        except Exception as e:
            print(f"Error logging in to MT5: {e}")
            if attempt < max_retries:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
                continue
    
    print("\nAll connection attempts failed.")
    return False

if __name__ == "__main__":
    print("=== MetaTrader 5 MCP Server Connection Test ===")
    success = test_mcp_connection()
    
    if success:
        print("\n✓ MCP Server connection test PASSED!")
        print("Your MT5 account is successfully connected through the MCP Server")
    else:
        print("\n✗ MCP Server connection test FAILED!")
        print("Please check the MCP Server status and your MT5 credentials")
