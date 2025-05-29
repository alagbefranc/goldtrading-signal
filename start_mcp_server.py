#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Start the MetaTrader 5 MCP Server directly
This script will start the MCP server and keep it running
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def find_mt5_terminal():
    """Find the MetaTrader 5 terminal path"""
    # Common MT5 installation paths
    possible_paths = [
        os.path.expanduser("~/AppData/Roaming/MetaQuotes/Terminal"),
        "C:/Program Files/MetaTrader 5",
        "C:/Program Files (x86)/MetaTrader 5",
        # Add your MT5 path here if different
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found MetaTrader 5 at: {path}")
            return path
    
    logger.warning("MetaTrader 5 terminal not found. Continuing anyway...")
    return None

def start_mt5_server():
    """Start the MetaTrader 5 MCP Server"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the mcp-metatrader5-server directory
    mcp_server_dir = os.path.join(os.path.dirname(script_dir), "mcp-metatrader5-server")
    
    if not os.path.exists(mcp_server_dir):
        logger.error(f"MCP server directory not found at: {mcp_server_dir}")
        return False
    
    # Path to the server script
    server_script = os.path.join(mcp_server_dir, "mt5_server.py")
    
    if not os.path.exists(server_script):
        logger.error(f"MCP server script not found at: {server_script}")
        return False
    
    # Find MetaTrader 5 terminal
    mt5_terminal = find_mt5_terminal()
    
    logger.info(f"Starting MetaTrader 5 MCP Server from: {server_script}")
    
    try:
        # Start the server
        process = subprocess.Popen(
            [
                sys.executable,
                server_script,
                "--host", "127.0.0.1",
                "--port", "8000"
            ],
            cwd=mcp_server_dir
        )
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Check if the server is running
        if process.poll() is None:
            logger.info("MetaTrader 5 MCP Server started successfully")
            
            # Print instructions
            print("\n" + "="*50)
            print("MetaTrader 5 MCP Server")
            print("="*50)
            print("\nServer is running at: http://127.0.0.1:8000")
            print("\nMake sure MetaTrader 5 is open and logged in to your account:")
            print(f"  Account: {os.getenv('MT5_ACCOUNT', '210053016')}")
            print(f"  Server: {os.getenv('MT5_SERVER', 'Exness-MT5Trial9')}")
            print("\nPress Ctrl+C to stop the server")
            print("="*50 + "\n")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
                    # Check if process is still running
                    if process.poll() is not None:
                        logger.error("Server process terminated unexpectedly")
                        return False
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt. Stopping server...")
                process.terminate()
                process.wait(timeout=5)
                logger.info("Server stopped")
            
            return True
        else:
            logger.error("Failed to start MetaTrader 5 MCP Server")
            return False
    except Exception as e:
        logger.error(f"Error starting MetaTrader 5 MCP Server: {e}")
        return False

if __name__ == "__main__":
    start_mt5_server()
