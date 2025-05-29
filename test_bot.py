#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the forex trading bot
This will test various functionalities of the bot
"""

import os
import time
import requests
import logging
import json
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_command(command):
    """Send a command to the Telegram bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": command
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info(f"Command sent: {command}")
            return True
        else:
            logger.error(f"Failed to send command: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return False

def test_basic_commands():
    """Test basic bot commands"""
    commands = [
        "/start",
        "/help",
        "/status",
        "/invest 100",
        "/signal"
    ]
    
    for command in commands:
        logger.info(f"Testing command: {command}")
        if send_command(command):
            # Wait for bot to process and respond
            time.sleep(2)
        else:
            logger.error(f"Failed to test command: {command}")

def test_mt5_commands():
    """Test MetaTrader 5 integration commands"""
    commands = [
        "/mt5status",
        "/mt5start",
        "/mt5connect"
    ]
    
    for command in commands:
        logger.info(f"Testing command: {command}")
        if send_command(command):
            # Wait for bot to process and respond
            time.sleep(5)  # Give more time for MT5 operations
        else:
            logger.error(f"Failed to test command: {command}")

def test_timezone_setting():
    """Test timezone setting functionality"""
    timezones = ["US/Eastern", "Europe/London", "Asia/Tokyo"]
    
    for timezone in timezones:
        command = f"/timezone {timezone}"
        logger.info(f"Testing command: {command}")
        if send_command(command):
            # Wait for bot to process and respond
            time.sleep(2)
        else:
            logger.error(f"Failed to test command: {command}")
    
    # Reset to original timezone
    send_command("/timezone US/Central")

def run_tests():
    """Run all tests"""
    logger.info("Starting forex bot tests...")
    
    # Test basic commands
    test_basic_commands()
    
    # Test timezone setting
    test_timezone_setting()
    
    # Test MT5 commands if enabled
    if os.getenv('MT5_ENABLED', 'false').lower() == 'true':
        test_mt5_commands()
    
    logger.info("Tests completed!")

if __name__ == "__main__":
    run_tests()
