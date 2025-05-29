#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Conversation module for Forex Trading Bot
Handles natural language understanding and dialog capabilities
"""

import re
import logging
import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ConversationAI:
    """Handles conversational capabilities for the trading bot"""
    
    def __init__(self):
        """Initialize the conversation engine"""
        self.last_signals = []  # Store recent signals for context
        self.max_signals = 5  # Maximum number of stored signals
    
    def add_signal(self, signal_data: Dict):
        """Add a new signal to context memory"""
        self.last_signals.append({
            "time": datetime.datetime.now(),
            "data": signal_data
        })
        
        # Keep only the most recent signals
        if len(self.last_signals) > self.max_signals:
            self.last_signals.pop(0)
    
    def process_message(self, message: str, user_data: Optional[Dict] = None) -> str:
        """Process user message and generate appropriate response"""
        message = message.lower().strip()
        
        # Check for different message intents
        if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
            return self._handle_greeting(user_data)
            
        elif any(word in message for word in ["why", "explain", "reason", "analysis"]):
            return self._handle_explanation_request(message)
            
        elif any(word in message for word in ["market", "trend", "outlook", "forecast"]):
            return self._handle_market_question(message)
            
        elif any(word in message for word in ["signal", "trade", "position", "buy", "sell"]):
            return self._handle_signal_question(message)
            
        # Default response if no intent is matched
        return "I'm your trading assistant. You can ask me about recent signals, market trends, or why a particular trading decision was made."
    
    def _handle_greeting(self, user_data: Optional[Dict] = None) -> str:
        """Handle user greeting"""
        current_hour = datetime.datetime.now().hour
        
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
            
        user_name = user_data.get("name", "") if user_data else ""
        if user_name:
            greeting += f", {user_name}"
            
        return f"{greeting}! I'm your ICT/SMC trading assistant. How can I help you today?"
    
    def _handle_explanation_request(self, message: str) -> str:
        """Explain trading decisions"""
        if not self.last_signals:
            return "I haven't generated any trading signals recently to explain."
            
        latest_signal = self.last_signals[-1]["data"]
        signal_type = latest_signal.get("type", "").upper()
        symbol = latest_signal.get("symbol", "")
        
        explanation = f"My last {signal_type} signal for {symbol} was based on ICT/SMC strategy:\n\n"
        explanation += "1. I identified order blocks where institutional smart money operates\n"
        explanation += "2. Located a fair value gap showing supply/demand imbalance\n"
        
        if signal_type == "BUY":
            explanation += "3. Found a bullish order block above price with a bullish fair value gap\n"
            explanation += "4. This suggests upward price movement is likely"
        else:
            explanation += "3. Found a bearish order block below price with a bearish fair value gap\n"
            explanation += "4. This suggests downward price movement is likely"
            
        return explanation
    
    def _handle_market_question(self, message: str) -> str:
        """Answer questions about market outlook"""
        if not self.last_signals:
            return "I need to analyze more market data before providing an outlook."
            
        # Count recent bullish vs bearish signals
        bullish_count = sum(1 for signal in self.last_signals if signal["data"].get("type", "").upper() == "BUY")
        bearish_count = len(self.last_signals) - bullish_count
        
        if bullish_count > bearish_count:
            sentiment = "bullish"
            reason = "identified more buying opportunities than selling opportunities"
        elif bearish_count > bullish_count:
            sentiment = "bearish" 
            reason = "identified more selling opportunities than buying opportunities"
        else:
            sentiment = "neutral"
            reason = "observed an equal number of buying and selling opportunities"
            
        return f"Based on recent signals, my market outlook is {sentiment} as I've {reason}. This is based on order blocks and fair value gaps in the price structure."
    
    def _handle_signal_question(self, message: str) -> str:
        """Answer questions about trading signals"""
        if not self.last_signals:
            return "I haven't generated any trading signals recently."
            
        latest_signal = self.last_signals[-1]["data"]
        signal_time = self.last_signals[-1]["time"].strftime("%Y-%m-%d %H:%M:%S")
        signal_type = latest_signal.get("type", "").upper()
        symbol = latest_signal.get("symbol", "")
        entry = latest_signal.get("entry_price", 0)
        sl = latest_signal.get("stop_loss", 0)
        tp = latest_signal.get("take_profit", 0)
        rr = latest_signal.get("rr_ratio", 0)
        
        response = f"The most recent signal was a {signal_type} on {symbol} generated at {signal_time}.\n"
        response += f"Entry: {entry:.5f}, Stop Loss: {sl:.5f}, Take Profit: {tp:.5f}\n"
        response += f"Risk-Reward Ratio: 1:{rr:.2f}"
        
        return response

# Singleton instance
conversation_ai = ConversationAI()
