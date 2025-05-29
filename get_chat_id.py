#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the bot token from .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def start(update, context):
    """Handle the /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    message = (
        f"👋 Hello {user.first_name}!\n\n"
        f"Your chat ID is: {chat_id}\n\n"
        "Copy this number and add it to your .env file as TELEGRAM_CHAT_ID."
    )
    update.message.reply_text(message)
    
    # Also log the chat ID to the console
    print(f"\n=== TELEGRAM CHAT ID ===")
    print(f"User: {user.first_name} {user.last_name if user.last_name else ''} (@{user.username})")
    print(f"Chat ID: {chat_id}")
    print("======================\n")

def message_handler(update, context):
    """Handle any message"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    message = (
        f"Your chat ID is: {chat_id}\n\n"
        "Copy this number and add it to your .env file as TELEGRAM_CHAT_ID."
    )
    update.message.reply_text(message)
    
    # Also log the chat ID to the console
    print(f"\n=== TELEGRAM CHAT ID ===")
    print(f"User: {user.first_name} {user.last_name if user.last_name else ''} (@{user.username})")
    print(f"Chat ID: {chat_id}")
    print("======================\n")

def main():
    """Run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: No Telegram bot token found in .env file")
        print("Make sure to add your bot token to the .env file as TELEGRAM_BOT_TOKEN")
        return
    
    print("\nStarting Chat ID Finder Bot...")
    print("Send any message to your bot on Telegram to get your chat ID")
    print("Press Ctrl+C to exit\n")
    
    # Create the Updater and pass it the bot token
    updater = Updater(TELEGRAM_BOT_TOKEN)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    
    # Register message handler for any message
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
