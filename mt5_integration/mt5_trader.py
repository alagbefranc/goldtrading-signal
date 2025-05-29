#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MetaTrader 5 Trader for the Forex Trading Bot
This module provides trading functionality using direct connection to MetaTrader 5
"""

import os
import time
import logging
import datetime
from typing import Dict, Optional, Tuple, Union
import MetaTrader5 as mt5
from .direct_mt5_connector import DirectMT5Connector

logger = logging.getLogger(__name__)

# Store a single instance of the MT5 connector
_mt5_connector = None

def get_mt5_connector():
    """
    Get the MT5 connector instance
    
    Returns:
        DirectMT5Connector: MT5 connector instance
    """
    global _mt5_connector
    if _mt5_connector is None:
        _mt5_connector = DirectMT5Connector()
    return _mt5_connector

class MT5Trader:
    """
    Class for executing trades in MetaTrader 5 based on ICT/SMC signals
    """
    
    def __init__(self, account=None, password=None, server=None, auto_trade=False, server_url=None):
        """
        Initialize the MT5 trader
        
        Args:
            account (int): MT5 account number
            password (str): MT5 account password
            server (str): MT5 server name
            auto_trade (bool): Whether to automatically execute trades
            server_url (str): URL of the MCP server (if using MCP server connection)
        """
        self.account = account
        self.password = password
        self.server = server
        self.server_url = server_url
        self.auto_trade = auto_trade
        
        # Get MT5 connector
        self.mt5_connector = get_mt5_connector()
        self.is_connected = False
        
        # Initialize server manager
        try:
            from .mcp_server_manager import MCP_Server_Manager
            self.server_manager = MCP_Server_Manager(server_url=self.server_url)
        except Exception as e:
            logger.warning(f"Could not initialize MCP server manager: {e}")
            self.server_manager = None
            
        # Try to initialize MT5
        self._initialize()
        
    def _initialize(self):
        """
        Initialize connection to MT5 - tries direct connection first, then MCP server
        """
        try:
            # Try direct connection first
            logger.info("Attempting direct connection to MT5 terminal...")
            if self.mt5_connector.initialize():
                logger.info("Direct MT5 connection initialized successfully")
                self.is_connected = True
                # Try to login if credentials are provided
                if self.account and self.password and self.server:
                    try:
                        if self.mt5_connector.login(int(self.account), self.password, self.server):
                            logger.info(f"Logged in to MT5 account {self.account}")
                            return True
                    except Exception as login_error:
                        logger.error(f"Error logging in to MT5 account: {login_error}")
            else:
                logger.warning("Could not initialize direct MT5 connection")
        except Exception as e:
            logger.error(f"Error in direct connection: {e}")
            
        # Fall back to MCP server if direct connection failed
        if not self.is_connected and self.server_manager:
            try:
                logger.info("Attempting connection via MCP server...")
                if self.server_manager.is_server_running():
                    self.is_connected = True
                    logger.info("Connected to MT5 via MCP server")
                    return True
            except Exception as e:
                logger.error(f"Error connecting via MCP server: {e}")
                
        return self.is_connected
        
    def start_server(self) -> bool:
        """
        Start the MT5 MCP Server
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if server manager exists
        if not hasattr(self, 'server_manager') or self.server_manager is None:
            logger.error("MCP Server manager is not available")
            return False
            
        # Start the server
        return self.server_manager.start_server()
    
    def stop_server(self) -> bool:
        """
        Stop the MT5 MCP Server
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.server_manager.stop_server()
    
    def connect(self) -> bool:
        """
        Connect to the MetaTrader 5 terminal
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.account or not self.password or not self.server:
            logger.error("MetaTrader 5 credentials not provided")
            return False
        
        # First try to connect directly to MT5
        try:
            import MetaTrader5 as mt5
            from .direct_mt5_connector import DirectMT5Connector
            
            logger.info("Attempting direct connection to MT5 terminal...")
            direct_connector = DirectMT5Connector()
            
            # Initialize MT5 directly
            if direct_connector.initialize():
                logger.info("MT5 initialized successfully through direct connection")
                
                # Login if account credentials provided
                if self.account and self.password and self.server:
                    logger.info(f"Logging in to MT5 account {self.account} on server {self.server}...")
                    if direct_connector.login(self.account, self.password, self.server):
                        logger.info("Logged in to MT5 account successfully")
                        # Use the direct connector instead
                        self.mt5_connector = direct_connector
                        self.is_connected = True
                        return True
                    else:
                        logger.error("Failed to login to MT5 account through direct connection")
                else:
                    # Just initialization without login
                    self.mt5_connector = direct_connector
                    self.is_connected = True
                    return True
            else:
                logger.error("Failed to initialize MT5 through direct connection")
        except Exception as e:
            logger.error(f"Error using direct MT5 connection: {e}")
            
        # Fallback to MCP Server if direct connection failed
        try:
            # Check if MCP Server is running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 8000))
            sock.close()
            self.is_server_running = (result == 0)
            
            if self.is_server_running:
                # Initialize MT5 through MCP Server
                logger.info("Initializing MT5 through MCP Server...")
                if self.mt5_connector.initialize():
                    logger.info("MT5 initialized successfully through MCP Server")
                    
                    # Login if account credentials provided
                    if self.account and self.password and self.server:
                        logger.info(f"Logging in to MT5 account {self.account} on server {self.server}...")
                        if self.mt5_connector.login(self.account, self.password, self.server):
                            logger.info("Logged in to MT5 account successfully through MCP Server")
                            self.is_connected = True
                            return True
                        else:
                            logger.error("Failed to login to MT5 account through MCP Server")
                    else:
                        # Just initialization without login
                        self.is_connected = True
                        return True
                else:
                    logger.error("Failed to initialize MT5 through MCP Server")
            else:
                logger.warning("MCP Server not running. Cannot initialize through MCP Server.")
        except Exception as e:
            logger.error(f"Error using MCP Server: {e}")
            
        return False
            
    def disconnect(self) -> bool:
        """
        Disconnect from the MetaTrader 5 terminal
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_connected:
                return True
            
            if self.mt5_connector.shutdown():
                self.is_connected = False
                logger.info("Disconnected from MetaTrader 5")
                return True
            else:
                logger.error("Failed to disconnect from MetaTrader 5")
                return False
        except Exception as e:
            logger.error(f"Error disconnecting from MetaTrader 5: {e}")
            return False
    
    def execute_trade(self, signal: Dict) -> Dict:
        """
        Execute a trade based on a signal
        
        Args:
            signal (Dict): Signal with trading parameters
            
        Returns:
            Dict: Trade result
        """
        if not self.is_connected:
            logger.error("Not connected to MetaTrader 5")
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        if not self.auto_trade:
            logger.info("Auto-trade is disabled. Signal not executed.")
            return {"success": False, "error": "Auto-trade is disabled"}
        
        # Extract signal parameters
        symbol = signal.get("symbol")
        signal_type = signal.get("type")
        entry_price = signal.get("entry_price")
        stop_loss = signal.get("stop_loss")
        take_profit = signal.get("take_profit")
        volume = signal.get("volume", 0.01)  # Default to 0.01 lots if not specified
        
        if not symbol or not signal_type or not entry_price or not stop_loss or not take_profit:
            return {"success": False, "error": "Missing required parameters in signal"}
        
        # Execute the trade
        order_type = "BUY" if signal_type.upper() == "BUY" else "SELL"
        
        # Get correct order type value
        import MetaTrader5 as mt5
        mt5_order_type = mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL
        
        # Make sure the symbol is enabled for trading
        try:
            # Try to select the symbol for trading
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"Symbol {symbol} not visible in Market Watch, attempting to add it")
                if not mt5.symbol_select(symbol, True):
                    return {"success": False, "error": f"Cannot select {symbol} for trading. Please add it to Market Watch in MT5."}
        except Exception as e:
            logger.error(f"Error selecting symbol {symbol}: {e}")
            return {"success": False, "error": f"Error selecting {symbol}: {e}"}
            
        # Call place_market_order with the correct parameter names (sl and tp instead of stop_loss and take_profit)
        try:
            result = self.mt5_connector.place_market_order(
                symbol=symbol,
                order_type=mt5_order_type,
                volume=volume,
                sl=stop_loss,
                tp=take_profit,
                comment=f"ICT/SMC Signal {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if "error" in result:
                logger.error(f"Failed to execute trade: {result['error']}")
                return {"success": False, "error": result["error"]}
            
            logger.info(f"Trade executed successfully: {order_type} {symbol} {volume} lots")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_info(self) -> Dict:
        """
        Get the account information
        
        Returns:
            Dict: Account information
        """
        if not self.is_connected:
            logger.error("Not connected to MetaTrader 5")
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            # Try to get account info
            import MetaTrader5 as mt5
            account_info = mt5.account_info()
            if account_info is None:
                return {"success": False, "error": "Failed to get account info"}
            
            # Convert named tuple to dict
            info = {
                "login": account_info.login,
                "server": account_info.server,
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "profit": account_info.profit,
                "leverage": account_info.leverage
            }
            
            return {"success": True, "account_info": info}
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {"success": False, "error": str(e)}
    
    def get_positions(self) -> Dict:
        """
        Get the open positions
        
        Returns:
            Dict: Positions result
        """
        if not self.is_connected:
            logger.error("Not connected to MetaTrader 5")
            return {"error": "Not connected to MetaTrader 5"}
        
        try:
            positions = self.mt5_connector.positions_get()
            return {"success": True, "positions": positions}
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return {"success": False, "error": str(e)}
        
    def place_test_order(self, symbol: str = "EURUSD", volume: float = 0.01) -> Dict:
        """
        Place a test order to verify connectivity
        
        Args:
            symbol (str): Symbol to trade
            volume (float): Volume in lots
            
        Returns:
            Dict: Order result
        """
        if not self.is_connected:
            logger.error("Not connected to MetaTrader 5")
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            # Get current price
            tick = self.mt5_connector.get_symbol_info_tick(symbol)
            if not tick:
                return {"success": False, "error": f"Failed to get price for {symbol}"}
            
            ask = tick.get("ask", 0)
            bid = tick.get("bid", 0)
            
            # Calculate stop loss and take profit (10 and 20 pips)
            if symbol == "XAUUSD":  # Gold
                pip_size = 0.1
            else:  # Standard forex pairs
                pip_size = 0.0001
                
            stop_loss = bid - (10 * pip_size) if symbol != "XAUUSD" else bid - 1  # 10 pips or $1
            take_profit = ask + (20 * pip_size) if symbol != "XAUUSD" else ask + 2  # 20 pips or $2
            
            # Place a buy order
            result = self.mt5_connector.place_market_order(
                symbol=symbol,
                order_type="BUY",
                volume=volume,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment="Test Order"
            )
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error placing test order: {e}")
            return {"success": False, "error": str(e)}
