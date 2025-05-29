#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MetaTrader 5 command handlers for the Telegram bot
This module contains handlers for MetaTrader 5 related commands
"""

import logging
import datetime

# Setup logging
logger = logging.getLogger(__name__)

def mt5_start_command(update, context, mt5_trader):
    """
    Handle the /mt5start command to start the MetaTrader 5 MCP Server
    
    Args:
        update: Telegram update object
        context: Telegram context object
        mt5_trader: MT5Trader instance
    """
    if not mt5_trader:
        update.message.reply_text("MetaTrader 5 integration is not available.")
        return
    
    update.message.reply_text("Starting MetaTrader 5 MCP Server... This may take a moment.")
    
    try:
        if mt5_trader.start_server():
            update.message.reply_text("✅ MetaTrader 5 MCP Server started successfully.")
        else:
            update.message.reply_text("❌ Failed to start MetaTrader 5 MCP Server. Check logs for details.")
    except Exception as e:
        logger.error(f"Error starting MT5 MCP Server: {e}")
        update.message.reply_text(f"❌ Error starting MetaTrader 5 MCP Server: {str(e)}")

def mt5_connect_command(update, context, mt5_trader):
    """
    Handle the /mt5connect command to connect to MetaTrader 5 account
    
    Args:
        update: Telegram update object
        context: Telegram context object
        mt5_trader: MT5Trader instance
    """
    if not mt5_trader:
        update.message.reply_text("MetaTrader 5 integration is not available.")
        return
    
    update.message.reply_text("Connecting to MetaTrader 5... This may take a moment.")
    
    try:
        if mt5_trader.connect():
            account_info = mt5_trader.get_account_info()
            
            # Format account info
            if account_info and "error" not in account_info:
                balance = account_info.get("balance", 0)
                equity = account_info.get("equity", 0)
                leverage = account_info.get("leverage", 0)
                margin_level = account_info.get("margin_level", 0)
                
                info_message = f"""
✅ Connected to MetaTrader 5 account successfully.

Account Information:
Balance: ${balance:.2f}
Equity: ${equity:.2f}
Leverage: 1:{leverage}
Margin Level: {margin_level:.2f}%
"""
                update.message.reply_text(info_message)
            else:
                update.message.reply_text("✅ Connected to MetaTrader 5 account.")
        else:
            update.message.reply_text("❌ Failed to connect to MetaTrader 5. Check your credentials.")
    except Exception as e:
        logger.error(f"Error connecting to MT5: {e}")
        update.message.reply_text(f"❌ Error connecting to MetaTrader 5: {str(e)}")

def mt5_status_command(update, context, mt5_trader):
    """
    Handle the /mt5status command to check MetaTrader 5 connection status
    
    Args:
        update: Telegram update object
        context: Telegram context object
        mt5_trader: MT5Trader instance
    """
    if not mt5_trader:
        update.message.reply_text("MetaTrader 5 integration is not available.")
        return
    
    try:
        # Check if the MCP server is running
        server_running = False
        if hasattr(mt5_trader, 'server_manager') and mt5_trader.server_manager is not None:
            try:
                server_running = mt5_trader.server_manager.is_server_running()
            except Exception as e:
                logger.warning(f"Could not check server status: {e}")
        
        # Check if connected to MT5
        is_connected = mt5_trader.is_connected
        
        # Get account info if connected
        account_info = mt5_trader.get_account_info() if is_connected else {}
        
        # Format the status message
        status_message = f"""
MetaTrader 5 Status:

MCP Server: {"✅ Running" if server_running else "❌ Not running"}
MT5 Connection: {"✅ Connected" if is_connected else "❌ Not connected"}
Auto-Trading: {"✅ Enabled" if mt5_trader.auto_trade else "❌ Disabled"}
"""

        # Add account info if connected
        if is_connected and account_info and "error" not in account_info:
            balance = account_info.get("balance", 0)
            equity = account_info.get("equity", 0)
            
            status_message += f"""
Account Balance: ${balance:.2f}
Account Equity: ${equity:.2f}
"""
        
        update.message.reply_text(status_message)
    except Exception as e:
        logger.error(f"Error checking MT5 status: {e}")
        update.message.reply_text(f"❌ Error checking MetaTrader 5 status: {str(e)}")

def mt5_positions_command(update, context, mt5_trader):
    """
    Handle the /mt5positions command to view open positions
    
    Args:
        update: Telegram update object
        context: Telegram context object
        mt5_trader: MT5Trader instance
    """
    if not mt5_trader:
        update.message.reply_text("MetaTrader 5 integration is not available.")
        return
    
    if not mt5_trader.is_connected:
        update.message.reply_text("Not connected to MetaTrader 5. Use /mt5connect to connect.")
        return
    
    try:
        # Get open positions
        result = mt5_trader.get_positions()
        
        if "error" in result:
            update.message.reply_text(f"❌ Error getting positions: {result['error']}")
            return
        
        positions = result.get("positions", [])
        
        if not positions:
            update.message.reply_text("No open positions.")
            return
        
        # Format positions
        positions_message = "Open Positions:\n\n"
        
        for pos in positions:
            symbol = pos.get("symbol", "Unknown")
            volume = pos.get("volume", 0)
            type_str = "BUY" if pos.get("type") == 0 else "SELL"
            open_price = pos.get("price_open", 0)
            current_price = pos.get("price_current", 0)
            profit = pos.get("profit", 0)
            
            positions_message += f"""
{symbol} {type_str} {volume} lots
Open: {open_price:.5f} | Current: {current_price:.5f}
Profit: {"+" if profit >= 0 else ""}{profit:.2f} USD
----------------------------
"""
        
        update.message.reply_text(positions_message)
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        update.message.reply_text(f"❌ Error getting positions: {str(e)}")

def mt5_autotrade_command(update, context, mt5_trader):
    """
    Handle the /mt5autotrade command to enable/disable auto-trading
    
    Args:
        update: Telegram update object
        context: Telegram context object
        mt5_trader: MT5Trader instance
    """
    if not mt5_trader:
        update.message.reply_text("MetaTrader 5 integration is not available.")
        return
    
    # Check if an argument was provided
    if not context.args or len(context.args) < 1:
        current_status = "enabled" if mt5_trader.auto_trade else "disabled"
        update.message.reply_text(f"Auto-trading is currently {current_status}.\nUse /mt5autotrade on or /mt5autotrade off to change.")
        return
    
    # Get the argument
    arg = context.args[0].lower()
    
    if arg in ["on", "true", "yes", "enable", "1"]:
        mt5_trader.auto_trade = True
        update.message.reply_text("✅ Auto-trading has been enabled. Signals will be automatically executed.")
    elif arg in ["off", "false", "no", "disable", "0"]:
        mt5_trader.auto_trade = False
        update.message.reply_text("❌ Auto-trading has been disabled. Signals will not be executed.")
    else:
        update.message.reply_text("Invalid argument. Use 'on' or 'off'.")

def mt5_test_command(update, context, mt5_trader):
    """
    Handle the /mt5test command to place a test order
    
    Args:
        update: Telegram update object
        context: Telegram context object
        mt5_trader: MT5Trader instance
    """
    if not mt5_trader:
        update.message.reply_text("MetaTrader 5 integration is not available.")
        return
    
    if not mt5_trader.is_connected:
        update.message.reply_text("Not connected to MetaTrader 5. Use /mt5connect to connect.")
        return
    
    # Get symbol and volume from arguments
    symbol = "EURUSD"  # Default symbol
    volume = 0.01      # Default volume
    
    if context.args and len(context.args) >= 1:
        symbol = context.args[0].upper()
    
    if context.args and len(context.args) >= 2:
        try:
            volume = float(context.args[1])
        except ValueError:
            update.message.reply_text("Invalid volume. Using default volume of 0.01 lots.")
    
    update.message.reply_text(f"Placing a test BUY order for {symbol} with volume {volume} lots...")
    
    try:
        # Place test order
        result = mt5_trader.place_test_order(symbol=symbol, volume=volume)
        
        if result.get("success", False):
            update.message.reply_text(f"✅ Test order placed successfully!\n\nDetails: {result.get('result', {})}")
        else:
            update.message.reply_text(f"❌ Failed to place test order: {result.get('error', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Error placing test order: {e}")
        update.message.reply_text(f"❌ Error placing test order: {str(e)}")
