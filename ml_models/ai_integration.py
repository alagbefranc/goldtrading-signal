#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Integration Module for Forex Trading Bot
Handles communication with external AI API services
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class AIIntegration:
    """Handles integration with external AI APIs for natural language processing"""
    
    def __init__(self):
        """Initialize AI integration with API keys and configuration"""
        # API configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.use_openai = self.openai_api_key != ""
        
        # Alternative free model options
        self.use_local_models = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
        self.local_model_url = os.getenv("LOCAL_MODEL_URL", "http://localhost:8000/v1/completions")
        
        # Conversation memory
        self.conversation_history = []
        self.max_history = 10  # Max number of exchanges to remember
        
        logger.info(f"AI Integration initialized with OpenAI: {self.use_openai}, Local models: {self.use_local_models}")
    
    def generate_response(self, 
                          user_message: str, 
                          context: Dict[str, Any] = None, 
                          max_tokens: int = 500) -> str:
        """
        Generate a response to user message using available AI services
        
        Args:
            user_message: Message from the user
            context: Additional context information (market data, signals, etc.)
            max_tokens: Maximum length of response
            
        Returns:
            AI-generated response text
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history * 2:  # *2 because each exchange has user+assistant
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
        
        # Prepare system prompt with trading context
        system_prompt = self._prepare_system_prompt(context)
        
        # Try OpenAI API first if available
        response = ""
        if self.use_openai:
            response = self._call_openai_api(system_prompt, max_tokens)
        
        # Fall back to local model if OpenAI failed or not configured
        if not response and self.use_local_models:
            response = self._call_local_model_api(system_prompt, max_tokens)
            
        # Fall back to rule-based responses if all AI fails
        if not response:
            response = self._generate_rule_based_response(user_message, context)
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _prepare_system_prompt(self, context: Optional[Dict[str, Any]]) -> str:
        """
        Prepare system prompt with relevant trading context
        
        Args:
            context: Dictionary containing trading context information
            
        Returns:
            System prompt string with context
        """
        # Base system prompt
        system_prompt = """You are an advanced forex trading assistant with expertise in ICT (Inner Circle Trader) and SMC (Smart Money Concepts) trading strategies.
Your purpose is to explain trading signals, market analysis, and answer user questions in a helpful, educational way.
You should be conversational but focused on providing valuable trading insights."""
        
        # Add signal context if available
        if context and "last_signal" in context:
            signal = context["last_signal"]
            system_prompt += f"\n\nRecent signal information:\n"
            system_prompt += f"Type: {signal.get('type', 'unknown').upper()} "
            system_prompt += f"Symbol: {signal.get('symbol', 'unknown')} "
            system_prompt += f"Entry: {signal.get('entry_price', 0)} "
            system_prompt += f"Stop Loss: {signal.get('stop_loss', 0)} "
            system_prompt += f"Take Profit: {signal.get('take_profit', 0)}"
        
        # Add market prediction if available
        if context and "market_prediction" in context:
            pred = context["market_prediction"]
            system_prompt += f"\n\nAI price prediction:\n"
            system_prompt += f"Direction: {pred.get('direction', 'unknown')} "
            system_prompt += f"Confidence: {pred.get('confidence', 0)}% "
            system_prompt += f"Current: {pred.get('current_price', 0)} "
            system_prompt += f"Predicted: {pred.get('predicted_price', 0)}"
        
        return system_prompt
    
    def _call_openai_api(self, system_prompt: str, max_tokens: int) -> str:
        """
        Call the OpenAI API to generate a response
        
        Args:
            system_prompt: System prompt with context
            max_tokens: Maximum response length
            
        Returns:
            Generated response or empty string if failed
        """
        if not self.openai_api_key:
            return ""
            
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history)
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ""
    
    def _call_local_model_api(self, system_prompt: str, max_tokens: int) -> str:
        """
        Call a local or alternative API model for response generation
        
        Args:
            system_prompt: System prompt with context
            max_tokens: Maximum response length
            
        Returns:
            Generated response or empty string if failed
        """
        try:
            # Prepare messages including history
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history)
            
            # Format for API request
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            # Make API request
            response = requests.post(
                self.local_model_url,
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("text", "")
            else:
                logger.error(f"Local model API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Local model API error: {e}")
            return ""
    
    def _generate_rule_based_response(self, user_message: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Generate a rule-based response when AI services are unavailable
        
        Args:
            user_message: User's message text
            context: Trading context information
            
        Returns:
            Rule-based response text
        """
        user_message = user_message.lower()
        
        # Simple keyword matching
        if any(word in user_message for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your forex trading assistant. How can I help you today?"
            
        elif any(word in user_message for word in ["signal", "trade", "recommendation"]):
            if context and "last_signal" in context:
                signal = context["last_signal"]
                return f"My latest trading signal is a {signal.get('type', '').upper()} for {signal.get('symbol', '')} at {signal.get('entry_price', 0)}."
            else:
                return "I don't have any recent trading signals to share. Would you like me to generate one?"
                
        elif any(word in user_message for word in ["explain", "why", "how", "analysis"]):
            return "My analysis is based on ICT/SMC principles, focusing on order blocks and fair value gaps. These are areas where institutional traders are likely to place orders, creating trading opportunities."
            
        elif any(word in user_message for word in ["thanks", "thank you"]):
            return "You're welcome! Let me know if you need anything else."
            
        else:
            return "I can help you understand market conditions, explain trading signals, or generate new signals for you. What would you like to know?"

# Create singleton instance
ai_integration = AIIntegration()
