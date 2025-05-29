#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Deployment script for running the forex trading bot with ngrok
This script helps deploy the bot so it can run continuously on a server
"""

import os
import sys
import time
import signal
import logging
import subprocess
import requests
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
ngrok_process = None
bot_process = None

def download_ngrok():
    """Download ngrok if not already available"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ngrok_path = os.path.join(script_dir, "ngrok.exe")
    
    if os.path.exists(ngrok_path):
        logger.info("ngrok already downloaded")
        return ngrok_path
    
    logger.info("Downloading ngrok...")
    try:
        # Download ngrok
        ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        response = requests.get(ngrok_url)
        
        # Save the zip file
        zip_path = os.path.join(script_dir, "ngrok.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        
        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(script_dir)
        
        # Remove the zip file
        os.remove(zip_path)
        
        logger.info(f"ngrok downloaded to {ngrok_path}")
        return ngrok_path
    except Exception as e:
        logger.error(f"Error downloading ngrok: {e}")
        return None

def start_ngrok(port=8080, auth_token=None):
    """Start ngrok to create a tunnel to the given port"""
    ngrok_path = download_ngrok()
    if not ngrok_path:
        logger.error("Failed to find or download ngrok")
        return None
    
    try:
        # Start ngrok
        cmd = [ngrok_path, "http", str(port)]
        
        # Add auth token if provided
        if auth_token:
            subprocess.run([ngrok_path, "authtoken", auth_token], check=True)
        
        # Start ngrok in the background
        global ngrok_process
        ngrok_process = subprocess.Popen(cmd)
        
        # Wait for ngrok to start
        time.sleep(2)
        
        # Get the public URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = response.json()["tunnels"]
            if tunnels:
                public_url = tunnels[0]["public_url"]
                logger.info(f"ngrok tunnel established: {public_url}")
                return public_url
        except:
            pass
        
        logger.info("ngrok started, but couldn't get public URL")
        return "Check http://localhost:4040 for the URL"
    except Exception as e:
        logger.error(f"Error starting ngrok: {e}")
        return None

def start_bot():
    """Start the forex trading bot"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(script_dir, "forex_bot.py")
    
    try:
        # Start the bot
        global bot_process
        bot_process = subprocess.Popen([sys.executable, bot_script])
        logger.info("Forex trading bot started")
        return True
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return False

def stop_all(signum=None, frame=None):
    """Stop all processes"""
    global ngrok_process, bot_process
    
    if bot_process:
        logger.info("Stopping forex trading bot...")
        bot_process.terminate()
        bot_process = None
    
    if ngrok_process:
        logger.info("Stopping ngrok...")
        ngrok_process.terminate()
        ngrok_process = None
    
    logger.info("All processes stopped")
    sys.exit(0)

def create_startup_script():
    """Create a batch script to start the deployment"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_path = os.path.join(script_dir, "start_bot.bat")
    
    script_content = f"""@echo off
echo Starting Forex Trading Bot with ngrok...
cd "{script_dir}"
python deploy_with_ngrok.py
pause
"""
    
    with open(batch_path, "w") as f:
        f.write(script_content)
    
    logger.info(f"Created startup script: {batch_path}")

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, stop_all)
    signal.signal(signal.SIGTERM, stop_all)
    
    # Create startup script
    create_startup_script()
    
    # Ask for ngrok auth token
    auth_token = input("Enter your ngrok auth token (leave empty if none): ").strip()
    
    # Start the bot
    logger.info("Starting forex trading bot...")
    if not start_bot():
        logger.error("Failed to start forex trading bot")
        return
    
    # Start ngrok
    logger.info("Starting ngrok...")
    public_url = start_ngrok(auth_token=auth_token if auth_token else None)
    if not public_url:
        logger.error("Failed to start ngrok")
        stop_all()
        return
    
    # Print instructions
    print("\n" + "="*50)
    print("Forex Trading Bot with ngrok Deployment")
    print("="*50)
    print(f"\nPublic URL: {public_url}")
    print("\nYour bot is now accessible from anywhere!")
    print("\nTo access the ngrok web interface: http://localhost:4040")
    print("\nPress Ctrl+C to stop all processes")
    print("="*50 + "\n")
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()

if __name__ == "__main__":
    main()
