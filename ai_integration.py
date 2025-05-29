"""
AI Integration module for the forex trading bot.
This module provides integration with OpenAI and other AI services.
"""
import os
import logging
import openai
import datetime
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

# Import user memory system
try:
    from user_memory import user_memory
    USER_MEMORY_AVAILABLE = True
except ImportError:
    USER_MEMORY_AVAILABLE = False

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIIntegration:
    """
    Class for integrating with AI services like OpenAI.
    """
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_local_models = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
        self.local_model_url = os.getenv("LOCAL_MODEL_URL", "")
        
        if not self.use_local_models and self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("OpenAI integration initialized")
        elif self.use_local_models and self.local_model_url:
            logger.info(f"Local AI model integration initialized at {self.local_model_url}")
        else:
            logger.warning("No AI integration available - missing API key or local model URL")
    
    @property
    def is_available(self) -> bool:
        """Check if AI integration is available"""
        return (not self.use_local_models and bool(self.openai_api_key)) or \
               (self.use_local_models and bool(self.local_model_url))
    
    def generate_response(self, user_message: str, context: Dict[str, Any] = None, max_tokens: int = 500) -> str:
        """
        Generate a response using an available AI model
        
        Args:
            user_message: The user's message or query
            context: Additional context to help the AI generate a relevant response
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Generated response as a string
        """
        if not self.is_available:
            return "AI integration is not available. Please check your API key."
        
        try:
            if not self.use_local_models:
                return self._generate_openai_response(user_message, context, max_tokens)
            else:
                return self._generate_local_model_response(user_message, context, max_tokens)
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"Sorry, I couldn't generate a response. Error: {str(e)}"
    
    def _generate_openai_response(self, user_message: str, context: Dict[str, Any] = None, max_tokens: int = 500) -> str:
        """Generate a response using OpenAI"""
        # Base system message
        system_message = "You are an intelligent forex trading assistant that provides accurate, helpful information about trading signals and market analysis."
        
        # Enhanced personalization if user memory is available
        personalized_context = ""
        if USER_MEMORY_AVAILABLE and context and "chat_id" in context:
            chat_id = context.get("chat_id")
            user_name = context.get("user", {}).get("name", "trader")
            
            # Get personalized user context from memory system
            try:
                personal_data = user_memory.get_personalized_context(chat_id)
                
                # Extract key information for personalization
                stats = personal_data.get("user", {}).get("stats", {})
                recent_trades = personal_data.get("recent_trades", [])
                strategy_perf = personal_data.get("strategy", {})
                preferences = personal_data.get("user", {}).get("preferences", {})
                
                # Build personalized context string
                personalized_items = []
                
                # Add user preferences if available
                if preferences:
                    pref_items = []
                    for k, v in preferences.items():
                        if k == "timezone":
                            pref_items.append(f"preferred timezone: {v}")
                        elif k == "risk_percentage":
                            pref_items.append(f"risk tolerance: {v}%")
                        else:
                            pref_items.append(f"{k}: {v}")
                    
                    if pref_items:
                        personalized_items.append("User preferences: " + ", ".join(pref_items))
                
                # Add trading stats if available
                if stats and stats.get("total_trades", 0) > 0:
                    win_rate = stats.get("win_rate", 0)
                    total_pips = stats.get("total_pips", 0)
                    personalized_items.append(
                        f"Trading history: {stats.get('total_trades', 0)} trades with {win_rate:.1f}% win rate, "
                        f"total of {total_pips:.1f} pips profit/loss"
                    )
                
                # Add recent trade info if available
                if recent_trades:
                    recent_results = [f"{t['pair']} {t['type']} ({t['result']})" for t in recent_trades if "result" in t and t["result"] not in ["pending", None]]
                    if recent_results:
                        personalized_items.append(f"Recent trades: {', '.join(recent_results[:3])}")
                
                # Add strategy performance if available
                if strategy_perf and strategy_perf.get("total_trades", 0) > 0:
                    personalized_items.append(
                        f"ICT/SMC strategy performance: {strategy_perf.get('performance_rating', 'N/A')} "
                        f"({strategy_perf.get('win_rate', 0):.1f}% win rate)"
                    )
                
                # Combine all personalization elements
                if personalized_items:
                    personalized_context = "\n".join(personalized_items)
                    personalized_context = f"\n\nUser Information for {user_name}:\n" + personalized_context
                    
                # Track important topics
                if user_message and len(user_message) > 10:
                    # Determine if this is an important topic to remember
                    important_keywords = ["strategy", "preference", "risk", "target", "signal", "profit", "loss"]
                    if any(keyword in user_message.lower() for keyword in important_keywords):
                        user_memory.record_conversation_topic(chat_id, "trading_discussion", user_message)
                        
            except Exception as e:
                logger.error(f"Error getting personalized context: {e}")
        
        # Build the complete message list
        messages = [{"role": "system", "content": system_message}]
        
        # Add personalized context if available
        if personalized_context:
            messages.append({"role": "system", "content": personalized_context})
        
        # Add any additional context
        if context:
            # Format context into a clear system message
            context_filtered = {k: v for k, v in context.items() if k not in ["chat_id", "user"]}
            if context_filtered:
                context_str = "\n".join([f"{k}: {v}" for k, v in context_filtered.items()])
                messages.append({"role": "system", "content": f"Additional context:\n{context_str}"})
        
        messages.append({"role": "user", "content": user_message})
        
        # Handle different versions of the OpenAI library
        try:
            # Try the newer version first (OpenAI v1.0+)
            if hasattr(openai, 'chat') and hasattr(openai.chat, 'completions'):
                response = openai.chat.completions.create(
                    model="gpt-4-turbo-preview",  # Using a capable model for trading insights
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            # Fall back to the older version (OpenAI v0.x)
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Fallback to standard GPT-4 if turbo not available
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message['content']
        except Exception as e:
            logger.error(f"Error with OpenAI API call: {e}")
            # Try a final fallback to the very old API format
            try:
                response = openai.Completion.create(
                    engine="davinci",
                    prompt=f"System: {system_message}\n\nUser: {user_message}",
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].text.strip()
            except Exception as e2:
                logger.error(f"Error with fallback OpenAI API call: {e2}")
                raise e  # Raise the original error
    
    def _generate_local_model_response(self, user_message: str, context: Dict[str, Any] = None, max_tokens: int = 500) -> str:
        """Generate a response using a local model (implementation will depend on the local setup)"""
        # This would need to be customized based on your local model setup
        # For now, we'll just return a placeholder
        return "Local model integration is not fully implemented yet."
    
    def analyze_market_conditions(self, price_data: Dict[str, Any], timeframe: str) -> Dict[str, Any]:
        """
        Analyze market conditions using AI
        
        Args:
            price_data: Historical price data
            timeframe: The timeframe being analyzed (e.g., "1h", "4h", "daily")
            
        Returns:
            Dictionary containing market analysis
        """
        if not self.is_available:
            return {"error": "AI integration not available"}
        
        try:
            # Create a summary of the price data for the AI to analyze
            recent_prices = price_data.get("close", [])[-10:]
            price_summary = ", ".join([str(p) for p in recent_prices])
            
            prompt = f"""
            Analyze these recent price points for the {timeframe} timeframe: {price_summary}.
            
            Provide insights on:
            1. Current market structure (bullish, bearish, or ranging)
            2. Key support and resistance levels
            3. Potential price targets
            4. Overall market sentiment
            
            Format your analysis as JSON.
            """
            
            response = self.generate_response(prompt)
            
            # In a production system, you'd parse the JSON response properly
            # For simplicity, we'll just return the raw text
            return {"analysis": response}
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {"error": str(e)}
