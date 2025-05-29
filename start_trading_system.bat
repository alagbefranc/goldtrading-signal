@echo off
echo Starting the Forex Trading System with MT5 Integration...
echo.

echo Step 1: Starting the MetaTrader 5 MCP Server...
start "MT5 MCP Server" cmd /c "cd /d C:\Users\falagbe\CascadeProjects\mcp-metatrader5-server && start_mcp_server.bat"

echo Waiting for MCP Server to initialize...
timeout /t 5 /nobreak > nul

echo Step 2: Starting the Forex Trading Bot...
start "Forex Trading Bot" cmd /c "cd /d C:\Users\falagbe\CascadeProjects\forex-trading-bot && python forex_bot.py"

echo.
echo Trading system is now running!
echo - MT5 MCP Server: http://127.0.0.1:8000
echo - Make sure your MetaTrader 5 terminal is open and logged in
echo - Test the bot by sending /start in your Telegram chat
echo.
echo Press any key to close this window (bot will continue running)...
pause > nul
