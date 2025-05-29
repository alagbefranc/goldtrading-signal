#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Deployment script for running the forex trading bot
This script helps deploy the bot so it can run continuously on a server
"""

import os
import sys
import time
import signal
import logging
import subprocess
import datetime
import threading

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='forex_bot_deployment.log'
)
logger = logging.getLogger(__name__)

# Global variables
bot_process = None
restart_count = 0
max_restarts = 5
restart_interval = 60  # seconds

def start_bot():
    """Start the forex trading bot"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(script_dir, "forex_bot.py")
    
    try:
        # Start the bot
        global bot_process
        logger.info("Starting forex trading bot...")
        bot_process = subprocess.Popen(
            [sys.executable, bot_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Start thread to monitor the output
        threading.Thread(target=monitor_output, daemon=True).start()
        
        logger.info(f"Forex trading bot started with PID {bot_process.pid}")
        print(f"Forex trading bot started with PID {bot_process.pid}")
        return True
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"Error starting bot: {e}")
        return False

def monitor_output():
    """Monitor the bot's output and log it"""
    while bot_process and bot_process.poll() is None:
        try:
            # Read output
            stdout_line = bot_process.stdout.readline()
            if stdout_line:
                logger.info(f"BOT: {stdout_line.strip()}")
            
            # Read errors
            stderr_line = bot_process.stderr.readline()
            if stderr_line:
                logger.error(f"BOT ERROR: {stderr_line.strip()}")
        except Exception as e:
            logger.error(f"Error monitoring output: {e}")
            break

def monitor_bot():
    """Monitor the bot process and restart if it crashes"""
    global restart_count, bot_process
    
    while True:
        if bot_process:
            return_code = bot_process.poll()
            if return_code is not None:
                # Bot process has terminated
                logger.warning(f"Bot process terminated with return code {return_code}")
                print(f"Bot process terminated with return code {return_code}")
                
                # Check if we should restart
                if restart_count < max_restarts:
                    restart_count += 1
                    logger.info(f"Restarting bot (attempt {restart_count}/{max_restarts})...")
                    print(f"Restarting bot (attempt {restart_count}/{max_restarts})...")
                    
                    # Wait before restarting
                    time.sleep(5)
                    start_bot()
                else:
                    logger.error(f"Maximum restart attempts ({max_restarts}) reached. Giving up.")
                    print(f"Maximum restart attempts ({max_restarts}) reached. Giving up.")
                    return False
        
        # Check every 10 seconds
        time.sleep(10)

def stop_bot(signum=None, frame=None):
    """Stop the bot process"""
    global bot_process
    
    if bot_process:
        logger.info("Stopping forex trading bot...")
        print("Stopping forex trading bot...")
        bot_process.terminate()
        
        # Wait for process to terminate
        try:
            bot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Bot did not terminate gracefully, forcing...")
            print("Bot did not terminate gracefully, forcing...")
            bot_process.kill()
        
        bot_process = None
    
    logger.info("Bot stopped")
    print("Bot stopped")

def create_startup_script():
    """Create a batch script to start the deployment"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_path = os.path.join(script_dir, "start_bot.bat")
    
    script_content = f"""@echo off
echo Starting Forex Trading Bot...
cd "{script_dir}"
python deploy.py
pause
"""
    
    with open(batch_path, "w") as f:
        f.write(script_content)
    
    logger.info(f"Created startup script: {batch_path}")
    print(f"Created startup script: {batch_path}")

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, stop_bot)
    signal.signal(signal.SIGTERM, stop_bot)
    
    # Create startup script
    create_startup_script()
    
    # Start the bot
    if not start_bot():
        logger.error("Failed to start forex trading bot")
        return 1
    
    # Print instructions
    print("\n" + "="*50)
    print("Forex Trading Bot Deployment")
    print("="*50)
    print("\nYour bot is now running!")
    print(f"\nStarted at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nLogs are being written to: forex_bot_deployment.log")
    print("\nPress Ctrl+C to stop the bot")
    print("="*50 + "\n")
    
    # Monitor the bot process
    try:
        monitor_bot()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Stopping bot...")
    finally:
        stop_bot()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
