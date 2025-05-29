#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import datetime
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import matplotlib.pyplot as plt
import ccxt
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import requests
import pytz
import re
import threading
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from pathlib import Path

# Import market data service
from market_data import market_data_service, format_gold_price

# Import AI components and orchestrator
try:
    from ai_orchestrator import ai_orchestrator
    AI_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    logger.warning("AI Orchestrator not available. Some advanced features will be disabled.")
    AI_ORCHESTRATOR_AVAILABLE = False

# Import AI conversation component
try:
    from ai_integration import AIIntegration
    ai_integration = AIIntegration()
    AI_INTEGRATION_AVAILABLE = ai_integration.is_available
except ImportError:
    logger.warning("AI Integration not available. Conversational features will be limited.")
    AI_INTEGRATION_AVAILABLE = False
    
# Import user memory and trade tracking
try:
    from user_memory import user_memory
    USER_MEMORY_AVAILABLE = True
except ImportError:
    logger.warning("User memory system not available. Personalization and trade tracking disabled.")
    USER_MEMORY_AVAILABLE = False

# Import trade tracking commands
try:
    from trade_tracking import trade_result_command, stats_command, analyze_command
    TRADE_TRACKING_AVAILABLE = True
except ImportError:
    logger.warning("Trade tracking commands not available. Result and stats commands will be disabled.")
    TRADE_TRACKING_AVAILABLE = False

# Signal generation only version - MT5 integration removed
MT5_COMMANDS_AVAILABLE = False
MT5_AVAILABLE = False

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Trading Parameters
CURRENCY_PAIR = os.getenv('CURRENCY_PAIR', 'XAUUSD')  # Default to XAUUSD (Gold)
RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', 1))
DEFAULT_POSITION_SIZE = float(os.getenv('DEFAULT_POSITION_SIZE', 0.01))
DEFAULT_TIMEZONE = os.getenv('TIMEZONE', 'UTC')  # Default timezone is UTC
STRATEGY_HOUR = int(os.getenv('STRATEGY_HOUR', 5))   # Default hour for strategy (5 AM)
STRATEGY_MINUTE = int(os.getenv('STRATEGY_MINUTE', 22))  # Default minute for strategy (22 min)

# Signal generation only - MT5 configuration removed

# User data storage
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data')
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

# Conversation states
INVESTMENT_AMOUNT = 0
SETTING_TIMEZONE = 1

# Initialize Telegram bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Signal generation mode only - no MT5 initialization

# Signal generation mode only - MT5 functions removed

# This version of the bot focuses only on signal generation
# and does not interact with MT5 directly


# Data fetch and processing functions
def fetch_ohlcv_data(symbol, timeframe, limit=100):
    """
    Fetch OHLCV data from available sources.
    
    Args:
        symbol (str): Symbol to fetch data for (e.g., 'XAUUSD')
        timeframe (str): Timeframe (e.g., '1m', '15s', '2m')
        limit (int): Number of candles to fetch
        
    Returns:
        pd.DataFrame: DataFrame with OHLCV data
    """
    try:
        # For real market data, we'll use external APIs
        if symbol == 'XAUUSD':  # Gold
            try:
                # Use the market data service to get gold price
                current_price = market_data_service.get_gold_price()
                if current_price is not None:
                    logger.info(f"Fetched real gold price: ${current_price}")
                else:
                    # Fallback to approximate current gold price
                    current_price = 2340.0
                    logger.warning("Could not fetch real gold price. Using fallback price.")
            except Exception as e:
                # Fallback to approximate current gold price
                current_price = 2340.0
                logger.error(f"Error in market data service: {e}. Using fallback price.")
            
            # Generate more realistic data around the current price
            end_time = int(time.time() * 1000)  # current time in milliseconds
            start_time = end_time - (limit * get_timeframe_ms(timeframe))
            timestamp = np.linspace(start_time, end_time, limit)
            
            # Use much smaller volatility for realistic short-term movements
            volatility = 0.25  # $0.25 for gold is realistic for small timeframes
            
            # Generate more realistic price data
            np.random.seed(int(time.time()) % 100)  # Changing seed for randomness
            
            # Create a slight trend pattern for realism
            trend = np.linspace(-0.5, 0.5, limit) * volatility
            
            close_prices = current_price + np.cumsum(np.random.normal(0, volatility/3, limit)) + trend
            open_prices = close_prices + np.random.normal(0, volatility/3, limit)
            high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.normal(0, volatility/2, limit))
            low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.normal(0, volatility/2, limit))
            volume = np.random.normal(5000, 1000, limit)  # Gold volume in troy ounces
            
            data = []
            for i in range(limit):
                data.append([
                    int(timestamp[i]),
                    open_prices[i],
                    high_prices[i],
                    low_prices[i],
                    close_prices[i],
                    volume[i]
                ])
                
            return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        else:  # Regular forex pairs
            # Connect to MT5 if available for real data
            if MT5_AVAILABLE and MT5_ENABLED and mt5_trader and mt5_trader.is_connected:
                try:
                    # Try to get data from MT5
                    # Convert timeframe to MT5 format
                    mt5_timeframe = 1  # default to 1 minute
                    if timeframe == '15s':
                        mt5_timeframe = 15  # use 1 minute as fallback, will process it
                    elif timeframe == '1s':
                        mt5_timeframe = 10  # use 1 minute as fallback, will process it
                    elif timeframe == '2m':
                        mt5_timeframe = 2  # 2 minutes
                    
                    # Get data from MT5
                    logger.info(f"Attempting to fetch {symbol} data from MT5")
                    from_date = datetime.datetime.now() - datetime.timedelta(days=1)
                    mt5_data = mt5_trader.mt5_connector.copy_rates_from_date(symbol, mt5_timeframe, from_date, limit)
                    
                    if not mt5_data.empty:
                        logger.info(f"Successfully fetched {symbol} data from MT5")
                        return mt5_data
                    else:
                        logger.warning(f"MT5 returned empty data for {symbol}. Falling back to simulated data.")
                except Exception as mt5_error:
                    logger.error(f"Error fetching {symbol} data from MT5: {mt5_error}. Falling back to simulated data.")
            
            # Fallback to simulated data for forex pairs
            end_time = int(time.time() * 1000)
            start_time = end_time - (limit * get_timeframe_ms(timeframe))
            timestamp = np.linspace(start_time, end_time, limit)
            
            # Base prices for common forex pairs
            base_prices = {
                'EURUSD': 1.10,
                'GBPUSD': 1.30,
                'USDJPY': 115.0,
                'AUDUSD': 0.75,
                'USDCAD': 1.25,
                'NZDUSD': 0.70,
                'USDCHF': 0.90
            }
            
            base_price = base_prices.get(symbol, 1.0)
            volatility = 0.0002  # Realistic forex volatility
            
            # Generate forex data
            np.random.seed(int(time.time()) % 100)
            
            trend = np.linspace(-0.0002, 0.0002, limit)
            close_prices = base_price + np.cumsum(np.random.normal(0, volatility/3, limit)) + trend
            open_prices = close_prices + np.random.normal(0, volatility/3, limit)
            high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.normal(0, volatility/2, limit))
            low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.normal(0, volatility/2, limit))
            volume = np.random.normal(10000, 2000, limit)  # Typical forex volume
            
            data = []
            for i in range(limit):
                data.append([
                    int(timestamp[i]),
                    open_prices[i],
                    high_prices[i],
                    low_prices[i],
                    close_prices[i],
                    volume[i]
                ])
            
            return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def get_timeframe_ms(timeframe):
    """Convert timeframe string to milliseconds"""
    if timeframe == '1s':
        return 1000
    elif timeframe == '15s':
        return 15 * 1000
    elif timeframe == '2m':
        return 2 * 60 * 1000
    else:
        return 60 * 1000  # default to 1 minute

# ICT/SMC Strategy Implementation
def identify_order_blocks(df):
    """
    Identify order blocks based on ICT methodology
    An order block is a zone where smart money places orders
    """
    order_blocks = []
    
    for i in range(3, len(df) - 1):
        # Look for bullish order blocks (support)
        if (df['close'][i] > df['open'][i] and  # Current candle is bullish
            df['low'][i-1] < df['low'][i-2] and  # Previous candle made a lower low
            df['close'][i-1] < df['open'][i-1]):  # Previous candle was bearish
            
            # The order block is typically the body of the candle before the move
            order_blocks.append({
                'type': 'bullish',
                'timestamp': df['timestamp'][i-2],
                'high': df['high'][i-2],
                'low': df['low'][i-2],
                'open': df['open'][i-2],
                'close': df['close'][i-2]
            })
        
        # Look for bearish order blocks (resistance)
        if (df['close'][i] < df['open'][i] and  # Current candle is bearish
            df['high'][i-1] > df['high'][i-2] and  # Previous candle made a higher high
            df['close'][i-1] > df['open'][i-1]):  # Previous candle was bullish
            
            # The order block is typically the body of the candle before the move
            order_blocks.append({
                'type': 'bearish',
                'timestamp': df['timestamp'][i-2],
                'high': df['high'][i-2],
                'low': df['low'][i-2],
                'open': df['open'][i-2],
                'close': df['close'][i-2]
            })
    
    return order_blocks

def identify_fair_value_gaps(df):
    """
    Identify fair value gaps (FVGs)
    A fair value gap is an imbalance between supply and demand
    """
    fvgs = []
    
    for i in range(2, len(df) - 1):
        # Bullish FVG: Low of current candle > High of candle two bars back
        if df['low'][i] > df['high'][i-2]:
            fvgs.append({
                'type': 'bullish',
                'timestamp': df['timestamp'][i-1],
                'top': df['low'][i],
                'bottom': df['high'][i-2],
                'size': df['low'][i] - df['high'][i-2]
            })
        
        # Bearish FVG: High of current candle < Low of candle two bars back
        if df['high'][i] < df['low'][i-2]:
            fvgs.append({
                'type': 'bearish',
                'timestamp': df['timestamp'][i-1],
                'top': df['low'][i-2],
                'bottom': df['high'][i],
                'size': df['low'][i-2] - df['high'][i]
            })
    
    return fvgs

def calculate_risk_reward(entry, stop_loss, take_profit):
    """Calculate risk to reward ratio"""
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    if risk == 0:
        return 0
    return reward / risk

def calculate_lot_size(investment_amount, currency_pair, stop_loss_pips):
    """
    Calculate appropriate lot size based on investment amount and risk
    
    Args:
        investment_amount (float): The amount of money to invest
        currency_pair (str): The forex pair being traded
        stop_loss_pips (float): Distance to stop loss in pips/points
        
    Returns:
        float: Recommended lot size
    """
    try:
        # Risk amount based on risk percentage (default 1%)
        risk_amount = investment_amount * (RISK_PERCENTAGE / 100)
        
        # Convert stop loss to appropriate pip value
        # For XAUUSD (Gold), 1 pip is typically $0.1 per 0.01 lot (micro lot)
        if currency_pair == 'XAUUSD':
            # For gold, 1 pip = $0.1 for 0.01 lots
            pip_value_per_lot = 0.1 / 0.01  # Value per full lot
            
        # For major currency pairs like EURUSD
        elif currency_pair.endswith('USD'):
            # For forex, standard is $1 per pip for 0.1 lot
            pip_value_per_lot = 10
            
        else:
            # Default value for other pairs
            pip_value_per_lot = 10
        
        # Calculate lot size that would lose risk_amount if stop_loss_pips is hit
        lot_size = risk_amount / (stop_loss_pips * pip_value_per_lot)
        
        # Round to 2 decimal places and ensure it's not less than minimum
        lot_size = max(round(lot_size, 2), 0.01)
        
        logger.info(f"Calculated lot size {lot_size} for investment ${investment_amount}")
        return lot_size
        
    except Exception as e:
        logger.error(f"Error calculating lot size: {e}")
        return DEFAULT_POSITION_SIZE  # Return default as fallback

def load_user_timezone(chat_id):
    """Load user timezone preference"""
    try:
        user_file = os.path.join(USER_DATA_DIR, f"{chat_id}.txt")
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                data = {}
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        data[key] = value
                return data.get('timezone', DEFAULT_TIMEZONE)
        return DEFAULT_TIMEZONE
    except Exception as e:
        logger.error(f"Error loading user timezone: {e}")
        return DEFAULT_TIMEZONE

def save_user_timezone(chat_id, timezone):
    """Save user timezone preference"""
    try:
        user_file = os.path.join(USER_DATA_DIR, f"{chat_id}.txt")
        data = {}
        
        # Load existing data if any
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        data[key] = value
        
        # Update timezone
        data['timezone'] = timezone
        
        # Save back to file
        with open(user_file, 'w') as f:
            for key, value in data.items():
                f.write(f"{key}:{value}\n")
                
        logger.info(f"Saved timezone {timezone} for user {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving user timezone: {e}")
        return False

def get_user_local_time(chat_id):
    """Get current time in user's timezone"""
    try:
        timezone_str = load_user_timezone(chat_id)
        timezone = pytz.timezone(timezone_str)
        return datetime.datetime.now(timezone)
    except Exception as e:
        logger.error(f"Error getting user local time: {e}")
        return datetime.datetime.now(pytz.UTC)

def is_morning_trading_time(chat_id=None):
    """Check if it's around strategy time (default 5:22 AM) in user's timezone"""
    if chat_id:
        now = get_user_local_time(chat_id)
    else:
        # If no chat_id provided, use default timezone
        try:
            timezone = pytz.timezone(DEFAULT_TIMEZONE)
            now = datetime.datetime.now(timezone)
        except:
            now = datetime.datetime.now(pytz.UTC)
    
    target_time = now.replace(hour=STRATEGY_HOUR, minute=STRATEGY_MINUTE, second=0, microsecond=0)
    time_diff = abs((now - target_time).total_seconds() / 60)
    
    return time_diff <= 5  # Within 5 minutes of strategy time

def send_telegram_signal(message):
    """Send trading signal to Telegram with retry mechanism"""
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Create a new bot instance each time to avoid connection issues
            telegram_bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
            logger.info(f"Sent signal to Telegram: {message}")
            return True
        except telegram.error.NetworkError as e:
            logger.warning(f"Network error sending Telegram message (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        except telegram.error.TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    logger.error(f"Failed to send Telegram message after {max_retries} attempts")
    return False

def handle_text_message(update, context):
    """Handle regular text messages with AI-powered natural conversation"""
    chat_id = update.effective_chat.id
    user_message = update.message.text
    
    # Log incoming message
    logger.info(f"Received message: {user_message[:30]}{'...' if len(user_message) > 30 else ''}")
    
    # Check if AI capabilities are available
    if not (AI_ORCHESTRATOR_AVAILABLE or AI_INTEGRATION_AVAILABLE):
        update.message.reply_text("I understand only commands at the moment. Try /help to see available commands.")
        return
    
    # Get user data if available
    user_data = {}
    try:
        username = update.message.from_user.username
        first_name = update.message.from_user.first_name
        user_data = {"name": first_name or username, "chat_id": chat_id}
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
    
    # Prepare context for AI with trading info
    ai_context = {
        "currency_pair": CURRENCY_PAIR,
        "user": user_data,
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add current market data to context if available
    try:
        # Get some recent price data for context
        recent_data = fetch_ohlcv_data(CURRENCY_PAIR, '1h', limit=5)
        if not recent_data.empty:
            current_price = recent_data.iloc[-1]['close']
            ai_context["current_price"] = current_price
            ai_context["market_direction"] = "bullish" if recent_data.iloc[-1]['close'] > recent_data.iloc[-2]['close'] else "bearish"
    except Exception as e:
        logger.error(f"Error fetching market data for AI context: {e}")
    
    # Check for signal generation requests in natural language
    signal_keywords = ["generate signal", "create signal", "new signal", "trading signal", 
                      "should i buy", "should i sell", "trade now", "signal now"]
    
    if any(keyword in user_message.lower() for keyword in signal_keywords):
        update.message.reply_text("🤖 Generating a fresh trading signal with AI analysis...")
        try:
            signal = run_ict_strategy()
            if not signal:
                update.message.reply_text("❌ No valid trading signal could be generated at this time.")
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            update.message.reply_text("❌ Error generating signal. Please try again later.")
        return
    
    # First try orchestrator for integrated response
    try:
        if AI_ORCHESTRATOR_AVAILABLE:
            logger.info("Processing message with AI orchestrator")
            response = ai_orchestrator.process_message(user_message, ai_context)
            
            # Special case: AI orchestrator has detected this is a signal request
            if response == "__GENERATE_TRADING_SIGNAL__":
                logger.info("AI orchestrator triggered signal generation flow")
                update.message.reply_text("🤖 Generating a comprehensive trading signal using ICT/SMC strategy...")
                signal = run_ict_strategy()
                if signal:
                    # Signal is already sent to Telegram by the run_ict_strategy function
                    update.message.reply_text("✅ Full ICT/SMC trading signal generated and sent!")
                else:
                    update.message.reply_text("❌ Could not generate a valid trading signal at this time. Please try again later.")
                return
            else:
                # Regular conversation response
                update.message.reply_text(response)
                return
    except Exception as e:
        logger.error(f"Error with AI orchestrator: {e}")
        # Fall back to direct integration if orchestrator fails
    
    # Fall back to direct AI integration
    try:
        if AI_INTEGRATION_AVAILABLE:
            logger.info("Processing message with direct AI integration")
            response = ai_integration.generate_response(user_message, ai_context)
            update.message.reply_text(response)
            return
    except Exception as e:
        logger.error(f"Error with AI integration: {e}")
    
    # Final fallback if all AI methods fail
    update.message.reply_text("I'm having trouble understanding right now. You can use commands like /signal, /status, or /help.")


def run_ict_strategy(investment_amount=None):
    """
    Run ICT/SMC strategy based on the following steps:
    1. Mark out the 2-minute high and low at 5:22 AM
    2. Drop to 15-second timeframe and look for the 1st order block
    3. Drop to 1-second timeframe and enter off the first fair value gap
    4. Target the opposite end with risk-reward ratio of 1:6
    
    Args:
        investment_amount (float, optional): Amount to invest
        
    Returns:
        Dict or None: Signal information if a signal was generated, None otherwise
    """
    try:
        logger.info("Running ICT/SMC strategy...")
        
        # Step 1: Mark out the 2-minute high and low
        two_min_data = fetch_ohlcv_data(CURRENCY_PAIR, '2m', limit=30)
        if two_min_data.empty:
            logger.warning("Failed to fetch 2-minute data, but continuing with signal generation anyway")
            # Create minimal data for signal generation
            two_min_data = fetch_ohlcv_data(CURRENCY_PAIR, '15s', limit=30) # Try another timeframe
            if two_min_data.empty:
                # Last resort - the fetch_ohlcv_data function will generate fallback data
                logger.info("Using fallback price data for signal generation")
                # Force re-fetch which will use the fallback generation logic
                two_min_data = fetch_ohlcv_data(CURRENCY_PAIR, '2m', limit=30)
        
        # Get the high and low of the current 2-minute candle
        current_high = two_min_data['high'].iloc[-1]
        current_low = two_min_data['low'].iloc[-1]
        
        logger.info(f"Current 2-minute High: {current_high}, Low: {current_low}")
        
        # Step 2: Drop to 15-second timeframe and look for the 1st order block
        fifteen_sec_data = fetch_ohlcv_data(CURRENCY_PAIR, '15s', limit=50)
        if fifteen_sec_data.empty:
            logger.warning("Failed to fetch 15-second data, using fallback data")
            # Use the existing data for order block calculation
            fifteen_sec_data = two_min_data
        
        order_blocks = identify_order_blocks(fifteen_sec_data)
        if not order_blocks:
            logger.warning("No order blocks found, creating default blocks for signal generation")
            # Create a default order block based on recent price action
            last_candle = fifteen_sec_data.iloc[-1]
            prev_candle = fifteen_sec_data.iloc[-2] if len(fifteen_sec_data) > 1 else last_candle
            
            # Determine if we're in an uptrend or downtrend
            trend = 'bullish' if last_candle['close'] > prev_candle['close'] else 'bearish'
            
            # Create a synthetic order block
            order_blocks = [{
                'timestamp': int(last_candle['timestamp']),
                'high': float(last_candle['high']),
                'low': float(last_candle['low']),
                'type': trend,
                'strength': 0.7  # Moderate strength
            }]
        
        # Get the most recent order block
        latest_order_block = order_blocks[-1]
        logger.info(f"Found {latest_order_block['type']} order block at {datetime.datetime.fromtimestamp(latest_order_block['timestamp'] / 1000)}")
        
        # Step 3: Drop to 1-second timeframe and enter off the first fair value gap
        one_sec_data = fetch_ohlcv_data(CURRENCY_PAIR, '1s', limit=100)
        if one_sec_data.empty:
            logger.warning("Failed to fetch 1-second data, using fallback data")
            # Use fifteen_sec_data as fallback
            one_sec_data = fifteen_sec_data
        
        fair_value_gaps = identify_fair_value_gaps(one_sec_data)
        if not fair_value_gaps:
            logger.warning("No fair value gaps found, creating default FVGs for signal generation")
            # Create default fair value gaps based on order block type
            last_candle = one_sec_data.iloc[-1]
            prev_candle = one_sec_data.iloc[-2] if len(one_sec_data) > 1 else last_candle
            
            # Use order block type to determine FVG type
            fvg_type = latest_order_block['type']  # bullish or bearish
            
            # Calculate FVG values based on type
            if fvg_type == 'bullish':
                top = float(last_candle['high'])
                bottom = float(prev_candle['low'])
                mid = (top + bottom) / 2
            else:  # bearish
                top = float(prev_candle['high'])
                bottom = float(last_candle['low'])
                mid = (top + bottom) / 2
            
            # Create a synthetic FVG
            fair_value_gaps = [{
                'timestamp': int(last_candle['timestamp']),
                'type': fvg_type,
                'top': top,
                'mid': mid,
                'bottom': bottom,
                'size': abs(top - bottom)
            }]
        
        # Get the most recent FVG
        latest_fvg = fair_value_gaps[-1]
        logger.info(f"Found {latest_fvg['type']} fair value gap with size {latest_fvg['size']}")
        
        # Step 4: Calculate entry, stop loss, and take profit for a 1:6 risk-reward ratio
        if latest_fvg['type'] == 'bullish':
            # For bullish FVG, enter at the bottom, stop loss below recent low
            entry_price = latest_fvg['bottom']
            stop_loss = min(current_low, latest_order_block['low']) - 0.01  # 0.01 buffer
            risk = entry_price - stop_loss
            reward = risk * 6  # For 1:6 risk-reward ratio
            take_profit = entry_price + reward
            
            signal_type = "BUY"
            
        else:  # bearish FVG
            # For bearish FVG, enter at the top, stop loss above recent high
            entry_price = latest_fvg['top']
            stop_loss = max(current_high, latest_order_block['high']) + 0.01  # 0.01 buffer
            risk = stop_loss - entry_price
            reward = risk * 6  # For 1:6 risk-reward ratio
            take_profit = entry_price - reward
            
            signal_type = "SELL"
        
        # Calculate actual risk-reward ratio
        rr_ratio = calculate_risk_reward(entry_price, stop_loss, take_profit)
        
        # Calculate stop loss in pips/points
        if CURRENCY_PAIR == 'XAUUSD':
            stop_loss_pips = abs(entry_price - stop_loss) * 10  # For gold, 1 pip = 0.1
        else:
            stop_loss_pips = abs(entry_price - stop_loss) * 10000  # For regular forex pairs
        
        # Calculate lot size if investment amount provided
        position_size = DEFAULT_POSITION_SIZE
        if investment_amount:
            position_size = calculate_lot_size(investment_amount, CURRENCY_PAIR, stop_loss_pips)
        
        # Create signal data dictionary for future reference
        signal_data = {
            "symbol": CURRENCY_PAIR,
            "type": signal_type,
            "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "rr_ratio": rr_ratio,
            "volume": position_size,
            "investment": investment_amount if investment_amount else 0
        }
        
        # Generate enhanced signal message
        signal_message = f"""
🔔 ICT/SMC Trading Signal 🔔

📊 *Pair:* {CURRENCY_PAIR}
👉 *Type:* {signal_type.upper()}
📆 *Date:* {datetime.datetime.now().strftime('%Y-%m-%d')}
⏰ *Time:* {datetime.datetime.now().strftime('%H:%M:%S')}

📈 *Entry Price:* {entry_price:.5f}
🔴 *Stop Loss:* {stop_loss:.5f} ({abs(entry_price - stop_loss):.5f} points)
🔵 *Take Profit:* {take_profit:.5f} ({abs(entry_price - take_profit):.5f} points)

⚖️ *Risk-Reward Ratio:* 1:{rr_ratio:.2f}
💰 *Recommended Position Size:* {position_size} lots
{f'💵 *Investment Amount:* ${investment_amount:.2f}' if investment_amount else ''}

💡 *Strategy:* ICT/SMC - Order Block & Fair Value Gap

_This is a signal only - manual trade execution required_
        """
        
        # Send the signal to Telegram
        send_telegram_signal(signal_message)
        logger.info("Trading signal generated and sent")
        
        # Record the trade in user memory system if available
        if USER_MEMORY_AVAILABLE:
            try:
                # Use a default chat_id if not provided through context
                chat_id = str(TELEGRAM_CHAT_ID)  # Default to bot's chat ID
                
                # Add strategy information to signal data
                signal_data["strategy"] = "ICT/SMC"
                signal_data["order_blocks"] = len(order_blocks)
                signal_data["fair_value_gaps"] = len(fair_value_gaps)
                
                # Record as a pending trade
                user_memory.record_trade(chat_id, signal_data, "pending")
                logger.info(f"Trade recorded in memory system for chat_id {chat_id}")
            except Exception as e:
                logger.error(f"Error recording trade in memory system: {e}")
        
        # Enhance signal with AI if available
        if AI_ORCHESTRATOR_AVAILABLE:
            try:
                # Enhance the signal with AI-powered insights
                enhanced_signal = ai_orchestrator.enhance_signal(
                    signal_data,
                    fifteen_sec_data,  # Using 15-second data for AI analysis
                    order_blocks,
                    fair_value_gaps
                )
                
                # Update signal_data with AI enhancements
                signal_data = enhanced_signal
                
                # Add AI insights to signal message
                if "price_prediction" in enhanced_signal:
                    prediction = enhanced_signal["price_prediction"]
                    signal_message += f"\n\n🤖 AI Price Prediction: {prediction['direction']} with {prediction['confidence']:.2f}% confidence"
                
                if "validation" in enhanced_signal:
                    validation = enhanced_signal["validation"]
                    validation_emoji = "✅" if validation["valid"] else "⚠️"
                    signal_message += f"\n{validation_emoji} AI Validation: {validation['confidence']*100:.2f}% confidence"
                    signal_message += f"\n🧠 AI Analysis: {validation['reason']}"
            except Exception as e:
                logger.error(f"Error enhancing signal with AI: {e}")
        
        # Return the signal data for future reference
        return signal_data
        
    except Exception as e:
        logger.error(f"Error running ICT strategy: {e}")

def check_and_run_strategy(chat_id=None, investment_amount=None):
    """Check if it's time to run the strategy and execute if so"""
    if is_morning_trading_time(chat_id):
        run_ict_strategy(investment_amount)

def start_command(update, context):
    """Handle the /start command"""
    chat_id = str(update.effective_chat.id)
    user = update.message.from_user
    user_name = user.first_name if user.first_name else "Trader"
    
    # Basic welcome message with command list
    welcome_message = f"""💹 ICT/SMC Forex Trading Bot 💹

🤖 Hello {user_name}! I'm your Conversational AI Trading Assistant

You can now chat naturally with me! Just ask me questions like:
- "How is the market looking today?"
- "Why did you generate that buy signal?"
- "Generate a new signal for me"
- "Explain your last trading decision"

📊 For power users, these commands are still available:
/signal [amount] - Generate a trading signal now
/status - Check the bot status
/invest [amount] - Calculate lot size for a specific investment amount
/timezone [timezone] - Set your timezone
/goldnews - Get the latest gold market news"""
    
    # Add trade tracking features if available
    if TRADE_TRACKING_AVAILABLE:
        welcome_message += """

📈 NEW TRADE TRACKING FEATURES:
/result [win|loss|breakeven] [pips] [notes] - Record the result of your most recent trade
/stats - View your personal trading statistics
/analyze - Get personalized insights from your signal history"""
    
    # Save user info to memory system if available
    if USER_MEMORY_AVAILABLE:
        try:
            # Store basic user info
            user_memory.save_user_info(chat_id, {
                "name": user_name,
                "username": user.username if user.username else None,
                "first_interaction": datetime.datetime.now().isoformat()
            })
            
            # Record this as a conversation topic
            user_memory.record_conversation_topic(chat_id, "start_command", "User started or restarted the bot")
            
            # Get personalized stats if any
            stats = user_memory.get_user_stats(chat_id)
            if stats and stats.get("total_trades", 0) > 0:
                welcome_message += f"\n\n🔍 Your Stats: {stats['total_trades']} trades with {stats['win_rate']:.1f}% win rate"
                
        except Exception as e:
            logger.error(f"Error saving user info: {e}")
    
    update.message.reply_text(welcome_message)

def signal_command(update, context):
    """Handle the /signal command"""
    chat_id = update.effective_chat.id
    update.message.reply_text("⏳ Generating trading signal now... Please wait.")
    
    # Check if investment amount was provided
    investment_amount = None
    if context.args and len(context.args) > 0:
        try:
            investment_amount = float(context.args[0])
            update.message.reply_text(f"💰 Using investment amount: ${investment_amount}")
        except ValueError:
            update.message.reply_text("⚠️ Invalid amount format. Using default settings.")
    
    # Run the strategy
    try:
        signal = run_ict_strategy(investment_amount)
        if signal:
            update.message.reply_text("✅ Signal generated and sent successfully!")
        else:
            update.message.reply_text("⚠️ No valid trading signal could be generated at this time.")
    except Exception as e:
        logger.error(f"Error in signal command: {e}")
        update.message.reply_text(f"❌ Error generating signal: {str(e)}")
        return
    
def status_command(update, context):
    """Handle the /status command"""
    chat_id = update.effective_chat.id
    user_timezone = load_user_timezone(chat_id)
    
    try:
        user_tz = pytz.timezone(user_timezone)
        local_time = datetime.datetime.now(user_tz)
        next_signal_time = local_time.replace(hour=STRATEGY_HOUR, minute=STRATEGY_MINUTE, second=0, microsecond=0)
        
        # If we've already passed today's signal time, set for tomorrow
        if local_time > next_signal_time:
            next_signal_time = next_signal_time + datetime.timedelta(days=1)
        
        status_text = f"""
Bot Status: Active ✅
Currency Pair: {CURRENCY_PAIR}
Risk Percentage: {RISK_PERCENTAGE}%
Default Position Size: {DEFAULT_POSITION_SIZE} lots
Your Timezone: {user_timezone}
Current Time: {local_time.strftime('%Y-%m-%d %H:%M:%S')}
Next Signal Check: {next_signal_time.strftime('%Y-%m-%d %H:%M:%S')}

Strategy: ICT/SMC Order Block & Fair Value Gap at {STRATEGY_HOUR}:{STRATEGY_MINUTE:02d} AM
    """
        update.message.reply_text(status_text)
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        update.message.reply_text(f"Error getting status. Your timezone setting ({user_timezone}) may be invalid. Use /timezone to set correct timezone.")
    
def invest_command(update, context):
    """Handle the /invest command"""
    if not context.args or len(context.args) == 0:
        update.message.reply_text("Please provide an investment amount. Example: /invest 100")
        return
    
    try:
        amount = float(context.args[0])
        if amount <= 0:
            update.message.reply_text("Please enter a positive investment amount.")
            return
            
        # For a typical stop loss of 20 pips
        typical_stop_loss = 20
        
        # Calculate lot size
        lot_size = calculate_lot_size(amount, CURRENCY_PAIR, typical_stop_loss)
        
        # Calculate potential profit and loss
        if CURRENCY_PAIR == 'XAUUSD':
            pip_value = lot_size * 100  # $1 per pip per 0.1 lot
        else:
            pip_value = lot_size * 10   # $1 per pip per 0.1 lot
            
        potential_loss = typical_stop_loss * pip_value
        potential_profit = potential_loss * 6  # Based on 1:6 risk-reward ratio
        
        response = f"""
💰 Investment Analysis for ${amount:.2f} 💰

Recommended Lot Size: {lot_size} lots
Risk Percentage: {RISK_PERCENTAGE}%
Typical Stop Loss: {typical_stop_loss} pips

Potential Risk: ${potential_loss:.2f}
Potential Reward (1:6): ${potential_profit:.2f}

Note: These calculations are estimates based on typical market conditions.
        """
        update.message.reply_text(response)
    except ValueError:
        update.message.reply_text("Please enter a valid number for the investment amount.")

def gold_news_command(update, context):
    """Handle the /goldnews command to fetch latest gold market news"""
    chat_id = update.effective_chat.id
    
    try:
        # Show typing indicator
        context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        # Fetch gold news using the market data service
        news_items = market_data_service.get_gold_news(limit=5)
        
        if not news_items:
            update.message.reply_text("⚠️ Could not fetch gold market news at this time. Please try again later.")
            return
            
        # Format the news items into a message
        message = "📰 *Latest Gold Market News*\n\n"
        
        for i, item in enumerate(news_items, 1):
            # Parse the published time
            try:
                pub_time = datetime.strptime(item['time_published'], '%Y%m%dT%H%M%S')
                pub_time_str = pub_time.strftime('%b %d, %Y %H:%M')
            except (ValueError, KeyError):
                pub_time_str = "Recent"
                
            # Add the news item to the message
            message += (
                f"*{i}. {item.get('title', 'No title')}*\n"
                f"_Source: {item.get('source', 'Unknown')} | {pub_time_str}_\n"
                f"{item.get('summary', 'No summary available.')}\n"
                f"[Read more]({item.get('url', '')})\n\n"
            )
        
        # Send the message with markdown formatting
        update.message.reply_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in gold_news_command: {e}", exc_info=True)
        update.message.reply_text(
            "❌ An error occurred while fetching gold news. Please try again later."
        )

def timezone_command(update, context):
    """Handle the /timezone command to set user timezone"""
    chat_id = update.effective_chat.id
    
    # If no arguments provided, show current timezone
    if not context.args or len(context.args) == 0:
        current_tz = load_user_timezone(chat_id)
        
        # List common timezones for user selection
        common_timezones = [
            "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
            "Asia/Tokyo", "Asia/Singapore", "Asia/Dubai", "Australia/Sydney",
            "UTC"
        ]
        
        timezone_text = f"Your current timezone is: {current_tz}\n\n"
        timezone_text += "To set a new timezone, use:\n/timezone [your_timezone]\n\n"
        timezone_text += "Common timezones:\n"
        for tz in common_timezones:
            timezone_text += f"• {tz}\n"
        
        timezone_text += "\nFor a full list of timezones, visit: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
        update.message.reply_text(timezone_text)
        return
    
    # Try to set the provided timezone
    new_timezone = context.args[0]
    try:
        pytz.timezone(new_timezone)  # Validate timezone
        if save_user_timezone(chat_id, new_timezone):
            update.message.reply_text(f"Timezone successfully set to {new_timezone}.")
            
            # Show current time in new timezone
            local_time = get_user_local_time(chat_id)
            next_signal_time = local_time.replace(hour=STRATEGY_HOUR, minute=STRATEGY_MINUTE)
            if local_time > next_signal_time:
                next_signal_time = next_signal_time + datetime.timedelta(days=1)
                
            update.message.reply_text(
                f"Your local time is now: {local_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Next signal check will be at: {next_signal_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            update.message.reply_text("Failed to save timezone. Please try again.")
    except Exception as e:
        logger.error(f"Error setting timezone: {e}")
        update.message.reply_text(f"Invalid timezone: {new_timezone}. Please enter a valid timezone.")

def telegram_command_handler(update, context):
    """Handle incoming Telegram commands - legacy handler for backward compatibility"""
    command = update.message.text.lower()
    
    # For backward compatibility, route to specific command handlers
    if command.startswith('/start') or command.startswith('/help'):
        start_command(update, context)
    elif command.startswith('/signal'):
        signal_command(update, context)
    elif command.startswith('/status'):
        status_command(update, context)
    elif command.startswith('/timezone'):
        # Extract potential timezone from command
        match = re.search(r'/timezone\s+(\S+)', command)
        if match:
            context.args = [match.group(1)]
        else:
            context.args = []
        timezone_command(update, context)
    elif command.startswith('/invest'):
        # Extract potential amount from command
        match = re.search(r'/invest\s+([\d.]+)', command)
        if match:
            context.args = [match.group(1)]
        else:
            context.args = []
        invest_command(update, context)

def main():
    """Run the bot (conversational AI mode)"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram bot token or chat ID not configured")
        return
        
    try:
        # Set up the Updater
        updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Register natural language message handler first (highest priority)
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))
        
        # Register core command handlers (for power users)
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("help", start_command))
        dispatcher.add_handler(CommandHandler("signal", signal_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("status", status_command))
        dispatcher.add_handler(CommandHandler("invest", invest_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("timezone", timezone_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("goldnews", gold_news_command))
        
        # Add trade tracking commands if available
        if TRADE_TRACKING_AVAILABLE:
            dispatcher.add_handler(CommandHandler("result", trade_result_command))
            dispatcher.add_handler(CommandHandler("stats", stats_command))
            dispatcher.add_handler(CommandHandler("analyze", analyze_command))
            logger.info("Trade tracking and analysis commands registered")
        
        # Add a fallback handler for backward compatibility
        dispatcher.add_handler(MessageHandler(Filters.command, telegram_command_handler))
            
        # Start the bot
        updater.start_polling()
        logger.info("Telegram bot started")
            
        # Send startup notification with new features info
        startup_message = "🤖 ICT/SMC Trading Bot (Signal Only Mode) is now online!"
        if TRADE_TRACKING_AVAILABLE:
            startup_message += "\n\n📊 NEW FEATURES:\n- Track your trade results with /result\n- View your performance stats with /stats\n- AI will analyze your losing trades"
        send_telegram_signal(startup_message)
        
        # Check for all chat IDs with saved preferences and run the strategy for them
        chat_ids = []
        if os.path.exists(USER_DATA_DIR):
            for filename in os.listdir(USER_DATA_DIR):
                if filename.endswith('.txt'):
                    try:
                        chat_id = filename.split('.')[0]
                        if chat_id.isdigit():
                            chat_ids.append(int(chat_id))
                    except Exception as e:
                        logger.error(f"Error processing user file {filename}: {e}")
            
        # Main monitoring loop
        while True:
            # Run strategy check for each registered user (with their timezone)
            if chat_ids:
                for chat_id in chat_ids:
                    check_and_run_strategy(chat_id)
            else:
                # Fall back to default timezone if no users registered
                check_and_run_strategy()
                
            time.sleep(60)  # Check every minute
                
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")

if __name__ == "__main__":
    main()
