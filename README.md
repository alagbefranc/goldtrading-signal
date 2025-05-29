# Forex Trading Bot with ICT/SMC Strategy

This bot implements a trading strategy based on Inner Circle Trader (ICT) and Smart Money Concepts (SMC) methodologies. It analyzes forex market data, identifies trading opportunities using order blocks and fair value gaps, and sends signals to a Telegram bot.

## Features

- **Trading Strategy**: ICT/SMC approach to identify high-probability setups
- **Telegram Integration**: Receive signals directly on your phone
- **Position Size Calculator**: Calculate optimal lot sizes based on your investment amount
- **Timezone Configuration**: Set your local timezone for accurate signal timing
- **Natural Language Interface**: Chat naturally with the bot without using commands
- **AI-Powered Analysis**: Advanced machine learning models enhance trading signals
- **MetaTrader 5 Integration**: Execute trades automatically in your MT5 account (optional)

## Advanced AI Capabilities

This trading bot incorporates multiple AI systems to enhance trading decisions and provide a natural user experience:

### 1. LSTM Price Prediction Model
- Deep learning neural network trained on historical price data
- Predicts future price movements and market direction
- Provides confidence levels for each prediction
- Automatically enhances trading signals with forecasting data

### 2. ML-based Signal Validation
- Machine learning model trained on successful and unsuccessful trades
- Validates trading signals before they're sent
- Analyzes patterns in order blocks and fair value gaps
- Improves signal quality by filtering out low-probability setups

### 3. Natural Language Processing
- Chat naturally with the bot using everyday language
- Ask questions about market conditions and receive intelligent responses
- Request explanations about why specific trading signals were generated
- Generate new signals through conversation

### 4. AI Orchestration
- Coordinates all AI components for comprehensive analysis
- Continuously learns from trading outcomes to improve future signals
- Combines technical analysis with AI insights for better decision making

### 5. Personalized Trading Assistant
- Remembers your preferences and trading history
- Adapts to your trading style over time
- Provides personalized insights based on your past trades
- Analyzes which signals work best for you specifically

### 6. Trade Tracking & Analysis
- Record and track your trade results with `/result` command
- View comprehensive statistics about your trading performance with `/stats`
- Get AI-powered insights about your signal patterns with `/analyze`
- Learn which time periods, signal types, and market conditions work best for your trading style

## Strategy Overview

The core ICT/SMC strategy follows these steps:
1. At 5:22 AM, mark out the 2-minute high and low
2. Drop down to the 15-second time frame and look for the first order block
3. Drop down to the 1-second time frame and enter off the first fair value gap
4. Target the opposite end with a risk-reward ratio of 1:6
5. AI components analyze and validate the signal before sending

## Lot Size Calculator

This bot includes an intelligent lot size calculator that helps you determine the appropriate position size based on:
- Your investment amount
- Your risk tolerance (configurable risk percentage)
- The specific currency pair being traded
- Stop loss distance in pips

For example, if you invest $100 with a 1% risk tolerance, the bot will calculate the exact lot size needed to risk only $1 per trade while maintaining the 1:6 risk-reward ratio.

## Setup Instructions

### Prerequisites
- Python 3.7+
- Telegram Bot (create one using BotFather on Telegram)

### Installation

1. Clone this repository or download the files
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file with your Telegram bot token and chat ID

### Getting a Telegram Bot Token
1. On Telegram, search for `@BotFather`
2. Start a chat and send `/newbot`
3. Follow the instructions to create a new bot
4. BotFather will provide your bot token, add this to your `.env` file

### Finding Your Chat ID
1. Start a chat with your bot or add it to a group
2. Send a message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `chat` object and note the `id` field, add this to your `.env` file

## Usage

Run the bot with:
```
python forex_bot.py
```

### Telegram Commands

#### General Commands
- `/start` or `/help` - Display help information
- `/signal [amount]` - Generate a trading signal immediately (optionally specify investment amount)
- `/status` - Check the bot's status
- `/invest [amount]` - Calculate recommended lot size for a specific investment amount
- `/timezone [timezone]` - View or set your timezone

#### MetaTrader 5 Commands
- `/mt5start` - Start the MetaTrader 5 MCP Server
- `/mt5connect` - Connect to your MetaTrader 5 account
- `/mt5status` - Check MetaTrader 5 connection status
- `/mt5positions` - View your open positions in MT5
- `/mt5autotrade [on/off]` - Enable/disable automatic trade execution
- `/mt5test [symbol] [volume]` - Place a test trade (e.g., `/mt5test EURUSD 0.01`)

## Customization

You can modify the following parameters in the `.env` file:

#### Trading Parameters
- `CURRENCY_PAIR` - The forex pair to trade (default: XAUUSD)
- `RISK_PERCENTAGE` - Risk percentage per trade (default: 1%)
- `DEFAULT_POSITION_SIZE` - Default position size in lots (default: 0.01)

#### Time Settings
- `TIMEZONE` - Default timezone (default: UTC)
- `STRATEGY_HOUR` - Hour to run the strategy (default: 5)
- `STRATEGY_MINUTE` - Minute to run the strategy (default: 22)

#### MetaTrader 5 Settings
- `MT5_ENABLED` - Enable/disable MT5 integration (default: false)
- `MT5_SERVER_URL` - URL of the MT5 MCP Server (default: http://127.0.0.1:8000)
- `MT5_ACCOUNT` - Your MT5 account number
- `MT5_PASSWORD` - Your MT5 account password
- `MT5_SERVER` - Your MT5 server name
- `MT5_AUTO_TRADE` - Enable/disable automatic trade execution (default: false)

## Timezone Configuration

The bot supports personalized timezone settings for each user, ensuring that trading signals are generated at the appropriate time in your local timezone.

### Setting Your Timezone

1. Use the `/timezone` command to check your current timezone and see available options

2. Set your timezone using the timezone code:
   ```
   /timezone US/Eastern
   ```

3. Common timezone options include:
   - `US/Eastern`, `US/Central`, `US/Mountain`, `US/Pacific`
   - `Europe/London`, `Europe/Paris`, `Europe/Berlin`
   - `Asia/Tokyo`, `Asia/Singapore`, `Asia/Dubai`
   - `Australia/Sydney`
   - `UTC`

When your timezone is set correctly, the strategy will run at 5:22 AM your local time.

## MetaTrader 5 Integration

This bot includes integration with MetaTrader 5 via the MCP (Model Context Protocol) Server, allowing it to automatically execute trades when signals are generated.

### Setup Instructions

1. **Install the MCP Server**
   - The bot will automatically install the server when you run the `/mt5start` command
   - You can also install it manually following the instructions at https://github.com/Qoyyuum/mcp-metatrader5-server

2. **Configure MetaTrader 5 Integration**
   - Update your `.env` file with your MT5 credentials:
     ```
     MT5_ENABLED=true
     MT5_ACCOUNT=your_account_number
     MT5_PASSWORD=your_password
     MT5_SERVER=your_server_name
     ```
   - Set `MT5_AUTO_TRADE=true` if you want signals to be automatically executed

3. **Start the MT5 MCP Server**
   - Send `/mt5start` command to your bot
   - Wait for confirmation that the server started successfully

4. **Connect to MetaTrader 5**
   - Send `/mt5connect` command to your bot
   - The bot will connect to your MT5 terminal and display account information

### Usage

1. **Check Connection Status**
   - Send `/mt5status` to check if you're connected to MT5

2. **View Open Positions**
   - Send `/mt5positions` to see all your open trades

3. **Enable/Disable Auto-Trading**
   - Send `/mt5autotrade on` to enable automatic trade execution
   - Send `/mt5autotrade off` to disable it (signals will still be sent but not executed)

4. **Test with a Small Order**
   - Send `/mt5test EURUSD 0.01` to place a test trade (0.01 lot BUY order for EURUSD)

When auto-trading is enabled, the bot will automatically execute trades in your MetaTrader 5 account when it identifies a trading opportunity.

### Investment-Based Position Sizing

To calculate the appropriate lot size for your investment amount:

1. Use the `/invest` command in Telegram with your investment amount
   ```
   /invest 100
   ```
   The bot will return the recommended lot size along with potential profit/loss calculations

2. When requesting a signal, you can also include your investment amount
   ```
   /signal 100
   ```
   This will generate a signal with a position size calibrated to your investment

## Disclaimer

This bot is provided for educational purposes only. Trading forex involves significant risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always conduct your own research and consult with a qualified financial advisor before making any investment decisions.
