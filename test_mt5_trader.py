#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for MT5Trader with fallback mechanism
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
from mt5_integration.mt5_trader import MT5Trader

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_mt5_trader():
    """Test MT5Trader with fallback mechanism"""
    print("=== MT5Trader Test (with Fallback Mechanism) ===")
    
    # Get MT5 credentials from environment variables
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"MT5 Account: {account}")
    print(f"MT5 Server: {server}")
    
    # Create MT5Trader instance
    print("\nCreating MT5Trader instance...")
    trader = MT5Trader(account=account, password=password, server=server)
    
    # Connect to MT5
    print("\nConnecting to MT5...")
    connected = trader.connect()
    print(f"Connection successful: {connected}")
    
    if not connected:
        print("Failed to connect to MT5")
        return False
    
    # Get account information
    print("\nGetting account information...")
    account_info = trader.get_account_info()
    
    if account_info:
        print("Account information:")
        for key, value in account_info.items():
            print(f"  {key}: {value}")
    
    # Get symbols
    print("\nGetting available symbols...")
    symbols = trader.get_symbols()
    
    if symbols:
        print(f"Found {len(symbols)} symbols")
        print("First 5 symbols:")
        for i in range(min(5, len(symbols))):
            print(f"  {symbols[i]}")
    
    # Get symbol info for EURUSD
    print("\nGetting symbol info for EURUSD...")
    symbol_info = trader.get_symbol_info("EURUSD")
    
    if symbol_info:
        print("EURUSD symbol info:")
        important_fields = ['name', 'bid', 'ask', 'point', 'volume_min']
        for field in important_fields:
            if field in symbol_info:
                print(f"  {field}: {symbol_info[field]}")
    
    # Get open positions
    print("\nGetting open positions...")
    positions = trader.get_positions()
    
    if positions:
        print(f"Found {len(positions)} open positions:")
        for pos in positions:
            print(f"  Symbol: {pos['symbol']}, Type: {'Buy' if pos['type'] == 0 else 'Sell'}, Volume: {pos['volume']}, Profit: {pos['profit']}")
    else:
        print("No open positions found")
    
    # Disconnect from MT5
    print("\nDisconnecting from MT5...")
    disconnected = trader.disconnect()
    print(f"Disconnection successful: {disconnected}")
    
    print("\n✓ MT5Trader test completed!")
    return True

if __name__ == "__main__":
    test_mt5_trader()
