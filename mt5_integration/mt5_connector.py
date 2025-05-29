#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MetaTrader 5 Connector for the Forex Trading Bot
This module provides integration with the MetaTrader 5 platform through the MCP Server.
Implements all features from the MetaTrader 5 MCP Server guide.
"""

import os
import logging
import json
import requests
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum, auto

logger = logging.getLogger(__name__)

# Define constants for MT5 order types and actions
class MT5OrderType(Enum):
    BUY = auto()            # Buy order
    SELL = auto()           # Sell order
    BUY_LIMIT = auto()      # Buy limit order
    SELL_LIMIT = auto()     # Sell limit order
    BUY_STOP = auto()       # Buy stop order
    SELL_STOP = auto()      # Sell stop order
    BUY_STOP_LIMIT = auto() # Buy stop limit order
    SELL_STOP_LIMIT = auto()# Sell stop limit order

class MT5TimeFrame(Enum):
    M1 = 1          # 1 minute
    M2 = 2          # 2 minutes
    M3 = 3          # 3 minutes
    M4 = 4          # 4 minutes
    M5 = 5          # 5 minutes
    M6 = 6          # 6 minutes
    M10 = 10        # 10 minutes
    M12 = 12        # 12 minutes
    M15 = 15        # 15 minutes
    M20 = 20        # 20 minutes
    M30 = 30        # 30 minutes
    H1 = 16385      # 1 hour
    H2 = 16386      # 2 hours
    H3 = 16387      # 3 hours
    H4 = 16388      # 4 hours
    H6 = 16390      # 6 hours
    H8 = 16392      # 8 hours
    H12 = 16396     # 12 hours
    D1 = 16408      # 1 day
    W1 = 32769      # 1 week
    MN1 = 49153     # 1 month

class OrderRequest:
    """
    Order request class for MT5 trading operations
    """
    def __init__(self, action, symbol, volume, type, price=None, sl=None, tp=None, deviation=None, 
                 magic=None, comment=None, type_time=None, type_filling=None, expiration=None):
        self.action = action
        self.symbol = symbol
        self.volume = volume
        self.type = type
        self.price = price
        self.sl = sl  # Stop Loss
        self.tp = tp  # Take Profit
        self.deviation = deviation
        self.magic = magic
        self.comment = comment
        self.type_time = type_time
        self.type_filling = type_filling
        self.expiration = expiration
        
    def to_dict(self):
        """
        Convert to dictionary for JSON serialization
        """
        data = {
            "action": self.action,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": self.type
        }
        
        # Add optional parameters if set
        if self.price is not None:
            data["price"] = self.price
        if self.sl is not None:
            data["sl"] = self.sl
        if self.tp is not None:
            data["tp"] = self.tp
        if self.deviation is not None:
            data["deviation"] = self.deviation
        if self.magic is not None:
            data["magic"] = self.magic
        if self.comment is not None:
            data["comment"] = self.comment
        if self.type_time is not None:
            data["type_time"] = self.type_time
        if self.type_filling is not None:
            data["type_filling"] = self.type_filling
        if self.expiration is not None:
            data["expiration"] = self.expiration
            
        return data

class MT5Connector:
    """
    Connector class for interacting with MetaTrader 5 through the MCP Server
    Implements all features from the MT5 MCP Server API reference
    """
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        """
        Initialize the MT5 connector
        
        Args:
            server_url (str): URL of the MT5 MCP Server
        """
        self.server_url = server_url
        self.initialized = False
        self.logged_in = False
        self.account_info = None
        self.available_symbols = []
    
    def _send_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """
        Send a request to the MT5 MCP Server
        
        Args:
            endpoint (str): API endpoint
            method (str): HTTP method (GET, POST)
            data (Dict): Data to send (for POST requests)
            
        Returns:
            Dict: Response from the server
        """
        url = f"{self.server_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with MT5 MCP Server: {e}")
            return {"error": str(e)}
    
    def initialize(self) -> bool:
        """
        Initialize the MT5 terminal
        
        Returns:
            bool: True if successful, False otherwise
        """
        result = self._send_request("initialize", method="POST")
        if "error" not in result:
            self.initialized = True
            logger.info("MT5 terminal initialized successfully")
            return True
        logger.error(f"Failed to initialize MT5 terminal: {result.get('error')}")
        return False
    
    def login(self, account: int, password: str, server: str) -> bool:
        """
        Log in to a trading account
        
        Args:
            account (int): Account number
            password (str): Password
            server (str): Server name
            
        Returns:
            bool: True if successful, False otherwise
        """
        data = {"account": account, "password": password, "server": server}
        result = self._send_request("login", method="POST", data=data)
        
        if "error" not in result:
            self.logged_in = True
            self.account_info = result.get("account_info")
            logger.info(f"Logged in to MT5 account {account} on server {server}")
            return True
        logger.error(f"Failed to log in to MT5 account: {result.get('error')}")
        return False
    
    def shutdown(self) -> bool:
        """
        Close the connection to the MT5 terminal
        
        Returns:
            bool: True if successful, False otherwise
        """
        result = self._send_request("shutdown", method="POST")
        if "error" not in result:
            self.initialized = False
            self.logged_in = False
            self.account_info = None
            logger.info("MT5 terminal connection closed")
            return True
        logger.error(f"Failed to close MT5 terminal connection: {result.get('error')}")
        return False
        
    # Market Data Functions
    def get_symbols(self) -> List[str]:
        """
        Get all available symbols
        
        Returns:
            List[str]: List of available symbols
        """
        result = self._send_request("get_symbols")
        if "error" not in result:
            self.available_symbols = result.get("symbols", [])
            return self.available_symbols
        logger.error(f"Failed to get symbols: {result.get('error')}")
        return []
    
    def get_symbols_by_group(self, group: str) -> List[str]:
        """
        Get symbols by group
        
        Args:
            group (str): Symbol group (e.g., 'Forex', 'Crypto', etc.)
            
        Returns:
            List[str]: List of symbols in the specified group
        """
        data = {"group": group}
        result = self._send_request("get_symbols_by_group", method="POST", data=data)
        if "error" not in result:
            return result.get("symbols", [])
        logger.error(f"Failed to get symbols by group: {result.get('error')}")
        return []
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get information about a specific symbol
        
        Args:
            symbol (str): Symbol name
            
        Returns:
            Dict: Symbol information
        """
        data = {"symbol": symbol}
        result = self._send_request("get_symbol_info", method="POST", data=data)
        if "error" not in result:
            return result.get("info", {})
        logger.error(f"Failed to get symbol info: {result.get('error')}")
        return {}
    
    def get_symbol_info_tick(self, symbol: str) -> Dict:
        """
        Get the latest tick for a symbol
        
        Args:
            symbol (str): Symbol name
            
        Returns:
            Dict: Latest tick data
        """
        data = {"symbol": symbol}
        result = self._send_request("get_symbol_info_tick", method="POST", data=data)
        if "error" not in result:
            return result.get("tick", {})
        logger.error(f"Failed to get symbol tick: {result.get('error')}")
        return {}
    
    def copy_rates_from_pos(self, symbol: str, timeframe: int, start_pos: int, count: int) -> pd.DataFrame:
        """
        Get bars from a specific position
        
        Args:
            symbol (str): Symbol name
            timeframe (int): Timeframe (use MT5TimeFrame enum)
            start_pos (int): Starting position
            count (int): Number of bars to get
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_pos": start_pos,
            "count": count
        }
        result = self._send_request("copy_rates_from_pos", method="POST", data=data)
        if "error" not in result:
            rates = result.get("rates", [])
            if rates:
                return pd.DataFrame(rates)
            return pd.DataFrame()
        logger.error(f"Failed to get rates from position: {result.get('error')}")
        return pd.DataFrame()
    
    def copy_rates_from_date(self, symbol: str, timeframe: int, date_from, count: int) -> pd.DataFrame:
        """
        Get bars from a specific date
        
        Args:
            symbol (str): Symbol name
            timeframe (int): Timeframe (use MT5TimeFrame enum)
            date_from: Starting date (datetime object or timestamp)
            count (int): Number of bars to get
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        # Convert datetime to timestamp if needed
        if isinstance(date_from, datetime.datetime):
            date_from = int(date_from.timestamp())
            
        data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "date_from": date_from,
            "count": count
        }
        result = self._send_request("copy_rates_from_date", method="POST", data=data)
        if "error" not in result:
            rates = result.get("rates", [])
            if rates:
                return pd.DataFrame(rates)
            return pd.DataFrame()
        logger.error(f"Failed to get rates from date: {result.get('error')}")
        return pd.DataFrame()
    
    def copy_rates_range(self, symbol: str, timeframe: int, date_from, date_to) -> pd.DataFrame:
        """
        Get bars within a date range
        
        Args:
            symbol (str): Symbol name
            timeframe (int): Timeframe (use MT5TimeFrame enum)
            date_from: Starting date (datetime object or timestamp)
            date_to: Ending date (datetime object or timestamp)
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        # Convert datetime to timestamp if needed
        if isinstance(date_from, datetime.datetime):
            date_from = int(date_from.timestamp())
        if isinstance(date_to, datetime.datetime):
            date_to = int(date_to.timestamp())
            
        data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "date_from": date_from,
            "date_to": date_to
        }
        result = self._send_request("copy_rates_range", method="POST", data=data)
        if "error" not in result:
            rates = result.get("rates", [])
            if rates:
                return pd.DataFrame(rates)
            return pd.DataFrame()
        logger.error(f"Failed to get rates range: {result.get('error')}")
        return pd.DataFrame()
    
    def copy_ticks_from_pos(self, symbol: str, start_pos: int, count: int) -> pd.DataFrame:
        """
        Get ticks from a specific position
        
        Args:
            symbol (str): Symbol name
            start_pos (int): Starting position
            count (int): Number of ticks to get
            
        Returns:
            pd.DataFrame: DataFrame with tick data
        """
        data = {
            "symbol": symbol,
            "start_pos": start_pos,
            "count": count
        }
        result = self._send_request("copy_ticks_from_pos", method="POST", data=data)
        if "error" not in result:
            ticks = result.get("ticks", [])
            if ticks:
                return pd.DataFrame(ticks)
            return pd.DataFrame()
        logger.error(f"Failed to get ticks from position: {result.get('error')}")
        return pd.DataFrame()
    
    def copy_ticks_from_date(self, symbol: str, date_from, count: int) -> pd.DataFrame:
        """
        Get ticks from a specific date
        
        Args:
            symbol (str): Symbol name
            date_from: Starting date (datetime object or timestamp)
            count (int): Number of ticks to get
            
        Returns:
            pd.DataFrame: DataFrame with tick data
        """
        # Convert datetime to timestamp if needed
        if isinstance(date_from, datetime.datetime):
            date_from = int(date_from.timestamp())
            
        data = {
            "symbol": symbol,
            "date_from": date_from,
            "count": count
        }
        result = self._send_request("copy_ticks_from_date", method="POST", data=data)
        if "error" not in result:
            ticks = result.get("ticks", [])
            if ticks:
                return pd.DataFrame(ticks)
            return pd.DataFrame()
        logger.error(f"Failed to get ticks from date: {result.get('error')}")
        return pd.DataFrame()
    
    def copy_ticks_range(self, symbol: str, date_from, date_to) -> pd.DataFrame:
        """
        Get ticks within a date range
        
        Args:
            symbol (str): Symbol name
            date_from: Starting date (datetime object or timestamp)
            date_to: Ending date (datetime object or timestamp)
            
        Returns:
            pd.DataFrame: DataFrame with tick data
        """
        # Convert datetime to timestamp if needed
        if isinstance(date_from, datetime.datetime):
            date_from = int(date_from.timestamp())
        if isinstance(date_to, datetime.datetime):
            date_to = int(date_to.timestamp())
            
        data = {
            "symbol": symbol,
            "date_from": date_from,
            "date_to": date_to
        }
        result = self._send_request("copy_ticks_range", method="POST", data=data)
        if "error" not in result:
            ticks = result.get("ticks", [])
            if ticks:
                return pd.DataFrame(ticks)
            return pd.DataFrame()
        logger.error(f"Failed to get ticks range: {result.get('error')}")
        return pd.DataFrame()
    
    # Trading Functions
    def order_send(self, request: OrderRequest) -> Dict:
        """
        Send an order to the trade server
        
        Args:
            request (OrderRequest): Order request object
            
        Returns:
            Dict: Order result
        """
        data = request.to_dict() if isinstance(request, OrderRequest) else request
        result = self._send_request("order_send", method="POST", data=data)
        if "error" not in result:
            logger.info(f"Order sent successfully: {result}")
            return result
        logger.error(f"Failed to send order: {result.get('error')}")
        return {"error": result.get("error")}
    
    def order_check(self, request: OrderRequest) -> Dict:
        """
        Check if an order can be placed with the specified parameters
        
        Args:
            request (OrderRequest): Order request object
            
        Returns:
            Dict: Check result
        """
        data = request.to_dict() if isinstance(request, OrderRequest) else request
        result = self._send_request("order_check", method="POST", data=data)
        if "error" not in result:
            return result
        logger.error(f"Order check failed: {result.get('error')}")
        return {"error": result.get("error")}
    
    def positions_get(self, symbol: str = None, group: str = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol (str, optional): Symbol to filter positions
            group (str, optional): Group to filter positions
            
        Returns:
            List[Dict]: Open positions
        """
        data = {}
        if symbol:
            data["symbol"] = symbol
        if group:
            data["group"] = group
            
        result = self._send_request("positions_get", method="POST", data=data if data else None)
        if "error" not in result:
            return result.get("positions", [])
        logger.error(f"Failed to get positions: {result.get('error')}")
        return []
    
    def positions_get_by_ticket(self, ticket: int) -> Dict:
        """
        Get an open position by its ticket
        
        Args:
            ticket (int): Position ticket
            
        Returns:
            Dict: Position information
        """
        data = {"ticket": ticket}
        result = self._send_request("positions_get_by_ticket", method="POST", data=data)
        if "error" not in result:
            return result.get("position", {})
        logger.error(f"Failed to get position by ticket: {result.get('error')}")
        return {}
    
    def orders_get(self, symbol: str = None, group: str = None) -> List[Dict]:
        """
        Get active orders
        
        Args:
            symbol (str, optional): Symbol to filter orders
            group (str, optional): Group to filter orders
            
        Returns:
            List[Dict]: Active orders
        """
        data = {}
        if symbol:
            data["symbol"] = symbol
        if group:
            data["group"] = group
            
        result = self._send_request("orders_get", method="POST", data=data if data else None)
        if "error" not in result:
            return result.get("orders", [])
        logger.error(f"Failed to get orders: {result.get('error')}")
        return []
    
    def orders_get_by_ticket(self, ticket: int) -> Dict:
        """
        Get an active order by its ticket
        
        Args:
            ticket (int): Order ticket
            
        Returns:
            Dict: Order information
        """
        data = {"ticket": ticket}
        result = self._send_request("orders_get_by_ticket", method="POST", data=data)
        if "error" not in result:
            return result.get("order", {})
        logger.error(f"Failed to get order by ticket: {result.get('error')}")
        return {}
    
    def history_orders_get(self, symbol: str = None, group: str = None, ticket: int = None, 
                           position: int = None, from_date = None, to_date = None) -> List[Dict]:
        """
        Get orders from history
        
        Args:
            symbol (str, optional): Symbol to filter orders
            group (str, optional): Group to filter orders
            ticket (int, optional): Order ticket
            position (int, optional): Position ticket
            from_date (optional): Start date (datetime object or timestamp)
            to_date (optional): End date (datetime object or timestamp)
            
        Returns:
            List[Dict]: Historical orders
        """
        # Convert datetime objects to timestamps if needed
        if isinstance(from_date, datetime.datetime):
            from_date = int(from_date.timestamp())
        if isinstance(to_date, datetime.datetime):
            to_date = int(to_date.timestamp())
            
        data = {}
        if symbol:
            data["symbol"] = symbol
        if group:
            data["group"] = group
        if ticket:
            data["ticket"] = ticket
        if position:
            data["position"] = position
        if from_date:
            data["from_date"] = from_date
        if to_date:
            data["to_date"] = to_date
            
        result = self._send_request("history_orders_get", method="POST", data=data if data else None)
        if "error" not in result:
            return result.get("orders", [])
        logger.error(f"Failed to get history orders: {result.get('error')}")
        return []
    
    def history_deals_get(self, symbol: str = None, group: str = None, ticket: int = None, 
                          position: int = None, from_date = None, to_date = None) -> List[Dict]:
        """
        Get deals from history
        
        Args:
            symbol (str, optional): Symbol to filter deals
            group (str, optional): Group to filter deals
            ticket (int, optional): Deal ticket
            position (int, optional): Position ticket
            from_date (optional): Start date (datetime object or timestamp)
            to_date (optional): End date (datetime object or timestamp)
            
        Returns:
            List[Dict]: Historical deals
        """
        # Convert datetime objects to timestamps if needed
        if isinstance(from_date, datetime.datetime):
            from_date = int(from_date.timestamp())
        if isinstance(to_date, datetime.datetime):
            to_date = int(to_date.timestamp())
            
        data = {}
        if symbol:
            data["symbol"] = symbol
        if group:
            data["group"] = group
        if ticket:
            data["ticket"] = ticket
        if position:
            data["position"] = position
        if from_date:
            data["from_date"] = from_date
        if to_date:
            data["to_date"] = to_date
            
        result = self._send_request("history_deals_get", method="POST", data=data if data else None)
        if "error" not in result:
            return result.get("deals", [])
        logger.error(f"Failed to get history deals: {result.get('error')}")
        return []
        
    # Helper method to get all symbols    
    def get_symbols(self) -> List[str]:
        """
        Get all available symbols
        
        Returns:
            List[str]: List of available symbols
        """
        result = self._send_request("get_symbols")
        if "error" not in result:
            return result.get("symbols", [])
        logger.error(f"Failed to get symbols: {result.get('error')}")
        return []
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get information about a specific symbol
        
        Args:
            symbol (str): Symbol name (e.g., "EURUSD", "XAUUSD")
            
        Returns:
            Dict: Symbol information
        """
        result = self._send_request(f"get_symbol_info/{symbol}")
        if "error" not in result:
            return result.get("symbol_info", {})
        logger.error(f"Failed to get symbol info for {symbol}: {result.get('error')}")
        return {}
    
    def get_symbol_info_tick(self, symbol: str) -> Dict:
        """
        Get the latest tick for a symbol
        
        Args:
            symbol (str): Symbol name (e.g., "EURUSD", "XAUUSD")
            
        Returns:
            Dict: Latest tick information
        """
        result = self._send_request(f"get_symbol_info_tick/{symbol}")
        if "error" not in result:
            return result.get("tick", {})
        logger.error(f"Failed to get latest tick for {symbol}: {result.get('error')}")
        return {}
    
    def copy_rates_from_date(self, symbol: str, timeframe: int, date_from: datetime.datetime, count: int) -> pd.DataFrame:
        """
        Get historical price data from a specific date
        
        Args:
            symbol (str): Symbol name (e.g., "EURUSD", "XAUUSD")
            timeframe (int): Timeframe (e.g., 1, 5, 15, 60, 240, 1440)
            date_from (datetime.datetime): Start date and time
            count (int): Number of bars to retrieve
            
        Returns:
            pd.DataFrame: Historical price data
        """
        data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "date_from": date_from.timestamp(),
            "count": count
        }
        result = self._send_request("copy_rates_from_date", method="POST", data=data)
        
        if "error" not in result and "rates" in result:
            rates = result.get("rates", [])
            if rates:
                df = pd.DataFrame(rates)
                # Convert time column to datetime
                if "time" in df.columns:
                    df["time"] = pd.to_datetime(df["time"], unit="s")
                return df
            return pd.DataFrame()
        
        logger.error(f"Failed to get historical data for {symbol}: {result.get('error')}")
        return pd.DataFrame()
    
    def order_send(self, request: Dict) -> Dict:
        """
        Send an order to the trade server
        
        Args:
            request (Dict): Order request
            
        Returns:
            Dict: Order result
        """
        result = self._send_request("order_send", method="POST", data=request)
        if "error" not in result:
            return result
        logger.error(f"Failed to send order: {result.get('error')}")
        return {"error": result.get("error")}
    
    def positions_get(self, symbol: str = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol (str, optional): Symbol name to filter positions
            
        Returns:
            List[Dict]: List of open positions
        """
        endpoint = "positions_get"
        if symbol:
            endpoint = f"{endpoint}/{symbol}"
            
        result = self._send_request(endpoint)
        if "error" not in result:
            return result.get("positions", [])
        logger.error(f"Failed to get positions: {result.get('error')}")
        return []
    
    def orders_get(self, symbol: str = None) -> List[Dict]:
        """
        Get active orders
        
        Args:
            symbol (str, optional): Symbol name to filter orders
            
        Returns:
            List[Dict]: List of active orders
        """
        endpoint = "orders_get"
        if symbol:
            endpoint = f"{endpoint}/{symbol}"
            
        result = self._send_request(endpoint)
        if "error" not in result:
            return result.get("orders", [])
        logger.error(f"Failed to get orders: {result.get('error')}")
        return []
    
    def history_orders_get(self, from_date: datetime.datetime, to_date: datetime.datetime, symbol: str = None) -> List[Dict]:
        """
        Get orders from history
        
        Args:
            from_date (datetime.datetime): Start date and time
            to_date (datetime.datetime): End date and time
            symbol (str, optional): Symbol name to filter orders
            
        Returns:
            List[Dict]: List of historical orders
        """
        data = {
            "from_date": from_date.timestamp(),
            "to_date": to_date.timestamp()
        }
        if symbol:
            data["symbol"] = symbol
            
        result = self._send_request("history_orders_get", method="POST", data=data)
        if "error" not in result:
            return result.get("history_orders", [])
        logger.error(f"Failed to get history orders: {result.get('error')}")
        return []
    
    def history_deals_get(self, from_date: datetime.datetime, to_date: datetime.datetime, symbol: str = None) -> List[Dict]:
        """
        Get deals from history
        
        Args:
            from_date (datetime.datetime): Start date and time
            to_date (datetime.datetime): End date and time
            symbol (str, optional): Symbol name to filter deals
            
        Returns:
            List[Dict]: List of historical deals
        """
        data = {
            "from_date": from_date.timestamp(),
            "to_date": to_date.timestamp()
        }
        if symbol:
            data["symbol"] = symbol
            
        result = self._send_request("history_deals_get", method="POST", data=data)
        if "error" not in result:
            return result.get("history_deals", [])
        logger.error(f"Failed to get history deals: {result.get('error')}")
        return []
        
    def place_market_order(self, symbol: str, order_type: str, volume: float, 
                          stop_loss: float = None, take_profit: float = None, 
                          comment: str = None, magic: int = 0) -> Dict:
        """
        Place a market order
        
        Args:
            symbol (str): Symbol name (e.g., "EURUSD", "XAUUSD")
            order_type (str): "BUY" or "SELL"
            volume (float): Trading volume in lots
            stop_loss (float, optional): Stop Loss price
            take_profit (float, optional): Take Profit price
            comment (str, optional): Order comment
            magic (int, optional): Magic number (Expert Advisor ID)
            
        Returns:
            Dict: Order result
        """
        # Get symbol info and the latest tick
        symbol_info = self.get_symbol_info(symbol)
        tick = self.get_symbol_info_tick(symbol)
        
        if not symbol_info or not tick:
            return {"error": f"Failed to get symbol info or latest tick for {symbol}"}
        
        # Determine the price and action type based on order type
        if order_type.upper() == "BUY":
            price = tick.get("ask", 0)
            action_type = 0  # TRADE_ACTION_DEAL
            order_type_val = 0  # ORDER_TYPE_BUY
        elif order_type.upper() == "SELL":
            price = tick.get("bid", 0)
            action_type = 0  # TRADE_ACTION_DEAL
            order_type_val = 1  # ORDER_TYPE_SELL
        else:
            return {"error": f"Invalid order type: {order_type}. Must be 'BUY' or 'SELL'"}
        
        # Prepare the order request
        request = {
            "action": action_type,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_val,
            "price": price,
            "deviation": 20,  # Maximum price deviation in points
            "magic": magic,
            "comment": comment or f"{order_type} {symbol}",
            "type_time": 1,  # ORDER_TIME_GTC (Good Till Cancelled)
            "type_filling": 2  # ORDER_FILLING_IOC (Immediate Or Cancel)
        }
        
        # Add stop loss if provided
        if stop_loss is not None:
            request["sl"] = stop_loss
            
        # Add take profit if provided
        if take_profit is not None:
            request["tp"] = take_profit
            
        # Send the order
        return self.order_send(request)


# Singleton instance for the connector
_mt5_connector = None

def get_mt5_connector(server_url: str = "http://127.0.0.1:8000") -> MT5Connector:
    """
    Get the MT5 connector instance (singleton)
    
    Args:
        server_url (str): URL of the MT5 MCP Server
        
    Returns:
        MT5Connector: MT5 connector instance
    """
    global _mt5_connector
    if _mt5_connector is None:
        _mt5_connector = MT5Connector(server_url=server_url)
    return _mt5_connector
