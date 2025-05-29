#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic MetaTrader 5 MCP Server - Minimal implementation
"""

import MetaTrader5 as mt5
from fastmcp import FastMCP
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("basic-mt5-mcp")

def main():
    """Run a basic MCP server for MetaTrader 5"""
    # Initialize MetaTrader 5
    print("Initializing MetaTrader 5...")
    if not mt5.initialize():
        print(f"Failed to initialize MetaTrader 5: {mt5.last_error()}")
        return False
    
    print("MetaTrader 5 initialized successfully")
    
    # Create MCP server
    mcp = FastMCP()
    
    # Define resources
    @mcp.resource
    def initialize():
        """Initialize MT5"""
        return {"success": mt5.initialize()}
    
    @mcp.resource
    def login(account, password, server):
        """Login to MT5"""
        return {"success": mt5.login(account, password, server)}
    
    @mcp.resource
    def get_account_info():
        """Get account info"""
        account_info = mt5.account_info()
        if account_info:
            info = {}
            for prop in dir(account_info):
                if not prop.startswith('_'):
                    try:
                        info[prop] = getattr(account_info, prop)
                    except:
                        pass
            return {"success": True, "account_info": info}
        return {"success": False}
    
    @mcp.resource
    def get_symbols():
        """Get available symbols"""
        symbols = mt5.symbols_get()
        if symbols:
            return {"success": True, "symbols": [s.name for s in symbols]}
        return {"success": False}
    
    # Start the server
    print("Starting MCP server on http://127.0.0.1:8000...")
    try:
        mcp.run(host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        mt5.shutdown()
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    finally:
        print("Shutting down MetaTrader 5...")
        mt5.shutdown()
