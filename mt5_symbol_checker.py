#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MT5 Symbol Checker - Diagnose symbol availability and trading permissions
"""

import os
import logging
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mt5-symbol-checker")

# Load environment variables
load_dotenv()

def check_mt5_symbols():
    """Check available symbols and trading permissions"""
    # Initialize MT5
    logger.info("Initializing MT5...")
    if not mt5.initialize():
        logger.error(f"Failed to initialize MT5: {mt5.last_error()}")
        return False
    
    # Login if needed
    account = os.getenv("MT5_ACCOUNT", "210053016")
    password = os.getenv("MT5_PASSWORD", "Korede16@@")
    server = os.getenv("MT5_SERVER", "Exness-MT5Trial9")
    
    logger.info(f"Logging in to account {account} on server {server}...")
    login_result = mt5.login(login=int(account), password=password, server=server)
    
    if not login_result:
        logger.error(f"Failed to login: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    logger.info("Login successful!")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        logger.info(f"Account: {account_info.login}, Balance: {account_info.balance} {account_info.currency}")
        logger.info(f"Leverage: 1:{account_info.leverage}")
        logger.info(f"Margin Free: {account_info.margin_free} {account_info.currency}")
    
    # Check available symbols
    logger.info("Checking available symbols...")
    symbols = mt5.symbols_get()
    if not symbols:
        logger.error("Failed to get symbols")
        mt5.shutdown()
        return False
    
    logger.info(f"Total symbols available: {len(symbols)}")
    
    # Print common forex symbols
    common_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    logger.info("Checking common symbols:")
    
    for symbol_name in common_symbols:
        symbol_info = mt5.symbol_info(symbol_name)
        if symbol_info:
            logger.info(f"  ✓ {symbol_name} is available")
            logger.info(f"    Visible: {symbol_info.visible}, Selected: {symbol_info.select}")
            logger.info(f"    Trade Mode: {symbol_info.trade_mode}, Bid: {symbol_info.bid}, Ask: {symbol_info.ask}")
            
            # Try to select it for trading
            if not symbol_info.visible:
                select_result = mt5.symbol_select(symbol_name, True)
                logger.info(f"    Selection attempt: {'Successful' if select_result else 'Failed'}")
        else:
            logger.info(f"  ✗ {symbol_name} is NOT available")
    
    # Check trading settings
    logger.info("\nChecking trading settings...")
    terminal_info = mt5.terminal_info()
    if terminal_info:
        logger.info(f"Trade allowed: {terminal_info.trade_allowed}")
        logger.info(f"Expert allowed: {terminal_info.trade_expert}")
        logger.info(f"Auto trading: {terminal_info.trade_expert_allowed}")
    
    # Shutdown
    mt5.shutdown()
    return True

if __name__ == "__main__":
    check_mt5_symbols()
