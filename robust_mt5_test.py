#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Robust MT5 connection test with enhanced error handling
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

def test_mt5_connection(max_retries=3):
    """Test connection to MetaTrader 5 with retries"""
    print("=== Robust MetaTrader 5 Connection Test ===")
    
    # Get MT5 credentials from environment variables
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"MT5 Account: {account}")
    print(f"MT5 Server: {server}")
    
    # Attempt to initialize with retries
    for attempt in range(1, max_retries + 1):
        print(f"\nInitialization attempt {attempt}/{max_retries}...")
        
        # First, make sure MT5 is shutdown if previously initialized
        mt5.shutdown()
        time.sleep(1)  # Give it a moment
        
        # Try to initialize
        result = mt5.initialize()
        if result:
            print("✓ MT5 initialized successfully!")
            break
        else:
            error = mt5.last_error()
            print(f"✗ Failed to initialize MT5: {error}")
            
            if attempt < max_retries:
                print(f"Waiting 3 seconds before retry...")
                time.sleep(3)
    
    if not result:
        print("\nFailed to initialize MT5 after multiple attempts.")
        print("Troubleshooting tips:")
        print("1. Make sure MetaTrader 5 terminal is running and logged in")
        print("2. Restart MetaTrader 5 terminal")
        print("3. Check if MT5 terminal has permission issues")
        return False
    
    # Try to login
    print("\nLogging in to MT5 account...")
    login_result = mt5.login(account, password, server)
    
    if not login_result:
        error = mt5.last_error()
        print(f"✗ Failed to login: {error}")
        mt5.shutdown()
        return False
    
    print("✓ Login successful!")
    
    # Get account information
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
    
    # Get available symbols
    symbols = mt5.symbols_get()
    if symbols:
        print(f"\nFound {len(symbols)} available symbols")
        print("First 5 symbols:")
        for i in range(min(5, len(symbols))):
            print(f"  {symbols[i].name}")
    
    # Get symbol info for a popular forex pair
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        print(f"\n{symbol} Information:")
        print(f"  Bid: {symbol_info.bid}")
        print(f"  Ask: {symbol_info.ask}")
        print(f"  Spread: {symbol_info.spread}")
        print(f"  Trade mode: {symbol_info.trade_mode}")
        print(f"  Volume min: {symbol_info.volume_min}")
    
    # Get open positions
    positions = mt5.positions_get()
    if positions:
        print(f"\nFound {len(positions)} open positions:")
        for pos in positions:
            print(f"  Symbol: {pos.symbol}, Type: {'Buy' if pos.type == 0 else 'Sell'}, Volume: {pos.volume}, Profit: {pos.profit}")
    else:
        print("\nNo open positions found")
    
    # Shutdown
    print("\nShutting down MT5 connection...")
    mt5.shutdown()
    
    print("\n✓ Direct MT5 connection test PASSED!")
    return True

if __name__ == "__main__":
    test_mt5_connection()
