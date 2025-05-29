#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to start the MetaTrader 5 MCP Server properly
"""

import os
import sys
import subprocess
import time
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='mcp_server.log'
)
logger = logging.getLogger(__name__)

def main():
    """Start the MCP server"""
    logger.info("Starting MetaTrader 5 MCP Server...")
    
    # Path to MCP server directory
    mcp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp-metatrader5-server")
    server_script = os.path.join(mcp_dir, "mt5_server.py")
    
    logger.info(f"MCP directory: {mcp_dir}")
    logger.info(f"Server script: {server_script}")
    
    # Check if server script exists
    if not os.path.exists(server_script):
        logger.error(f"Server script not found at: {server_script}")
        print(f"Server script not found at: {server_script}")
        return False
    
    # Check if the required packages are installed
    try:
        import MetaTrader5
        import fastmcp
        logger.info("Required packages are installed")
    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        print(f"Required package not installed: {e}")
        print("Installing required packages...")
        
        # Install required packages
        subprocess.run([sys.executable, "-m", "pip", "install", "MetaTrader5", "fastmcp", "pydantic"])
    
    # Change to the MCP server directory
    os.chdir(mcp_dir)
    
    # Command to run the server
    command = [sys.executable, server_script, "--host", "127.0.0.1", "--port", "8000"]
    
    # Run the server
    logger.info(f"Running command: {' '.join(command)}")
    print(f"Starting MCP server with command: {' '.join(command)}")
    
    try:
        process = subprocess.Popen(command)
        
        # Give the server a moment to start
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is None:
            logger.info("MCP server started successfully")
            print("MCP server started successfully!")
            print("The server is now running in the background")
            print("You can now start your trading bot to connect to the MCP server")
            return True
        else:
            logger.error(f"MCP server failed to start. Return code: {process.returncode}")
            print(f"MCP server failed to start. Return code: {process.returncode}")
            return False
    
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")
        print(f"Error starting MCP server: {e}")
        return False

if __name__ == "__main__":
    main()
