#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Direct MetaTrader 5 connection test without MCP server
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
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
    print("=== Direct MetaTrader 5 Connection Test ===")
    
    # Get MT5 credentials from environment variables
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"MT5 Account: {account}")
    print(f"MT5 Server: {server}")
    
    # Step 1: Initialize MT5
    print("\nInitializing MT5...")
    if not mt5.initialize():
        print(f"Failed to initialize MT5: {mt5.last_error()}")
        print("Make sure your MetaTrader 5 terminal is running")
        return False
    
    print("MT5 initialized successfully!")
    
    # Step 2: Login to MT5 account
    print("\nLogging in to MT5 account...")
    login_result = mt5.login(account, password, server)
    
    if not login_result:
        print(f"Failed to login: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print("Login successful!")
    
    # Step 3: Get account information
    account_info = mt5.account_info()
    if account_info:
        print("\nAccount Information:")
        print(f"  Login: {account_info.login}")
        print(f"  Server: {account_info.server}")
        print(f"  Balance: {account_info.balance}")
        print(f"  Equity: {account_info.equity}")
        print(f"  Margin: {account_info.margin}")
        print(f"  Free Margin: {account_info.margin_free}")
        print(f"  Currency: {account_info.currency}")
    
    # Step 4: Get available symbols
    symbols = mt5.symbols_get()
    if symbols:
        print(f"\nFound {len(symbols)} available symbols")
        print("First 5 symbols:")
        for i in range(min(5, len(symbols))):
            print(f"  {symbols[i].name}")
    
    # Step 5: Get symbol info for a popular forex pair
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        print(f"\n{symbol} Information:")
        print(f"  Bid: {symbol_info.bid}")
        print(f"  Ask: {symbol_info.ask}")
        print(f"  Spread: {symbol_info.spread}")
        print(f"  Trade mode: {symbol_info.trade_mode}")
        print(f"  Volume min: {symbol_info.volume_min}")
    
    # Step 6: Get open positions
    positions = mt5.positions_get()
    if positions:
        print(f"\nFound {len(positions)} open positions:")
        for pos in positions:
            print(f"  Symbol: {pos.symbol}, Type: {'Buy' if pos.type == 0 else 'Sell'}, Volume: {pos.volume}, Profit: {pos.profit}")
    else:
        print("\nNo open positions found")
    
    # Shutdown
    mt5.shutdown()
    
    print("\n✓ Direct MT5 connection test PASSED!")
    return True

if __name__ == "__main__":
    test_direct_mt5_connection()
