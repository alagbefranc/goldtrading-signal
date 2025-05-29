# Installation and Deployment Guide

This guide explains how to install, configure, and deploy the ICT/SMC Forex Trading Bot.

## Prerequisites

- Python 3.7 or higher
- Telegram account
- Telegram bot token (create one using BotFather)
- MetaTrader 5 (optional, for auto-trading)

## Installation

1. **Clone or download this repository**

2. **Install required dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure your environment**
   - Copy `.env.example` to `.env`
   - Update the `.env` file with your settings:
     ```
     # Required settings
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     TELEGRAM_CHAT_ID=your_chat_id_here
     
     # Optional settings
     CURRENCY_PAIR=XAUUSD
     TIMEZONE=your_timezone  # e.g., US/Eastern, Europe/London
     
     # MetaTrader 5 settings (optional)
     MT5_ENABLED=false
     MT5_ACCOUNT=your_account_number
     MT5_PASSWORD=your_password
     MT5_SERVER=your_broker_server
     MT5_AUTO_TRADE=false
     ```

## Deployment Options

### Option 1: Local Deployment

To run the bot on your local machine:

```bash
python forex_bot.py
```

### Option 2: Persistent Deployment

For a more robust deployment that keeps the bot running:

1. Run the deployment script:
   ```bash
   python deploy.py
   ```

2. This script will:
   - Start the bot
   - Monitor it and restart if it crashes
   - Log all output to `forex_bot_deployment.log`
   - Create a `start_bot.bat` file for easy startup on Windows

### Option 3: Server Deployment

To deploy on a server:

1. Copy all files to your server
2. Install the required dependencies
3. Configure your `.env` file
4. Run the deployment script:
   ```
   python deploy.py
   ```

#### Running as a Service on Linux

If you're deploying on Linux, you can create a systemd service:

1. Create a service file `/etc/systemd/system/forex-bot.service`:
   ```
   [Unit]
   Description=ICT/SMC Forex Trading Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/forex-trading-bot
   ExecStart=/usr/bin/python3 /path/to/forex-trading-bot/forex_bot.py
   Restart=on-failure
   RestartSec=5s

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start the service:
   ```
   sudo systemctl enable forex-bot.service
   sudo systemctl start forex-bot.service
   ```

3. Check status:
   ```
   sudo systemctl status forex-bot.service
   ```

## Finding Your Chat ID

1. Start a chat with your bot
2. Send any message to your bot
3. Run the following command to get your chat ID:
   ```
   python get_chat_id.py
   ```
4. Add this chat ID to your `.env` file

## Testing Your Bot

1. Send `/start` to your bot to see all available commands
2. Try `/status` to check the bot's status
3. Use `/timezone` to set your local timezone
4. Use `/invest 100` to see lot size recommendation for a $100 investment
5. Try `/signal` to generate a trading signal

## MetaTrader 5 Integration (Optional)

If you want to use automatic trading with MetaTrader 5:

1. Install MetaTrader 5 on your computer
2. Set `MT5_ENABLED=true` in your `.env` file
3. Configure your MT5 account settings in `.env`
4. Start the bot and use `/mt5start` to start the MCP Server
5. Use `/mt5connect` to connect to your MT5 account
6. Enable auto-trading with `/mt5autotrade on`

## Troubleshooting

### Bot doesn't respond
- Check if the bot is running
- Verify your Telegram bot token is correct
- Make sure your chat ID is correct

### Error connecting to MetaTrader 5
- Check if MetaTrader 5 is installed and running
- Verify your account credentials in `.env`
- Try running `/mt5start` followed by `/mt5connect`

### Bot crashes frequently
- Check the logs for error messages
- Make sure all dependencies are installed
- Try updating your Python packages with `pip install -U -r requirements.txt`
