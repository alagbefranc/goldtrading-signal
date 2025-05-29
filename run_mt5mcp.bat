@echo off
echo Starting MetaTrader 5 MCP Server...

:: Set the path to the MCP server directory
set MCP_DIR=C:\Users\falagbe\CascadeProjects\mcp-metatrader5-server

:: Install dependencies if needed
echo Installing dependencies...
pip install uv MetaTrader5 fastmcp numpy pandas pydantic

:: Change to the MCP directory
cd /d %MCP_DIR%

:: Try the exact command from the guide
echo Running 'uv run mt5mcp dev'...
uv run mt5mcp dev

:: If the above fails, try the alternative command
if %ERRORLEVEL% NEQ 0 (
    echo First command failed, trying alternative approach...
    uv run --with MetaTrader5 --with fastmcp --with numpy --with pandas --with pydantic fastmcp run mt5_server.py
)

echo Server should now be running at http://127.0.0.1:8000
echo Press any key to stop the server...
pause
