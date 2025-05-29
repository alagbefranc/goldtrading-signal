@echo off
echo Starting MetaTrader 5 MCP Server directly with Python...

:: Set the path to the MCP server directory
set MCP_DIR=C:\Users\falagbe\CascadeProjects\mcp-metatrader5-server

:: Make sure MT5 terminal is running first
echo Checking if MetaTrader 5 terminal is running...
tasklist /FI "IMAGENAME eq terminal64.exe" 2>NUL | find /I /N "terminal64.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo WARNING: MetaTrader 5 terminal does not appear to be running.
    echo Please start your MetaTrader 5 terminal before starting the MCP server.
    echo Press any key to continue anyway...
    pause > nul
)

:: Change to the MCP directory
cd /d %MCP_DIR%

:: Kill any existing processes on port 8000
echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Found process: %%a
    taskkill /F /PID %%a 2>NUL
    echo Process terminated.
)

:: Run the server directly using Python
echo Running MCP server using Python...
python mt5_server.py --host 127.0.0.1 --port 8000

echo.
echo If you see this message, the server has stopped.
echo.
pause
