#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MetaTrader 5 MCP Server Manager
This module provides functions to manage the MT5 MCP Server (start, stop, check status)
"""

import os
import sys
import time
import logging
import subprocess
import requests
from pathlib import Path
import signal
import platform
import json
from typing import Optional, Dict, Union, Tuple

logger = logging.getLogger(__name__)

class MCP_Server_Manager:
    """MetaTrader 5 MCP Server Manager class"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize the MCP Server manager
        
        Args:
            config_file (str, optional): Path to the configuration file
        """
        self.process = None
        self.server_url = "http://127.0.0.1:8000"
        self.is_running = False
        
        # Default config
        self.config = {
            "host": "127.0.0.1",
            "port": 8000,
            "mcp_server_path": "",
            "installed": False
        }
        
        # Load config if available
        self._load_config(config_file)
    
    def _load_config(self, config_file: str = None) -> None:
        """
        Load configuration from file
        
        Args:
            config_file (str, optional): Path to the configuration file
        """
        if not config_file:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, "mcp_config.json")
        
        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    
                # Update server URL
                self.server_url = f"http://{self.config['host']}:{self.config['port']}"
                logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def _save_config(self, config_file: str = None) -> None:
        """
        Save configuration to file
        
        Args:
            config_file (str, optional): Path to the configuration file
        """
        if not config_file:
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, "mcp_config.json")
        
        try:
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def is_server_installed(self) -> bool:
        """
        Check if the MCP server is installed
        
        Returns:
            bool: True if installed, False otherwise
        """
        return self.config.get("installed", False)
    
    def install_server(self) -> bool:
        """
        Install the MCP server
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the server is already installed
            if self.is_server_installed():
                logger.info("MCP server is already installed")
                return True
                
            # Create temp directory for installation
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Clone the repository
            logger.info("Cloning MCP server repository...")
            clone_cmd = ["git", "clone", "https://github.com/Qoyyuum/mcp-metatrader5-server.git", temp_dir]
            
            subprocess.run(clone_cmd, check=True)
            
            # Install dependencies
            logger.info("Installing MCP server dependencies...")
            install_cmd = ["pip", "install", "-e", temp_dir]
            
            subprocess.run(install_cmd, check=True)
            
            # Find the server.py path
            server_path = os.path.join(temp_dir, "src", "mcp_metatrader5_server", "server.py")
            
            if not os.path.exists(server_path):
                logger.error(f"Server file not found at {server_path}")
                return False
            
            # Update configuration
            self.config["mcp_server_path"] = server_path
            self.config["installed"] = True
            self._save_config()
            
            logger.info("MCP server installed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to install MCP server: {e}")
            return False
    
    def start_server(self) -> bool:
        """
        Start the MCP server
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if the server is already running
        if self._check_server_status():
            self.is_running = True
            logger.info("MCP server is already running")
            return True
        
        try:
            # Start the server using the batch file in the existing repository
            mcp_server_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "mcp-metatrader5-server")
            batch_file = os.path.join(mcp_server_dir, "run_mcp_server.bat")
            
            if not os.path.exists(batch_file):
                logger.error(f"MCP server batch file not found at {batch_file}")
                return False
                
            logger.info(f"Starting MCP server from {batch_file}")
            
            # Use different methods depending on the platform
            if platform.system() == "Windows":
                # On Windows, use start command to open a new console window
                os.system(f'start "MCP Server" /D "{mcp_server_dir}" "{batch_file}"')
                # Set process to a dummy value since we're not tracking it directly
                self.process = True
            else:
                # On other platforms, use standard subprocess.Popen
                self.process = subprocess.Popen(
                    ["bash", batch_file],
                    cwd=mcp_server_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # Wait a moment for the server to start
            logger.info("Waiting for MCP server to start...")
            for i in range(10):
                time.sleep(1)
                if self._check_server_status():
                    self.is_running = True
                    logger.info("MCP server started successfully")
                    
                    # Mark as installed since we're using existing server
                    self.config["installed"] = True
                    self._save_config()
                    
                    return True
            
            logger.error("Timed out waiting for MCP server to start")
            return False
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """
        Stop the MCP server
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_running or not self.process:
            logger.info("MCP server is not running")
            return True
        
        try:
            # Terminate the process
            if platform.system() == "Windows":
                # On Windows, use taskkill to terminate the process and its children
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)])
            else:
                # On other platforms, use kill signals
                os.kill(self.process.pid, signal.SIGTERM)
                time.sleep(1)
                if self.process.poll() is None:  # If process is still running
                    os.kill(self.process.pid, signal.SIGKILL)
            
            # Reset state
            self.process = None
            self.is_running = False
            
            logger.info("MCP server stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop MCP server: {e}")
            return False
    
    def restart_server(self) -> bool:
        """
        Restart the MCP server
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.stop_server()
        time.sleep(1)
        return self.start_server()
    
    def _check_server_status(self) -> bool:
        """
        Check if the server is responding
        
        Returns:
            bool: True if the server is responding, False otherwise
        """
        try:
            response = requests.get(f"{self.server_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def get_server_url(self) -> str:
        """
        Get the server URL
        
        Returns:
            str: Server URL
        """
        return self.server_url
