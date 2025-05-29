#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Orchestrator for Forex Trading Bot
Coordinates all AI components for enhanced trading capabilities
"""

import os
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import datetime

# Import AI components with error handling
try:
    from ml_models.price_predictor import price_predictor
    PRICE_PREDICTOR_AVAILABLE = True
except ImportError:
    PRICE_PREDICTOR_AVAILABLE = False

try:
    from ml_models.signal_validator import signal_validator
    SIGNAL_VALIDATOR_AVAILABLE = True
except ImportError:
    SIGNAL_VALIDATOR_AVAILABLE = False

try:
    from ai_integration import AIIntegration
    AI_INTEGRATION_AVAILABLE = True
except ImportError:
    AI_INTEGRATION_AVAILABLE = False
    
# Import user memory system
try:
    from user_memory import user_memory
    USER_MEMORY_AVAILABLE = True
except ImportError:
    USER_MEMORY_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Coordinates all AI components of the trading bot for enhanced decision making
    """
    
    def __init__(self):
        """Initialize the AI Orchestrator"""
        logger.info("Initializing AI Orchestrator")
        
        # Check available components
        logger.info(f"Price Predictor available: {PRICE_PREDICTOR_AVAILABLE}")
        logger.info(f"Signal Validator available: {SIGNAL_VALIDATOR_AVAILABLE}")
        logger.info(f"AI Integration available: {AI_INTEGRATION_AVAILABLE}")
        
        # Set up requirements for each component
        self.tensorflow_required = PRICE_PREDICTOR_AVAILABLE
        self.sklearn_required = SIGNAL_VALIDATOR_AVAILABLE
        self.openai_required = AI_INTEGRATION_AVAILABLE
        
        # Install required packages if not available
        self._check_and_install_requirements()
        
        # Initialize AI Integration
        if AI_INTEGRATION_AVAILABLE:
            self.ai_integration = AIIntegration()
            logger.info(f"AI Integration initialized and is available: {self.ai_integration.is_available}")
        
        # Training data storage
        self.historical_signals = []
    
    def _check_and_install_requirements(self):
        """Check and install required packages"""
        try:
            import pip
            
            # Attempt to install TensorFlow if not available and required
            if self.tensorflow_required:
                try:
                    import tensorflow
                except ImportError:
                    logger.info("Installing TensorFlow...")
                    pip.main(['install', 'tensorflow'])
            
            # Attempt to install scikit-learn if not available and required
            if self.sklearn_required:
                try:
                    import sklearn
                except ImportError:
                    logger.info("Installing scikit-learn...")
                    pip.main(['install', 'scikit-learn'])
            
            # Attempt to install OpenAI if not available and required
            if self.openai_required:
                try:
                    import openai
                except ImportError:
                    logger.info("Installing OpenAI...")
                    pip.main(['install', 'openai'])
        
        except Exception as e:
            logger.error(f"Error installing requirements: {e}")
    
    def enhance_signal(self, 
                      signal: Dict,
                      data: pd.DataFrame,
                      order_blocks: List[Dict],
                      fair_value_gaps: List[Dict]) -> Dict:
        """
        Enhance a trading signal with AI-powered insights
        
        Args:
            signal: Original trading signal
            data: Historical OHLCV data
            order_blocks: Detected order blocks
            fair_value_gaps: Detected fair value gaps
            
        Returns:
            Enhanced signal with AI insights
        """
        enhanced_signal = signal.copy()
        
        # Step 1: Use Price Predictor to forecast future price
        if PRICE_PREDICTOR_AVAILABLE:
            try:
                price_prediction = price_predictor.predict(data)
                if price_prediction:
                    enhanced_signal["price_prediction"] = price_prediction
                    
                    # Log prediction results
                    direction = price_prediction.get("direction", "unknown")
                    confidence = price_prediction.get("confidence", 0)
                    logger.info(f"Price prediction: {direction} with {confidence}% confidence")
            except Exception as e:
                logger.error(f"Error making price prediction: {e}")
        
        # Step 2: Validate signal with ML model
        if SIGNAL_VALIDATOR_AVAILABLE:
            try:
                validation_result = signal_validator.validate_signal(
                    data,
                    order_blocks,
                    fair_value_gaps,
                    signal.get("type", "")
                )
                if validation_result:
                    enhanced_signal["validation"] = validation_result
                    
                    # Log validation results
                    valid = validation_result.get("valid", False)
                    confidence = validation_result.get("confidence", 0)
                    reason = validation_result.get("reason", "")
                    logger.info(f"Signal validation: {valid} with {confidence} confidence. Reason: {reason}")
                    
                    # Store signal for future training if we get outcome feedback
                    self._store_signal_for_training(signal, data, order_blocks, fair_value_gaps)
            except Exception as e:
                logger.error(f"Error validating signal: {e}")
        
        return enhanced_signal
    
    def process_message(self, user_message: str, context: Dict = None) -> str:
        """
        Process a user message and generate an AI-powered response
        
        Args:
            user_message: Message from the user
            context: Trading context information
            
        Returns:
            AI-generated response
        """
        # Default response
        response = "I'm sorry, but AI assistance is not available at the moment."
        
        # Enhance context with user memory if available
        enhanced_context = context.copy() if context else {}
        
        if USER_MEMORY_AVAILABLE and context and "chat_id" in context:
            try:
                chat_id = context["chat_id"]
                
                # Get personalized user context
                personal_data = user_memory.get_personalized_context(chat_id)
                if personal_data:
                    # Add to context
                    enhanced_context["user_data"] = personal_data
                    
                    # Add recent trades to context if available
                    if "recent_trades" in personal_data:
                        enhanced_context["recent_trades"] = personal_data["recent_trades"]
                    
                    # Record this conversation for future reference
                    user_memory.record_conversation_topic(chat_id, "ai_conversation", user_message)
                    
                    logger.info(f"Enhanced context with user memory for chat_id {chat_id}")
            except Exception as e:
                logger.error(f"Error enhancing context with user memory: {e}")
        
        # Look for signal requests in natural language
        signal_keywords = [
            "signal", "trade", "buy", "sell", "long", "short", 
            "entry", "position", "setup", "opportunity"
        ]
        
        # If message contains signal keywords, check if it's a signal request
        if any(keyword in user_message.lower() for keyword in signal_keywords):
            # Check if this is clearly asking for a signal or just discussing signals in general
            signal_request_phrases = [
                "give me", "generate", "create", "get", "find", "looking for", 
                "need a", "want a", "provide", "show me", "what is"
            ]
            
            if any(phrase in user_message.lower() for phrase in signal_request_phrases):
                # If user memory is available, record this as a signal request
                if USER_MEMORY_AVAILABLE and context and "chat_id" in context:
                    try:
                        chat_id = context["chat_id"]
                        user_memory.record_conversation_topic(chat_id, "signal_request", user_message)
                    except Exception as e:
                        logger.error(f"Error recording signal request: {e}")
                
                return "__GENERATE_TRADING_SIGNAL__"
        
        # Use AI Integration if available
        if AI_INTEGRATION_AVAILABLE and self.ai_integration.is_available:
            try:
                # Pass the enhanced context with user memory data
                response = self.ai_integration.generate_response(user_message, enhanced_context)
                
                # Check if the response mentions a specific strategy or analysis
                strategy_keywords = ["ict", "smart money", "order block", "fair value gap", "liquidity"]
                if USER_MEMORY_AVAILABLE and context and "chat_id" in context:
                    if any(keyword in response.lower() for keyword in strategy_keywords):
                        try:
                            # Record that we provided strategy information
                            chat_id = context["chat_id"]
                            user_memory.record_conversation_topic(chat_id, "strategy_explanation", 
                                                              f"Bot explained: {user_message}")
                        except Exception as e:
                            logger.error(f"Error recording strategy explanation: {e}")
                            
            except Exception as e:
                logger.error(f"Error generating AI response: {e}")
                response = f"There was an error generating a response. Please try again later."
        
        return response
    
    def _store_signal_for_training(self, 
                                  signal: Dict,
                                  data: pd.DataFrame,
                                  order_blocks: List[Dict], 
                                  fair_value_gaps: List[Dict]):
        """
        Store signal information for future model training
        
        Args:
            signal: Trading signal
            data: OHLCV data
            order_blocks: Detected order blocks
            fair_value_gaps: Detected fair value gaps
        """
        self.historical_signals.append({
            "time": datetime.datetime.now(),
            "signal": signal,
            "data": data,
            "order_blocks": order_blocks,
            "fair_value_gaps": fair_value_gaps,
            "outcome": None  # To be filled later when we know if signal was successful
        })
        
        # Keep only the most recent 100 signals
        if len(self.historical_signals) > 100:
            self.historical_signals.pop(0)
    
    def record_signal_outcome(self, signal_time: datetime.datetime, successful: bool):
        """
        Record whether a previous signal was successful
        
        Args:
            signal_time: Timestamp of the original signal
            successful: Whether the signal led to a successful trade
        """
        # Find the signal in historical records
        for record in self.historical_signals:
            if abs((record["time"] - signal_time).total_seconds()) < 60:  # Within a minute
                record["outcome"] = successful
                logger.info(f"Recorded outcome for signal: {successful}")
                
                # If we have enough signals with outcomes, train the model
                if sum(1 for r in self.historical_signals if r.get("outcome") is not None) >= 5:
                    self._train_validator_with_historical_data()
                    
                break
    
    def analyze_signal_performance(self, chat_id: str) -> Dict[str, Any]:
        """
        Analyze signal performance and provide insights based on past signals
        
        Args:
            chat_id: User chat ID to analyze
            
        Returns:
            Dict containing analysis results
        """
        if not USER_MEMORY_AVAILABLE:
            return {"error": "User memory system not available"}
        
        try:
            # Get user's trade history
            user_trades = user_memory.get_user_trades(chat_id, limit=20)
            completed_trades = [t for t in user_trades if t.get("status") in ["win", "loss", "breakeven"]]
            
            if not completed_trades:
                return {"message": "Not enough trade history to analyze performance"}
            
            # Basic statistics
            analysis = {
                "total_analyzed": len(completed_trades),
                "signals": {
                    "buy": len([t for t in completed_trades if t.get("signal", {}).get("type") == "BUY"]),
                    "sell": len([t for t in completed_trades if t.get("signal", {}).get("type") == "SELL"])
                },
                "outcomes": {
                    "win": len([t for t in completed_trades if t.get("status") == "win"]),
                    "loss": len([t for t in completed_trades if t.get("status") == "loss"]),
                    "breakeven": len([t for t in completed_trades if t.get("status") == "breakeven"])
                },
                "insights": []
            }
            
            # Calculate win rates by signal type
            buy_signals = [t for t in completed_trades if t.get("signal", {}).get("type") == "BUY"]
            if buy_signals:
                buy_wins = len([t for t in buy_signals if t.get("status") == "win"])
                buy_win_rate = (buy_wins / len(buy_signals)) * 100
                analysis["buy_win_rate"] = buy_win_rate
            
            sell_signals = [t for t in completed_trades if t.get("signal", {}).get("type") == "SELL"]
            if sell_signals:
                sell_wins = len([t for t in sell_signals if t.get("status") == "win"])
                sell_win_rate = (sell_wins / len(sell_signals)) * 100
                analysis["sell_win_rate"] = sell_win_rate
            
            # Generate insights based on the data
            if "buy_win_rate" in analysis and "sell_win_rate" in analysis:
                if analysis["buy_win_rate"] > analysis["sell_win_rate"] + 15:
                    analysis["insights"].append("Buy signals have been significantly more successful than sell signals")
                elif analysis["sell_win_rate"] > analysis["buy_win_rate"] + 15:
                    analysis["insights"].append("Sell signals have been significantly more successful than buy signals")
            
            # Check for patterns in time of day
            morning_signals = [t for t in completed_trades if "time" in t.get("signal", {}) and 
                               (datetime.datetime.fromisoformat(t["signal"]["time"]).hour < 12)]
            
            if morning_signals:
                morning_wins = len([t for t in morning_signals if t.get("status") == "win"])
                morning_win_rate = (morning_wins / len(morning_signals)) * 100
                
                afternoon_signals = [t for t in completed_trades if "time" in t.get("signal", {}) and 
                                    (datetime.datetime.fromisoformat(t["signal"]["time"]).hour >= 12)]
                
                if afternoon_signals:
                    afternoon_wins = len([t for t in afternoon_signals if t.get("status") == "win"])
                    afternoon_win_rate = (afternoon_wins / len(afternoon_signals)) * 100
                    
                    if abs(morning_win_rate - afternoon_win_rate) > 20:
                        better_time = "morning" if morning_win_rate > afternoon_win_rate else "afternoon"
                        analysis["insights"].append(f"Signals generated in the {better_time} have been more successful")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing signal performance: {e}")
            return {"error": f"Error analyzing signal performance: {str(e)}"}
            
    def _train_validator_with_historical_data(self):
        """Train the signal validator with historical signal outcomes"""
        if SIGNAL_VALIDATOR_AVAILABLE and len(self.historical_signals) > 0:
            try:
                # Prepare training data
                training_data = []
                labels = []
                
                for record in self.historical_signals:
                    if record.get("outcome") is not None:
                        training_data.append({
                            "data": record.get("data"),
                            "order_blocks": record.get("order_blocks"),
                            "fvgs": record.get("fair_value_gaps")
                        })
                        labels.append(1 if record["outcome"] else 0)
                
                if training_data and labels:
                    # Train the validator
                    metrics = signal_validator.train(training_data, labels)
                    logger.info(f"Signal validator trained with metrics: {metrics}")
            except Exception as e:
                logger.error(f"Error training signal validator: {e}")

# Create singleton instance
ai_orchestrator = AIOrchestrator()
