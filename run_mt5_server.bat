@echo off
echo Starting MetaTrader 5 MCP Server...

cd /d C:\Users\falagbe\CascadeProjects\mcp-metatrader5-server

echo Current directory: %CD%

echo Running server...
python mt5_server.py --host 127.0.0.1 --port 8000

pause
