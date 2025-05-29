#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple MT5 connection test - prints each step clearly
"""

import os
import sys
import time
from dotenv import load_dotenv
import MetaTrader5 as mt5

def main():
    """Run a simple MT5 connection test"""
    print("=== Simple MT5 Connection Test ===")
    
    # Load environment variables
    load_dotenv()
    
    # Step 1: Initialize MT5
    print("\nStep 1: Initializing MT5...")
    init_result = mt5.initialize()
    print(f"Initialize result: {init_result}")
    
    if not init_result:
        error = mt5.last_error()
        print(f"Error: {error}")
        return
    
    # Step 2: Login to MT5 account
    print("\nStep 2: Logging in to MT5 account...")
    
    # Get MT5 credentials
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    print(f"Account: {account}")
    print(f"Server: {server}")
    
    # Convert account to integer
    account = int(account)
    
    # Login - properly pass parameters with their names
    login_result = mt5.login(login=account, password=password, server=server)
    print(f"Login result: {login_result}")
    
    if not login_result:
        error = mt5.last_error()
        print(f"Error: {error}")
    else:
        # Step 3: Get account info
        print("\nStep 3: Getting account info...")
        account_info = mt5.account_info()
        
        if account_info:
            print("Account info:")
            print(f"  Login: {account_info.login}")
            print(f"  Server: {account_info.server}")
            print(f"  Balance: {account_info.balance}")
            print(f"  Equity: {account_info.equity}")
            print(f"  Margin: {account_info.margin}")
            print(f"  Free Margin: {account_info.margin_free}")
        
        # Step 4: Get available symbols
        print("\nStep 4: Getting available symbols...")
        symbols = mt5.symbols_get()
        
        if symbols:
            print(f"Found {len(symbols)} symbols")
            print("First 5 symbols:")
            for i in range(min(5, len(symbols))):
                print(f"  {symbols[i].name}")
    
    # Step 5: Shutdown MT5
    print("\nStep 5: Shutting down MT5...")
    mt5.shutdown()
    print("MT5 shutdown complete")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
