"""
MetaTrader 5 Integration Package
This package provides integration with MetaTrader 5 platform through the MCP Server.
"""

from .mt5_connector import MT5Connector, get_mt5_connector
from .mcp_server_manager import MCP_Server_Manager

__all__ = ['MT5Connector', 'get_mt5_connector', 'MCP_Server_Manager']
