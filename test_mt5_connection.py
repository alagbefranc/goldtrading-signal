#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for MetaTrader 5 MCP Server connection
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
from mt5_integration.mt5_connector import MT5Connector

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_mt5_connection():
    """Test connection to MetaTrader 5 MCP Server"""
    print("Testing connection to MetaTrader 5 MCP Server...")
    
    # Create MT5 connector
    connector = MT5Connector(server_url=os.getenv("MT5_SERVER_URL", "http://127.0.0.1:8000"))
    
    # Initialize MT5
    print("Initializing MT5 terminal...")
    initialized = connector.initialize()
    print(f"MT5 terminal initialized: {initialized}")
    
    if not initialized:
        print("Failed to initialize MT5 terminal. Make sure the MCP server is running.")
        return False
    
    # Login to MT5 account
    print("\nLogging in to MT5 account...")
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"Account: {account}")
    print(f"Server: {server}")
    
    login_result = connector.login(account, password, server)
    print(f"Login result: {login_result}")
    
    if not login_result:
        print("Failed to login to MT5 account. Check your credentials.")
        return False
    
    # Get account information
    print("\nAccount information:")
    if connector.account_info:
        for key, value in connector.account_info.items():
            print(f"  {key}: {value}")
    
    # Get available symbols
    print("\nFetching available symbols...")
    symbols = connector.get_symbols()
    print(f"Found {len(symbols)} symbols")
    if symbols:
        print("First 5 symbols:")
        for symbol in symbols[:5]:
            print(f"  {symbol}")
    
    # Get symbol info for XAUUSD (Gold)
    print("\nGetting information for XAUUSD (Gold)...")
    gold_info = connector.get_symbol_info("XAUUSD")
    if gold_info:
        print("Gold information:")
        for key, value in list(gold_info.items())[:10]:  # Show first 10 items
            print(f"  {key}: {value}")
    
    # Get latest tick for XAUUSD
    print("\nGetting latest tick for XAUUSD...")
    gold_tick = connector.get_symbol_info_tick("XAUUSD")
    if gold_tick:
        print("Latest gold tick:")
        for key, value in gold_tick.items():
            print(f"  {key}: {value}")
    
    print("\nConnection test completed!")
    return True

if __name__ == "__main__":
    test_mt5_connection()
