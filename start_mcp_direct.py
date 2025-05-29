#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Start MetaTrader 5 MCP Server directly using FastMCP
"""

import os
import sys
import time
import logging
import MetaTrader5 as mt5
import fastmcp
from fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_mcp_server():
    """Start the MetaTrader 5 MCP Server"""
    logger.info("Starting MetaTrader 5 MCP Server directly...")
    
    # Initialize MT5
    logger.info("Initializing MetaTrader 5...")
    if not mt5.initialize():
        logger.error(f"Failed to initialize MetaTrader 5: {mt5.last_error()}")
        return False
    
    # Create FastMCP instance
    logger.info("Creating FastMCP instance...")
    mcp = FastMCP()
    
    # Add resources
    # Market Data Functions
    @mcp.resource
    def initialize():
        """Initialize the MT5 terminal"""
        if mt5.initialize():
            return {"success": True, "message": "MetaTrader 5 initialized successfully"}
        else:
            return {"success": False, "message": f"Failed to initialize MetaTrader 5: {mt5.last_error()}"}
    
    @mcp.resource
    def login(account, password, server):
        """Log in to a trading account"""
        if mt5.login(account, password, server):
            account_info = mt5.account_info()
            if account_info is not None:
                return {
                    "success": True,
                    "message": f"Logged in successfully to account {account_info.login}",
                    "account_info": {
                        "login": account_info.login,
                        "balance": account_info.balance,
                        "equity": account_info.equity,
                        "margin": account_info.margin,
                        "margin_free": account_info.margin_free,
                        "currency": account_info.currency,
                        "server": account_info.server
                    }
                }
            else:
                return {"success": True, "message": "Logged in but couldn't get account info"}
        else:
            return {"success": False, "message": f"Failed to log in: {mt5.last_error()}"}
    
    @mcp.resource
    def shutdown():
        """Close the connection to the MT5 terminal"""
        mt5.shutdown()
        return {"success": True, "message": "MetaTrader 5 connection closed"}
    
    @mcp.resource
    def get_symbols():
        """Get all available symbols"""
        symbols = mt5.symbols_get()
        if symbols is not None:
            return {"success": True, "symbols": [symbol.name for symbol in symbols]}
        else:
            return {"success": False, "message": f"Failed to get symbols: {mt5.last_error()}"}
    
    @mcp.resource
    def get_symbol_info(symbol):
        """Get information about a specific symbol"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is not None:
            info = {}
            for prop in dir(symbol_info):
                if not prop.startswith('_'):
                    try:
                        info[prop] = getattr(symbol_info, prop)
                    except:
                        pass
            return {"success": True, "symbol_info": info}
        else:
            return {"success": False, "message": f"Failed to get symbol info: {mt5.last_error()}"}
    
    @mcp.resource
    def get_symbol_info_tick(symbol):
        """Get the latest tick for a symbol"""
        tick = mt5.symbol_info_tick(symbol)
        if tick is not None:
            info = {}
            for prop in dir(tick):
                if not prop.startswith('_'):
                    try:
                        info[prop] = getattr(tick, prop)
                    except:
                        pass
            return {"success": True, "tick": info}
        else:
            return {"success": False, "message": f"Failed to get symbol tick: {mt5.last_error()}"}
    
    # Run the server
    logger.info("Starting FastMCP server...")
    try:
        mcp.run(host="127.0.0.1", port=8000)
    except Exception as e:
        logger.error(f"Error starting FastMCP server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        print("Starting MetaTrader 5 MCP Server...")
        print("Server will be available at http://127.0.0.1:8000")
        start_mcp_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
