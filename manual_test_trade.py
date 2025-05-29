#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manual test trade - directly place a small test trade to diagnose issues
"""

import os
import logging
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test-trade")

# Load environment variables
load_dotenv()

def place_test_trade():
    """Place a very small test trade to diagnose issues"""
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
    
    # Symbol selection
    symbol = "EURUSD"  # Using EURUSD as it's almost always available
    logger.info(f"Preparing to place test trade for {symbol}")
    
    # Make sure symbol is enabled for trading
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select {symbol} for trading")
        mt5.shutdown()
        return False
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logger.error(f"Failed to get current price for {symbol}")
        mt5.shutdown()
        return False
    
    bid = tick.bid
    ask = tick.ask
    logger.info(f"Current {symbol} prices: Bid={bid}, Ask={ask}")
    
    # Get account info
    account_info = mt5.account_info()
    if not account_info:
        logger.error("Failed to get account info")
        mt5.shutdown()
        return False
    
    logger.info(f"Account balance: {account_info.balance} {account_info.currency}")
    logger.info(f"Account margin: {account_info.margin} {account_info.currency}")
    logger.info(f"Account leverage: 1:{account_info.leverage}")
    
    # Check symbol info
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        logger.error(f"Failed to get symbol info for {symbol}")
        mt5.shutdown()
        return False
    
    # Calculate appropriate volume (use minimum allowed)
    min_volume = symbol_info.volume_min
    logger.info(f"Minimum allowed volume: {min_volume} lots")
    volume = min_volume
    
    # Calculate appropriate stop loss and take profit levels
    point = symbol_info.point
    price = ask  # Buy price
    stop_loss = bid - 50 * point  # 50 points below bid
    take_profit = ask + 100 * point  # 100 points above ask
    
    # Create the request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": float(stop_loss),
        "tp": float(take_profit),
        "deviation": 20,
        "magic": 12345,
        "comment": "Test trade from Python",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Log the full request
    logger.info(f"Sending order request: {request}")
    
    # Send the order
    result = mt5.order_send(request)
    
    # Process the result
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"✅ Order executed successfully! Order ID: {result.order}")
        logger.info(f"Trade details: {symbol} BUY {volume} lots at {price}")
        logger.info(f"Stop Loss: {stop_loss}, Take Profit: {take_profit}")
    else:
        if result:
            logger.error(f"❌ Order failed with code {result.retcode}")
        else:
            logger.error(f"❌ Order failed: {mt5.last_error()}")
    
    # Check positions
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        logger.info(f"Open positions for {symbol}:")
        for position in positions:
            logger.info(f"  Position: {position.identifier}, Type: {'Buy' if position.type == mt5.POSITION_TYPE_BUY else 'Sell'}, Volume: {position.volume}, Profit: {position.profit}")
    else:
        logger.info(f"No open positions for {symbol}")
    
    # Shutdown
    mt5.shutdown()
    return True

if __name__ == "__main__":
    place_test_trade()
