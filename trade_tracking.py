#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Trade tracking and result management functions for the forex trading bot
"""

import logging
from telegram import Update
from telegram.ext import CallbackContext
import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Import user memory if available
try:
    from user_memory import user_memory
    USER_MEMORY_AVAILABLE = True
except ImportError:
    USER_MEMORY_AVAILABLE = False
    logger.warning("User memory system not available. Trade tracking disabled.")

# Import AI for analysis if available
try:
    from ai_orchestrator import ai_orchestrator
    AI_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    AI_ORCHESTRATOR_AVAILABLE = False


def trade_result_command(update: Update, context: CallbackContext):
    """
    Handle the /result command to update trade results
    Example: /result win 45 Hit take profit exactly
    Example: /result loss -20 Stopped out early
    """
    if not USER_MEMORY_AVAILABLE:
        update.message.reply_text("⚠️ Trade tracking system is not available.")
        return
    
    chat_id = str(update.effective_chat.id)
    
    # Check if arguments provided
    if not context.args or len(context.args) < 2:
        update.message.reply_text(
            "⚠️ Please provide result type and pips: /result win|loss|breakeven PIPS [notes]\n"
            "Example: /result win 45 Hit take profit exactly\n"
            "Example: /result loss -20 Stopped out early"
        )
        return
    
    # Parse arguments
    result_type = context.args[0].lower()
    
    # Validate result type
    if result_type not in ["win", "loss", "breakeven"]:
        update.message.reply_text("⚠️ Result must be 'win', 'loss', or 'breakeven'")
        return
    
    try:
        pips = float(context.args[1])
        notes = " ".join(context.args[2:]) if len(context.args) > 2 else ""
    except ValueError:
        update.message.reply_text("⚠️ Pips must be a number")
        return
    
    # Get most recent pending trade for this user
    recent_trades = user_memory.get_recent_trades(10)
    pending_trades = [t for t in recent_trades if t["chat_id"] == chat_id and t["status"] == "open"]
    
    if not pending_trades:
        update.message.reply_text("⚠️ No pending trades found to update.")
        return
    
    # Update the most recent pending trade
    trade = pending_trades[0]
    success = user_memory.update_trade_result(trade["trade_id"], result_type, pips, notes)
    
    if success:
        symbol = trade["signal"].get("symbol", "Unknown")
        trade_type = trade["signal"].get("type", "Unknown")
        
        # Get updated user stats
        stats = user_memory.get_user_stats(chat_id)
        win_rate = stats.get("win_rate", 0)
        total_pips = stats.get("total_pips", 0)
        
        update.message.reply_text(
            f"✅ Trade result recorded: {symbol} {trade_type} - {result_type.upper()} {pips} pips\n\n"
            f"📊 Your stats: {stats.get('total_trades', 0)} trades, {win_rate:.1f}% win rate, {total_pips:.1f} total pips"
        )
        
        # If this was a loss, trigger the AI to analyze what went wrong
        if result_type == "loss" and AI_ORCHESTRATOR_AVAILABLE:
            try:
                analysis_context = {
                    "trade": {
                        "symbol": symbol,
                        "type": trade_type,
                        "entry": trade["signal"].get("entry_price"),
                        "result": "loss",
                        "pips": pips
                    }
                }
                
                analysis = ai_orchestrator.process_message(
                    "Analyze why this trade failed and what could be improved next time", 
                    analysis_context
                )
                
                if analysis and analysis != "__GENERATE_TRADING_SIGNAL__":
                    update.message.reply_text(f"🧠 AI Analysis of failed trade:\n\n{analysis}")
            except Exception as e:
                logger.error(f"Error analyzing failed trade: {e}")
    else:
        update.message.reply_text("❌ Failed to update trade result. Please try again.")


def stats_command(update: Update, context: CallbackContext):
    """Handle the /stats command to view trading statistics"""
    if not USER_MEMORY_AVAILABLE:
        update.message.reply_text("⚠️ Trade tracking system is not available.")
        return
    
    chat_id = str(update.effective_chat.id)
    
    # Get user stats
    stats = user_memory.get_user_stats(chat_id)
    strategy_perf = user_memory.get_strategy_performance("ICT/SMC")
    
    # Format stats in a nice message
    if stats["total_trades"] == 0:
        update.message.reply_text("📊 No trading history found yet. Use /signal to generate trades and /result to record outcomes.")
        return
    
    win_rate = stats.get("win_rate", 0)
    total_pips = stats.get("total_pips", 0)
    biggest_win = stats.get("biggest_win", 0)
    biggest_loss = stats.get("biggest_loss", 0)
    avg_win = stats.get("avg_profit", 0)
    avg_loss = stats.get("avg_loss", 0)
    
    stats_message = f"""📊 *Your Trading Statistics* 📊

*Overall Performance:*
• Total Trades: {stats["total_trades"]}
• Win Rate: {win_rate:.1f}%
• Total Pips: {total_pips:.1f}
• Biggest Win: {biggest_win:.1f} pips
• Biggest Loss: {biggest_loss:.1f} pips
• Average Win: {avg_win:.1f} pips
• Average Loss: {avg_loss:.1f} pips

*ICT/SMC Strategy Performance:*
• Rating: {strategy_perf.get('performance_rating', 'N/A')}
• Strategy Win Rate: {strategy_perf.get('win_rate', 0):.1f}%
• Total Strategy Trades: {strategy_perf.get('total_trades', 0)}

_Use /result win|loss|breakeven PIPS to record new trade results_
_Use /analyze for personalized signal insights_"""
    
    update.message.reply_text(stats_message, parse_mode="Markdown")


def analyze_command(update: Update, context: CallbackContext):
    """Handle the /analyze command to get personalized signal insights"""
    if not USER_MEMORY_AVAILABLE:
        update.message.reply_text("⚠️ Trade tracking system is not available.")
        return
    
    # Check if AI orchestrator is available
    try:
        from ai_orchestrator import ai_orchestrator, AI_ORCHESTRATOR_AVAILABLE
        if not AI_ORCHESTRATOR_AVAILABLE:
            update.message.reply_text("⚠️ AI analysis system is not available.")
            return
    except ImportError:
        update.message.reply_text("⚠️ AI analysis system is not available.")
        return
        
    chat_id = str(update.effective_chat.id)
    
    # Send typing action to show that analysis is in progress
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Get signal performance analysis
    analysis = ai_orchestrator.analyze_signal_performance(chat_id)
    
    if "error" in analysis:
        update.message.reply_text(f"⚠️ {analysis['error']}")
        return
        
    if "message" in analysis:
        update.message.reply_text(analysis["message"])
        return
    
    # Format analysis in a nice message
    insights = "\n".join([f"• {insight}" for insight in analysis.get("insights", [])])
    if not insights:
        insights = "• Not enough trade history yet for detailed insights"
    
    buy_win_rate = analysis.get("buy_win_rate", 0)
    sell_win_rate = analysis.get("sell_win_rate", 0)
    
    analysis_message = f"""🧠 *Signal Performance Analysis* 🧠

*Based on your {analysis['total_analyzed']} recorded trades:*

*Signal Types:*
• Buy Signals: {analysis['signals']['buy']} ({buy_win_rate:.1f}% win rate)
• Sell Signals: {analysis['signals']['sell']} ({sell_win_rate:.1f}% win rate)

*Key Insights:*
{insights}

_The bot learns from your trade results to provide better signals over time_"""
    
    update.message.reply_text(analysis_message, parse_mode="Markdown")
