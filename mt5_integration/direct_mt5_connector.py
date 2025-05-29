#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Direct MetaTrader 5 Connector for the Forex Trading Bot
This module provides direct integration with the MetaTrader 5 platform using the official Python package.
"""

import os
import logging
import json
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
import MetaTrader5 as mt5

logger = logging.getLogger(__name__)

class DirectMT5Connector:
    """
    Direct connector class for interacting with MetaTrader 5 using the official Python package
    """
    
    def __init__(self):
        """Initialize the MT5 connector"""
        self.initialized = False
        self.logged_in = False
        self.account_info = None
        self.available_symbols = []
    
    def initialize(self) -> bool:
        """
        Initialize the MT5 terminal
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.initialized:
                # Initialize MT5
                initialization = mt5.initialize()
                if initialization:
                    self.initialized = True
                    logger.info("MT5 terminal initialized successfully")
                    return True
                else:
                    logger.error(f"Failed to initialize MT5 terminal: {mt5.last_error()}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error initializing MT5 terminal: {e}")
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
        try:
            if not self.initialized:
                if not self.initialize():
                    return False
            
            # Ensure account is an integer
            if not isinstance(account, int):
                try:
                    account = int(account)
                except ValueError:
                    logger.error("Account number must be an integer")
                    return False
            
            # Login to account - pass parameters correctly as per MT5 API
            login_result = mt5.login(login=account, password=password, server=server)
            if login_result:
                self.logged_in = True
                # Get account info
                self.account_info = mt5.account_info()._asdict() if mt5.account_info() else None
                logger.info(f"Logged in to MT5 account {account} on server {server}")
                return True
            else:
                logger.error(f"Failed to login to MT5 account: {mt5.last_error()}")
                return False
        except Exception as e:
            logger.error(f"Error logging in to MT5 account: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Close the connection to the MT5 terminal
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            mt5.shutdown()
            self.initialized = False
            self.logged_in = False
            self.account_info = None
            logger.info("MT5 terminal connection closed")
            return True
        except Exception as e:
            logger.error(f"Error shutting down MT5 terminal: {e}")
            return False
    
    def get_symbols(self) -> List[str]:
        """
        Get all available symbols
        
        Returns:
            List[str]: List of available symbols
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return []
            
            symbols = mt5.symbols_get()
            if symbols:
                self.available_symbols = [symbol.name for symbol in symbols]
                return self.available_symbols
            else:
                logger.error(f"Failed to get symbols: {mt5.last_error()}")
                return []
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get information about a specific symbol
        
        Args:
            symbol (str): Symbol name
            
        Returns:
            Dict: Symbol information
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return {}
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                return symbol_info._asdict()
            else:
                logger.error(f"Failed to get symbol info: {mt5.last_error()}")
                return {}
        except Exception as e:
            logger.error(f"Error getting symbol info: {e}")
            return {}
    
    def get_symbol_info_tick(self, symbol: str) -> Dict:
        """
        Get the latest tick for a symbol
        
        Args:
            symbol (str): Symbol name
            
        Returns:
            Dict: Latest tick data
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return {}
            
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                return tick._asdict()
            else:
                logger.error(f"Failed to get symbol tick: {mt5.last_error()}")
                return {}
        except Exception as e:
            logger.error(f"Error getting symbol tick: {e}")
            return {}
    
    def copy_rates_from_pos(self, symbol: str, timeframe: int, start_pos: int, count: int) -> pd.DataFrame:
        """
        Get bars from a specific position
        
        Args:
            symbol (str): Symbol name
            timeframe (int): Timeframe (use mt5.TIMEFRAME_*)
            start_pos (int): Starting position
            count (int): Number of bars to get
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return pd.DataFrame()
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
            if rates is not None:
                return pd.DataFrame(rates)
            else:
                logger.error(f"Failed to get rates from position: {mt5.last_error()}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting rates from position: {e}")
            return pd.DataFrame()
    
    def copy_rates_from_date(self, symbol: str, timeframe: int, date_from, count: int) -> pd.DataFrame:
        """
        Get bars from a specific date
        
        Args:
            symbol (str): Symbol name
            timeframe (int): Timeframe (use mt5.TIMEFRAME_*)
            date_from: Starting date (datetime object or timestamp)
            count (int): Number of bars to get
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return pd.DataFrame()
            
            # Convert datetime to datetime object if it's a timestamp
            if isinstance(date_from, int):
                date_from = datetime.datetime.fromtimestamp(date_from)
            
            rates = mt5.copy_rates_from_date(symbol, timeframe, date_from, count)
            if rates is not None:
                return pd.DataFrame(rates)
            else:
                logger.error(f"Failed to get rates from date: {mt5.last_error()}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting rates from date: {e}")
            return pd.DataFrame()
    
    def positions_get(self, symbol: str = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol (str, optional): Symbol to filter positions
            
        Returns:
            List[Dict]: Open positions
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return []
            
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()
            
            if positions:
                return [position._asdict() for position in positions]
            else:
                if mt5.last_error() != (0, "No error"):
                    logger.error(f"Failed to get positions: {mt5.last_error()}")
                return []
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def order_send(self, request: Dict) -> Dict:
        """
        Send an order to the trade server
        
        Args:
            request (Dict): Order request dictionary
            
        Returns:
            Dict: Order result
        """
        try:
            if not self.initialized:
                if not self.initialize():
                    return {"retcode": -1, "comment": "MT5 not initialized"}
            
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Order sent successfully: {result.order}")
                return result._asdict()
            else:
                error_message = f"Order failed with code {result.retcode}" if result else f"Order failed: {mt5.last_error()}"
                logger.error(error_message)
                return {"retcode": result.retcode if result else -1, "comment": error_message}
        except Exception as e:
            logger.error(f"Error sending order: {e}")
            return {"retcode": -1, "comment": str(e)}
    
    def place_market_order(self, symbol: str, order_type: int, volume: float, sl: float = None, tp: float = None, comment: str = None) -> Dict:
        """
        Place a market order
        
        Args:
            symbol (str): Symbol name
            order_type (int): Order type (mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL)
            volume (float): Order volume in lots
            sl (float, optional): Stop Loss price
            tp (float, optional): Take Profit price
            comment (str, optional): Order comment
            
        Returns:
            Dict: Order result
        """
        try:
            logger.info(f"Attempting to place {volume} lots {'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL'} order for {symbol}")
            logger.info(f"Stop Loss: {sl}, Take Profit: {tp}, Comment: {comment}")
            
            if not self.initialized:
                if not self.initialize():
                    logger.error("Cannot place order: MT5 not initialized")
                    return {"retcode": -1, "comment": "MT5 not initialized"}
            
            # Get symbol info for pricing
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Symbol {symbol} not found")
                return {"retcode": -1, "comment": f"Symbol {symbol} not found"}
            
            # Enable symbol for trading if needed
            if not symbol_info.visible or not symbol_info.select:
                logger.info(f"Symbol {symbol} not visible, enabling for trading")
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol {symbol} for trading")
                    return {"retcode": -1, "comment": f"Failed to select symbol {symbol} for trading"}
            
            # Get tick for current price
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error(f"Failed to get tick for {symbol}")
                return {"retcode": -1, "comment": f"Failed to get tick for {symbol}"}
            
            # Set price based on order type
            price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
            logger.info(f"Current price for {symbol}: Ask={tick.ask}, Bid={tick.bid}, Using price={price}")
            
            # Prepare the request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),  # Ensure volume is float
                "type": order_type,
                "price": price,
                "deviation": 20,  # Price deviation in points
                "magic": 12345,   # Magic number (identifier)
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add optional parameters
            if sl is not None:
                request["sl"] = float(sl)  # Ensure stop loss is float
            if tp is not None:
                request["tp"] = float(tp)  # Ensure take profit is float
            if comment is not None:
                request["comment"] = comment
            
            # Log the complete trade request
            logger.info(f"Sending order with request: {request}")
            
            # Send the order
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Order executed successfully! Order ID: {result.order}")
                logger.info(f"Trade details: {symbol} {'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL'} {volume} lots at {price}")
                return result._asdict()
            else:
                # Get detailed error information
                if result:
                    error_code = result.retcode
                    error_message = f"Order failed with code {error_code}"
                    
                    # Translate common error codes
                    if error_code == mt5.TRADE_RETCODE_REQUOTE:
                        error_message = "Requote - price changed, please try again"
                    elif error_code == mt5.TRADE_RETCODE_INVALID_VOLUME:
                        error_message = "Invalid volume - check minimum trade size"
                    elif error_code == mt5.TRADE_RETCODE_INVALID_PRICE:
                        error_message = "Invalid price"
                    elif error_code == mt5.TRADE_RETCODE_INVALID_STOPS:
                        error_message = "Invalid stop loss or take profit levels"
                    elif error_code == mt5.TRADE_RETCODE_TRADE_DISABLED:
                        error_message = "Trading is disabled"
                    elif error_code == mt5.TRADE_RETCODE_MARKET_CLOSED:
                        error_message = "Market is closed"
                    elif error_code == mt5.TRADE_RETCODE_NO_MONEY:
                        error_message = "Not enough money to execute trade"
                    elif error_code == mt5.TRADE_RETCODE_PRICE_CHANGED:
                        error_message = "Price changed, please try again"
                    elif error_code == mt5.TRADE_RETCODE_PRICE_OFF:
                        error_message = "No quotes to process request"
                    elif error_code == mt5.TRADE_RETCODE_INVALID_EXPIRATION:
                        error_message = "Invalid order expiration"
                    elif error_code == mt5.TRADE_RETCODE_ORDER_LOCKED:
                        error_message = "Order is locked and cannot be modified"
                    elif error_code == mt5.TRADE_RETCODE_LIMIT_ORDERS:
                        error_message = "Limit on number of orders reached"
                else:
                    error_code = -1
                    error_message = f"Order failed: {mt5.last_error()}"
                
                logger.error(f"❌ {error_message}")
                return {"retcode": error_code, "comment": error_message}
        except Exception as e:
            logger.error(f"❌ Error sending order: {e}")
            # Include the full exception traceback for better debugging
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"retcode": -1, "comment": str(e)}

# Create a global instance of the connector
direct_mt5_connector = DirectMT5Connector()
