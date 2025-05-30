#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MT5 Dashboard - Simple web interface to test MCP Server integration
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import requests
from flask import Flask, render_template, request, jsonify

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# MCP Server URL
MCP_SERVER_URL = os.getenv("MT5_SERVER_URL", "http://127.0.0.1:8000")

# MT5 Account details
MT5_ACCOUNT = os.getenv("MT5_ACCOUNT", "210053016")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "Korede16@@")
MT5_SERVER = os.getenv("MT5_SERVER", "Exness-MT5Trial9")

def send_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Send a request to the MCP Server"""
    url = f"{MCP_SERVER_URL}/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        else:
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP Error: {response.status_code}", "message": response.text}
    
    except Exception as e:
        logger.error(f"Error sending request to {endpoint}: {e}")
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    """Render the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/server-status')
def server_status():
    """Check MCP Server status"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "running", "message": "MCP Server is running"})
        else:
            return jsonify({"status": "error", "message": f"MCP Server returned status code {response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error connecting to MCP Server: {e}"})

@app.route('/api/initialize', methods=["POST"])
def initialize_mt5():
    """Initialize MT5"""
    result = send_request("initialize", method="POST")
    return jsonify(result)

@app.route('/api/login', methods=["POST"])
def login_mt5():
    """Login to MT5"""
    data = {
        "account": MT5_ACCOUNT,
        "password": MT5_PASSWORD,
        "server": MT5_SERVER
    }
    result = send_request("login", method="POST", data=data)
    return jsonify(result)

@app.route('/api/symbols', methods=["GET"])
def get_symbols():
    """Get available symbols"""
    result = send_request("get_symbols")
    return jsonify(result)

@app.route('/api/symbol-info', methods=["POST"])
def get_symbol_info():
    """Get symbol info"""
    symbol = request.json.get("symbol", "EURUSD")
    result = send_request(f"get_symbol_info?symbol={symbol}")
    return jsonify(result)

@app.route('/api/account-info', methods=["GET"])
def get_account_info():
    """Get account info"""
    result = send_request("get_account_info")
    return jsonify(result)

@app.route('/api/positions', methods=["GET"])
def get_positions():
    """Get open positions"""
    result = send_request("positions_get")
    return jsonify(result)

@app.route('/api/shutdown', methods=["POST"])
def shutdown_mt5():
    """Shutdown MT5 connection"""
    result = send_request("shutdown", method="POST")
    return jsonify(result)

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    # Create dashboard.html template
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MT5 MCP Server Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
        }
        .status-indicator {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        .status-green {
            background-color: #28a745;
        }
        .status-red {
            background-color: #dc3545;
        }
        .status-yellow {
            background-color: #ffc107;
        }
        .card {
            margin-bottom: 20px;
        }
        pre {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">MT5 MCP Server Dashboard</h1>
        
        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <span class="status-indicator" id="server-status-indicator"></span>
                        <strong>Server Status</strong>
                    </div>
                    <div class="card-body">
                        <p id="server-status-message">Checking server status...</p>
                        <button class="btn btn-sm btn-primary" id="btn-check-status">Check Status</button>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="status-indicator" id="mt5-status-indicator"></span>
                        <strong>MT5 Connection</strong>
                    </div>
                    <div class="card-body">
                        <p id="mt5-status-message">MT5 not initialized</p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary mb-2" id="btn-initialize">Initialize MT5</button>
                            <button class="btn btn-success mb-2" id="btn-login">Login to MT5</button>
                            <button class="btn btn-danger" id="btn-shutdown">Shutdown MT5</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <ul class="nav nav-tabs" id="myTab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="account-tab" data-bs-toggle="tab" data-bs-target="#account" type="button">Account Info</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="symbols-tab" data-bs-toggle="tab" data-bs-target="#symbols" type="button">Symbols</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="positions-tab" data-bs-toggle="tab" data-bs-target="#positions" type="button">Positions</button>
                    </li>
                </ul>
                <div class="tab-content mt-3" id="myTabContent">
                    <div class="tab-pane fade show active" id="account" role="tabpanel">
                        <div class="d-flex justify-content-between mb-2">
                            <h5>Account Information</h5>
                            <button class="btn btn-sm btn-primary" id="btn-get-account">Get Account Info</button>
                        </div>
                        <pre id="account-info">No account information available</pre>
                    </div>
                    <div class="tab-pane fade" id="symbols" role="tabpanel">
                        <div class="d-flex justify-content-between mb-2">
                            <h5>Available Symbols</h5>
                            <button class="btn btn-sm btn-primary" id="btn-get-symbols">Get Symbols</button>
                        </div>
                        <pre id="symbols-list">No symbols available</pre>
                        
                        <div class="mt-4">
                            <div class="input-group mb-3">
                                <input type="text" class="form-control" id="symbol-input" placeholder="Enter symbol (e.g., EURUSD)" value="EURUSD">
                                <button class="btn btn-primary" id="btn-get-symbol-info">Get Info</button>
                            </div>
                            <pre id="symbol-info">No symbol information available</pre>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="positions" role="tabpanel">
                        <div class="d-flex justify-content-between mb-2">
                            <h5>Open Positions</h5>
                            <button class="btn btn-sm btn-primary" id="btn-get-positions">Get Positions</button>
                        </div>
                        <pre id="positions-list">No positions available</pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Helper function to make API calls
        async function apiCall(endpoint, method = 'GET', body = null) {
            try {
                const options = {
                    method,
                    headers: {}
                };
                
                if (body) {
                    options.headers['Content-Type'] = 'application/json';
                    options.body = JSON.stringify(body);
                }
                
                const response = await fetch(`/api/${endpoint}`, options);
                return await response.json();
            } catch (error) {
                console.error(`Error calling ${endpoint}:`, error);
                return { success: false, error: error.message };
            }
        }
        
        // Helper function to update status indicators
        function updateStatusIndicator(id, status) {
            const indicator = document.getElementById(id);
            indicator.className = 'status-indicator';
            
            if (status === 'success' || status === 'running') {
                indicator.classList.add('status-green');
            } else if (status === 'warning') {
                indicator.classList.add('status-yellow');
            } else {
                indicator.classList.add('status-red');
            }
        }
        
        // Helper function to format JSON
        function formatJSON(obj) {
            return JSON.stringify(obj, null, 2);
        }
        
        // Check server status
        async function checkServerStatus() {
            const statusMessage = document.getElementById('server-status-message');
            statusMessage.textContent = 'Checking server status...';
            
            const result = await apiCall('server-status');
            
            if (result.status === 'running') {
                statusMessage.textContent = 'MCP Server is running';
                updateStatusIndicator('server-status-indicator', 'success');
            } else {
                statusMessage.textContent = result.message || 'Unable to connect to MCP Server';
                updateStatusIndicator('server-status-indicator', 'error');
            }
        }
        
        // Initialize MT5
        async function initializeMT5() {
            const statusMessage = document.getElementById('mt5-status-message');
            statusMessage.textContent = 'Initializing MT5...';
            
            const result = await apiCall('initialize', 'POST');
            
            if (result.success) {
                statusMessage.textContent = 'MT5 initialized successfully';
                updateStatusIndicator('mt5-status-indicator', 'warning');
            } else {
                statusMessage.textContent = result.error || 'Failed to initialize MT5';
                updateStatusIndicator('mt5-status-indicator', 'error');
            }
        }
        
        // Login to MT5
        async function loginMT5() {
            const statusMessage = document.getElementById('mt5-status-message');
            statusMessage.textContent = 'Logging in to MT5...';
            
            const result = await apiCall('login', 'POST');
            
            if (result.success) {
                statusMessage.textContent = 'Logged in to MT5 successfully';
                updateStatusIndicator('mt5-status-indicator', 'success');
            } else {
                statusMessage.textContent = result.error || 'Failed to login to MT5';
                updateStatusIndicator('mt5-status-indicator', 'warning');
            }
        }
        
        // Shutdown MT5
        async function shutdownMT5() {
            const statusMessage = document.getElementById('mt5-status-message');
            statusMessage.textContent = 'Shutting down MT5...';
            
            const result = await apiCall('shutdown', 'POST');
            
            if (result.success) {
                statusMessage.textContent = 'MT5 connection closed';
                updateStatusIndicator('mt5-status-indicator', 'error');
            } else {
                statusMessage.textContent = result.error || 'Failed to shutdown MT5';
            }
        }
        
        // Get account info
        async function getAccountInfo() {
            const accountInfo = document.getElementById('account-info');
            accountInfo.textContent = 'Loading account information...';
            
            const result = await apiCall('account-info');
            
            if (result.success) {
                accountInfo.textContent = formatJSON(result.data);
            } else {
                accountInfo.textContent = result.error || 'Failed to get account information';
            }
        }
        
        // Get symbols
        async function getSymbols() {
            const symbolsList = document.getElementById('symbols-list');
            symbolsList.textContent = 'Loading symbols...';
            
            const result = await apiCall('symbols');
            
            if (result.success) {
                symbolsList.textContent = formatJSON(result.data);
            } else {
                symbolsList.textContent = result.error || 'Failed to get symbols';
            }
        }
        
        // Get symbol info
        async function getSymbolInfo() {
            const symbolInfo = document.getElementById('symbol-info');
            const symbol = document.getElementById('symbol-input').value;
            
            symbolInfo.textContent = `Loading information for ${symbol}...`;
            
            const result = await apiCall('symbol-info', 'POST', { symbol });
            
            if (result.success) {
                symbolInfo.textContent = formatJSON(result.data);
            } else {
                symbolInfo.textContent = result.error || `Failed to get information for ${symbol}`;
            }
        }
        
        // Get positions
        async function getPositions() {
            const positionsList = document.getElementById('positions-list');
            positionsList.textContent = 'Loading positions...';
            
            const result = await apiCall('positions');
            
            if (result.success) {
                positionsList.textContent = formatJSON(result.data);
            } else {
                positionsList.textContent = result.error || 'Failed to get positions';
            }
        }
        
        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            // Check server status on page load
            checkServerStatus();
            
            // Attach event listeners
            document.getElementById('btn-check-status').addEventListener('click', checkServerStatus);
            document.getElementById('btn-initialize').addEventListener('click', initializeMT5);
            document.getElementById('btn-login').addEventListener('click', loginMT5);
            document.getElementById('btn-shutdown').addEventListener('click', shutdownMT5);
            document.getElementById('btn-get-account').addEventListener('click', getAccountInfo);
            document.getElementById('btn-get-symbols').addEventListener('click', getSymbols);
            document.getElementById('btn-get-symbol-info').addEventListener('click', getSymbolInfo);
            document.getElementById('btn-get-positions').addEventListener('click', getPositions);
            
            // Initialize tab navigation
            const triggerTabList = [].slice.call(document.querySelectorAll('#myTab button'));
            triggerTabList.forEach(function (triggerEl) {
                const tabTrigger = new bootstrap.Tab(triggerEl);
                
                triggerEl.addEventListener('click', function (event) {
                    event.preventDefault();
                    tabTrigger.show();
                });
            });
        });
    </script>
</body>
</html>
    """
    
    with open("templates/dashboard.html", "w") as f:
        f.write(dashboard_html)
    
    # Run Flask app
    app.run(debug=True, port=5000)
