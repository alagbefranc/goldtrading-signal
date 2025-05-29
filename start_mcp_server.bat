@echo off
echo Starting MetaTrader 5 MCP Server...

:: Set paths
set MCP_SERVER_DIR=C:\Users\falagbe\CascadeProjects\mcp-metatrader5-server
set PYTHON_PATH=%PATH%

:: Change to the MCP server directory
cd /d %MCP_SERVER_DIR%

:: Start the server using uv as specified in the guide
uv run --with MetaTrader5 --with fastmcp --with numpy --with pandas --with pydantic fastmcp run %MCP_SERVER_DIR%\mt5_server.py --host 127.0.0.1 --port 8000

echo MCP Server stopped.
pause
