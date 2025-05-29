#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for MT5 connector with MCP Server
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

def test_mt5_connector():
    """Test MT5 connector with MCP Server"""
    print("=== MT5 Connector with MCP Server Test ===")
    
    # Create MT5 connector
    mt5_connector = MT5Connector(server_url="http://127.0.0.1:8000")
    
    # Step 1: Initialize MT5
    print("\nStep 1: Initializing MT5...")
    initialized = mt5_connector.initialize()
    print(f"MT5 initialized: {initialized}")
    
    if not initialized:
        print("Failed to initialize MT5")
        return False
    
    # Step 2: Login to MT5 account
    print("\nStep 2: Logging in to MT5 account...")
    
    # Get MT5 credentials from environment variables
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"MT5 Account: {account}")
    print(f"MT5 Server: {server}")
    
    logged_in = mt5_connector.login(account, password, server)
    print(f"MT5 logged in: {logged_in}")
    
    if not logged_in:
        print("Failed to login to MT5 account")
        return False
    
    # Step 3: Get available symbols
    print("\nStep 3: Getting available symbols...")
    symbols = mt5_connector.get_symbols()
    
    if symbols:
        print(f"Found {len(symbols)} symbols")
        print("First 5 symbols:")
        for i in range(min(5, len(symbols))):
            print(f"  {symbols[i]}")
    else:
        print("Failed to get symbols")
    
    # Step 4: Get symbol info for EURUSD
    print("\nStep 4: Getting symbol info for EURUSD...")
    symbol_info = mt5_connector.get_symbol_info("EURUSD")
    
    if symbol_info:
        print("EURUSD symbol info:")
        important_fields = ['name', 'bid', 'ask', 'point', 'digits', 'spread']
        for field in important_fields:
            if field in symbol_info:
                print(f"  {field}: {symbol_info[field]}")
    else:
        print("Failed to get symbol info for EURUSD")
    
    # Step 5: Get latest tick for EURUSD
    print("\nStep 5: Getting latest tick for EURUSD...")
    tick = mt5_connector.get_symbol_info_tick("EURUSD")
    
    if tick:
        print("EURUSD latest tick:")
        for key, value in tick.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to get latest tick for EURUSD")
    
    # Step 6: Get open positions
    print("\nStep 6: Getting open positions...")
    positions = mt5_connector.positions_get()
    
    if positions is not None:
        if len(positions) > 0:
            print(f"Found {len(positions)} open positions:")
            for i, pos in enumerate(positions):
                print(f"Position {i+1}:")
                for key, value in pos.items():
                    print(f"  {key}: {value}")
        else:
            print("No open positions found")
    else:
        print("Failed to get open positions")
    
    # Step 7: Shutdown
    print("\nStep 7: Shutting down MT5 connection...")
    shutdown = mt5_connector.shutdown()
    print(f"MT5 shutdown: {shutdown}")
    
    print("\n✓ MT5 Connector test completed!")
    return True

if __name__ == "__main__":
    test_mt5_connector()
