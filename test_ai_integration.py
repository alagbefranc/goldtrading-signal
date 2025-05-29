#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for AI integration in the forex trading bot
"""

import os
import logging
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import AI components
from ai_integration import AIIntegration
from ai_orchestrator import ai_orchestrator

def test_openai_integration():
    """Test direct OpenAI integration"""
    logger.info("Testing OpenAI integration...")
    
    # Initialize AI integration
    ai_integration = AIIntegration()
    
    if not ai_integration.is_available:
        logger.error("OpenAI integration is not available. Check your API key.")
        return False
    
    logger.info("OpenAI integration is available. Generating test response...")
    
    # Test with a simple forex trading question
    test_message = "What are the key factors that influence gold prices?"
    response = ai_integration.generate_response(test_message)
    
    logger.info(f"Question: {test_message}")
    logger.info(f"AI Response: {response}")
    
    return True

def test_ai_orchestrator():
    """Test AI orchestrator message processing"""
    logger.info("Testing AI orchestrator message processing...")
    
    # Test with a forex analysis question
    test_message = "Can you explain how to identify a fair value gap in the market?"
    context = {
        "currency_pair": "XAUUSD",
        "timeframe": "15m"
    }
    
    response = ai_orchestrator.process_message(test_message, context)
    
    logger.info(f"Question: {test_message}")
    logger.info(f"AI Response: {response}")
    
    return True

if __name__ == "__main__":
    logger.info("Starting AI integration tests...")
    
    # Test OpenAI integration
    openai_success = test_openai_integration()
    time.sleep(2)  # Avoid rate limiting
    
    # Test AI orchestrator
    orchestrator_success = test_ai_orchestrator()
    
    # Summary
    if openai_success and orchestrator_success:
        logger.info("✅ All AI integration tests passed successfully!")
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
