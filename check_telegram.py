#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Check Telegram connectivity
"""

import os
import requests
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_telegram_connection():
    """Check if the Telegram bot token is valid"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Checking Telegram connection...")
    print(f"Bot Token: {bot_token[:5]}...{bot_token[-5:]} (length: {len(bot_token)})")
    print(f"Chat ID: {chat_id}")
    
    # Check if the bot token is valid
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info["ok"]:
                print(f"✓ Bot token is valid!")
                print(f"Bot name: {bot_info['result']['first_name']}")
                print(f"Bot username: @{bot_info['result']['username']}")
            else:
                print(f"✗ Bot token is invalid: {bot_info}")
                return False
        else:
            print(f"✗ Error verifying bot token: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception checking bot token: {e}")
        return False
    
    # Try to send a test message
    test_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    test_data = {
        "chat_id": chat_id,
        "text": "🔍 Connectivity Test: Your forex trading bot is operational!"
    }
    
    try:
        print(f"\nAttempting to send test message to chat ID: {chat_id}")
        test_response = requests.post(test_url, data=test_data)
        if test_response.status_code == 200:
            print(f"✓ Test message sent successfully!")
            return True
        else:
            print(f"✗ Failed to send test message: Status code {test_response.status_code}")
            print(f"Response: {test_response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception sending test message: {e}")
        return False

if __name__ == "__main__":
    check_telegram_connection()
