#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for direct MetaTrader 5 connection
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
from mt5_integration.direct_mt5_connector import DirectMT5Connector
import MetaTrader5 as mt5

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_direct_mt5_connection():
    """Test direct connection to MetaTrader 5"""
    print("Testing direct connection to MetaTrader 5...")
    
    # Create MT5 connector
    connector = DirectMT5Connector()
    
    # Initialize MT5
    print("Initializing MT5 terminal...")
    initialized = connector.initialize()
    print(f"MT5 terminal initialized: {initialized}")
    
    if not initialized:
        print("Failed to initialize MT5 terminal. Make sure MT5 is installed and running.")
        return False
    
    # Login to MT5 account
    print("\nLogging in to MT5 account...")
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"Account: {account}")
    print(f"Server: {server}")
    
    # Convert account to integer since MT5 API expects login as an integer
    login_result = connector.login(int(account), password, server)
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
        # Print just a few key fields to keep output manageable
        important_fields = ['name', 'bid', 'ask', 'point', 'trade_mode', 'volume_min']
        for key in important_fields:
            if key in gold_info:
                print(f"  {key}: {gold_info[key]}")
    
    # Get latest tick for XAUUSD
    print("\nGetting latest tick for XAUUSD...")
    gold_tick = connector.get_symbol_info_tick("XAUUSD")
    if gold_tick:
        print("Latest gold tick:")
        for key, value in gold_tick.items():
            print(f"  {key}: {value}")
    
    # Get open positions
    print("\nGetting open positions...")
    positions = connector.positions_get()
    if positions:
        print(f"Found {len(positions)} open positions:")
        for pos in positions:
            print(f"  Symbol: {pos['symbol']}, Type: {'Buy' if pos['type'] == 0 else 'Sell'}, Volume: {pos['volume']}, Profit: {pos['profit']}")
    else:
        print("No open positions found.")
    
    # Shutdown MT5
    print("\nShutting down MT5 connection...")
    connector.shutdown()
    
    print("\nConnection test completed!")
    return True

if __name__ == "__main__":
    test_direct_mt5_connection()
