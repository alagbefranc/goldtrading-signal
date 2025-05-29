#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple MetaTrader 5 MCP Server
"""

import os
import sys
import logging
import MetaTrader5 as mt5
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("simple-mt5-mcp")

def main():
    """Run a simple MCP server for MetaTrader 5"""
    print("Starting Simple MetaTrader 5 MCP Server...")
    
    # Initialize MT5
    print("Initializing MetaTrader 5...")
    if not mt5.initialize():
        print(f"Failed to initialize MetaTrader 5: {mt5.last_error()}")
        return False
    
    print("MetaTrader 5 initialized successfully")
    
    # Create FastMCP instance (without deprecated parameters)
    mcp = FastMCP("Simple MetaTrader 5 MCP Server")
    
    # Add resources
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
    
    @mcp.resource
    def positions_get(symbol=None):
        """Get open positions"""
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()
            
        if positions is not None:
            result = []
            for pos in positions:
                pos_dict = {}
                for prop in dir(pos):
                    if not prop.startswith('_'):
                        try:
                            pos_dict[prop] = getattr(pos, prop)
                        except:
                            pass
                result.append(pos_dict)
            return {"success": True, "positions": result}
        else:
            return {"success": False, "message": f"Failed to get positions: {mt5.last_error()}"}
    
    @mcp.resource
    def orders_get(symbol=None):
        """Get active orders"""
        if symbol:
            orders = mt5.orders_get(symbol=symbol)
        else:
            orders = mt5.orders_get()
            
        if orders is not None:
            result = []
            for order in orders:
                order_dict = {}
                for prop in dir(order):
                    if not prop.startswith('_'):
                        try:
                            order_dict[prop] = getattr(order, prop)
                        except:
                            pass
                result.append(order_dict)
            return {"success": True, "orders": result}
        else:
            return {"success": False, "message": f"Failed to get orders: {mt5.last_error()}"}
    
    # Run the server
    print("Starting FastMCP server on http://127.0.0.1:8000...")
    try:
        # Use the proper run() syntax as per deprecation warning
        mcp.run(host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Error starting FastMCP server: {e}")
        mt5.shutdown()
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Ensure MT5 is shut down properly
        print("Shutting down MetaTrader 5...")
        mt5.shutdown()
