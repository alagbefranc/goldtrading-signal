#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User Memory and Trade History Module for Forex Trading Bot
Stores and manages user preferences, trade history, and performance metrics
"""

import os
import json
import datetime
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class UserMemory:
    """Manages user preferences, trade history and bot personalization"""
    
    def __init__(self, data_dir=None):
        """Initialize the user memory manager"""
        if data_dir is None:
            # Default to a 'data' directory in the project root
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        else:
            self.data_dir = data_dir
            
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # File paths for different data types
        self.preferences_file = os.path.join(self.data_dir, 'user_preferences.json')
        self.trade_history_file = os.path.join(self.data_dir, 'trade_history.json')
        self.conversations_file = os.path.join(self.data_dir, 'conversations.json')
        
        # Initialize data structures
        self.user_preferences = self._load_json(self.preferences_file, {})
        self.trade_history = self._load_json(self.trade_history_file, {"trades": []})
        self.conversations = self._load_json(self.conversations_file, {"topics": []})
        
        logger.info("User memory system initialized")
    
    def _load_json(self, file_path: str, default: Any) -> Any:
        """Load data from a JSON file with fallback to default"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                return default
        return default
    
    def _save_json(self, file_path: str, data: Any) -> bool:
        """Save data to a JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving to {file_path}: {e}")
            return False
    
    def save_user_preference(self, chat_id: str, key: str, value: Any) -> bool:
        """Save a user preference"""
        if chat_id not in self.user_preferences:
            self.user_preferences[chat_id] = {}
        
        self.user_preferences[chat_id][key] = value
        return self._save_json(self.preferences_file, self.user_preferences)
    
    def get_user_preference(self, chat_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        if chat_id in self.user_preferences and key in self.user_preferences[chat_id]:
            return self.user_preferences[chat_id][key]
        return default
    
    def record_trade(self, 
                    chat_id: str, 
                    signal_data: Dict,
                    result: Optional[str] = None,
                    profit_pips: Optional[float] = None,
                    notes: Optional[str] = None) -> bool:
        """
        Record a trade in the history
        
        Args:
            chat_id: User's chat ID
            signal_data: The signal data that led to this trade
            result: Optional result ("win", "loss", "break_even", "pending")
            profit_pips: Optional profit/loss in pips
            notes: Optional notes about the trade
        
        Returns:
            bool: Success or failure
        """
        # Generate a unique trade ID based on timestamp
        trade_id = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{chat_id}"
        
        # Create the trade record
        trade_record = {
            "trade_id": trade_id,
            "chat_id": chat_id,
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "signal": signal_data,
            "status": "open" if result is None else "closed",
            "result": result,
            "profit_pips": profit_pips,
            "notes": notes
        }
        
        # Add to history
        self.trade_history["trades"].append(trade_record)
        
        # Save to file
        return self._save_json(self.trade_history_file, self.trade_history)
    
    def update_trade_result(self, trade_id: str, result: str, profit_pips: float, notes: Optional[str] = None) -> bool:
        """
        Update a trade with its result
        
        Args:
            trade_id: The ID of the trade to update
            result: The result ("win", "loss", "break_even")
            profit_pips: Profit or loss in pips
            notes: Optional notes about the trade outcome
        
        Returns:
            bool: Success or failure
        """
        for trade in self.trade_history["trades"]:
            if trade["trade_id"] == trade_id:
                trade["status"] = "closed"
                trade["result"] = result
                trade["profit_pips"] = profit_pips
                if notes:
                    trade["notes"] = notes
                return self._save_json(self.trade_history_file, self.trade_history)
        
        logger.error(f"Trade ID {trade_id} not found")
        return False
    
    def get_user_stats(self, chat_id: str) -> Dict:
        """
        Get trading statistics for a user
        
        Args:
            chat_id: User's chat ID
        
        Returns:
            Dict with trading statistics
        """
        user_trades = [t for t in self.trade_history["trades"] if t["chat_id"] == chat_id]
        
        if not user_trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "biggest_win": 0.0,
                "biggest_loss": 0.0,
                "total_pips": 0.0
            }
        
        # Calculate statistics
        wins = [t for t in user_trades if t["result"] == "win"]
        losses = [t for t in user_trades if t["result"] == "loss"]
        
        win_rate = len(wins) / len(user_trades) if user_trades else 0.0
        
        win_pips = [t["profit_pips"] for t in wins if t["profit_pips"] is not None]
        loss_pips = [t["profit_pips"] for t in losses if t["profit_pips"] is not None]
        
        avg_win = sum(win_pips) / len(win_pips) if win_pips else 0.0
        avg_loss = sum(loss_pips) / len(loss_pips) if loss_pips else 0.0
        
        biggest_win = max(win_pips) if win_pips else 0.0
        biggest_loss = min(loss_pips) if loss_pips else 0.0
        
        total_pips = sum([t["profit_pips"] for t in user_trades if t["profit_pips"] is not None])
        
        return {
            "total_trades": len(user_trades),
            "win_rate": win_rate * 100,  # as percentage
            "avg_profit": avg_win,
            "avg_loss": avg_loss,
            "biggest_win": biggest_win,
            "biggest_loss": biggest_loss,
            "total_pips": total_pips
        }
    
    def get_strategy_performance(self, strategy_type: str = "ICT/SMC") -> Dict:
        """
        Get performance metrics for a specific strategy
        
        Args:
            strategy_type: The trading strategy to analyze
            
        Returns:
            Dict with strategy performance metrics
        """
        # Filter trades by strategy type
        strategy_trades = [t for t in self.trade_history["trades"] 
                         if t["signal"].get("strategy") == strategy_type 
                         and t["status"] == "closed"]
        
        if not strategy_trades:
            return {
                "strategy": strategy_type,
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_pips": 0.0,
                "performance_rating": "N/A"
            }
        
        # Calculate statistics
        wins = [t for t in strategy_trades if t["result"] == "win"]
        win_rate = len(wins) / len(strategy_trades) if strategy_trades else 0.0
        
        profit_pips = [t["profit_pips"] for t in strategy_trades if t["profit_pips"] is not None]
        avg_pips = sum(profit_pips) / len(profit_pips) if profit_pips else 0.0
        
        # Calculate a simple performance rating
        if win_rate >= 0.7 and avg_pips > 0:
            performance = "Excellent"
        elif win_rate >= 0.5 and avg_pips > 0:
            performance = "Good"
        elif win_rate >= 0.4 and avg_pips > 0:
            performance = "Average"
        else:
            performance = "Needs improvement"
        
        return {
            "strategy": strategy_type,
            "total_trades": len(strategy_trades),
            "win_rate": win_rate * 100,  # as percentage
            "avg_pips": avg_pips,
            "performance_rating": performance
        }
    
    def get_recent_trades(self, limit: int = 5) -> List[Dict]:
        """Get the most recent trades"""
        # Sort by timestamp descending and take the most recent ones
        sorted_trades = sorted(
            self.trade_history["trades"], 
            key=lambda x: x["timestamp"] if "timestamp" in x else "0", 
            reverse=True
        )
        return sorted_trades[:limit]
    
    def get_personalized_context(self, chat_id: str) -> Dict:
        """
        Get personalized context for AI conversations
        
        Args:
            chat_id: User's chat ID
            
        Returns:
            Dict with personalized context information
        """
        # Get user preferences
        user_prefs = self.user_preferences.get(chat_id, {})
        
        # Get user statistics
        stats = self.get_user_stats(chat_id)
        
        # Get recent trades
        recent_trades = [t for t in self.get_recent_trades() if t["chat_id"] == chat_id]
        
        # Get strategy performance
        strategy_perf = self.get_strategy_performance("ICT/SMC")
        
        # Construct personalized context
        context = {
            "user": {
                "preferences": user_prefs,
                "stats": stats
            },
            "recent_trades": [
                {
                    "timestamp": t["timestamp"],
                    "pair": t["signal"].get("symbol"),
                    "type": t["signal"].get("type"),
                    "result": t["result"],
                    "pips": t["profit_pips"]
                } 
                for t in recent_trades if "signal" in t
            ],
            "strategy": strategy_perf
        }
        
        return context
    
    def record_conversation_topic(self, chat_id: str, topic: str, user_message: str) -> bool:
        """Record an important conversation topic"""
        topic_record = {
            "chat_id": chat_id,
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "topic": topic,
            "message": user_message
        }
        
        self.conversations["topics"].append(topic_record)
        return self._save_json(self.conversations_file, self.conversations)
    
    def get_conversation_topics(self, chat_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversation topics for a user"""
        user_topics = [t for t in self.conversations["topics"] if t["chat_id"] == chat_id]
        sorted_topics = sorted(user_topics, key=lambda x: x["timestamp"], reverse=True)
        return sorted_topics[:limit]


# Create a singleton instance
user_memory = UserMemory()

# For example usage and testing
if __name__ == "__main__":
    # Example of recording a trade
    signal_example = {
        "symbol": "XAUUSD",
        "type": "BUY",
        "entry_price": 2350.50,
        "strategy": "ICT/SMC"
    }
    
    user_memory.record_trade("test_user", signal_example, "pending")
    
    # Add a result later
    trades = user_memory.get_recent_trades(1)
    if trades:
        user_memory.update_trade_result(
            trades[0]["trade_id"], 
            "win", 
            45.5, 
            "Trade hit take profit after 3 hours"
        )
    
    # Get statistics
    stats = user_memory.get_user_stats("test_user")
    print(f"User statistics: {stats}")
    
    # Get strategy performance
    perf = user_memory.get_strategy_performance()
    print(f"Strategy performance: {perf}")
