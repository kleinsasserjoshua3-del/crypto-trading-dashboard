#!/usr/bin/env python3
"""
Production-Grade Risk Management System
Handles position sizing, stop-losses, drawdown protection, and circuit breakers
"""

from datetime import datetime, timedelta
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    NORMAL = "normal"

class CircuitBreakerStatus(Enum):
    ACTIVE = "active"
    LEVEL_1_TRIGGERED = "level_1_triggered"  # Daily loss hit
    LEVEL_2_TRIGGERED = "level_2_triggered"  # Drawdown 15%
    LEVEL_3_TRIGGERED = "level_3_triggered"  # Drawdown 20% - EMERGENCY
    PAUSED = "paused"

class RiskManager:
    """
    Enterprise-grade risk management system for crypto trading
    """
    
    def __init__(self, initial_capital=50.0):
        self.initial_capital = initial_capital
        self.current_balance = initial_capital
        self.peak_balance = initial_capital
        
        # Risk limits
        self.daily_loss_limit = initial_capital * 0.05  # 5% = $2.50 for $50
        self.weekly_loss_limit = initial_capital * 0.10  # 10% = $5.00 for $50
        self.max_drawdown_limit = initial_capital * 0.15  # 15% = $7.50 for $50
        self.emergency_drawdown_limit = initial_capital * 0.20  # 20% = $10.00 for $50
        
        # Position sizing
        self.max_position_size = initial_capital * 0.10  # 10% per trade
        self.max_open_positions = 5
        self.risk_per_trade = initial_capital * 0.01  # 1% per trade
        
        # Circuit breaker
        self.circuit_breaker_status = CircuitBreakerStatus.ACTIVE
        self.daily_loss = 0.0
        self.weekly_loss = 0.0
        self.trades_today = []
        self.trades_this_week = []
        
        # Alerts
        self.alerts = []
        self.last_alert_time = None
        
    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk management rules
        
        Formula: Position Size = (Capital × Risk %) / (Entry Price - Stop Loss Price)
        """
        if entry_price <= stop_loss_price:
            logger.warning("Invalid entry/stop-loss prices")
            return 0
        
        price_difference = entry_price - stop_loss_price
        position_size = self.risk_per_trade / price_difference
        
        # Cap at maximum position size
        max_size = self.max_position_size / entry_price
        position_size = min(position_size, max_size)
        
        return round(position_size, 8)
    
    def calculate_stop_loss(self, entry_price, strategy_type):
        """
        Calculate stop-loss based on strategy
        """
        stop_losses = {
            'grid': entry_price * 0.97,  # -3%
            'momentum': entry_price * 0.97,  # -3%
            'dca': entry_price * 0.95,  # -5%
            'scalping': entry_price * 0.995,  # -0.5%
            'arbitrage': entry_price * 0.99,  # -1%
        }
        return stop_losses.get(strategy_type, entry_price * 0.97)
    
    def calculate_take_profit(self, entry_price, strategy_type):
        """
        Calculate take-profit targets based on strategy
        """
        take_profits = {
            'grid': entry_price * 1.02,  # +2%
            'momentum': entry_price * 1.08,  # +8%
            'dca': entry_price * 1.03,  # +3%
            'scalping': entry_price * 1.01,  # +1%
            'arbitrage': entry_price * 1.005,  # +0.5%
        }
        return take_profits.get(strategy_type, entry_price * 1.02)
    
    def record_trade(self, trade_data):
        """
        Record a trade and update risk metrics
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': trade_data.get('symbol'),
            'side': trade_data.get('side'),  # 'buy' or 'sell'
            'entry_price': trade_data.get('entry_price'),
            'exit_price': trade_data.get('exit_price'),
            'position_size': trade_data.get('position_size'),
            'profit_loss': trade_data.get('profit_loss'),
            'strategy': trade_data.get('strategy'),
        }
        
        # Update balance
        self.current_balance += trade['profit_loss']
        
        # Track daily/weekly losses
        if trade['profit_loss'] < 0:
            self.daily_loss += abs(trade['profit_loss'])
            self.weekly_loss += abs(trade['profit_loss'])
        
        # Update peak balance for drawdown calculation
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
        
        # Add to trade history
        self.trades_today.append(trade)
        self.trades_this_week.append(trade)
        
        # Check circuit breakers
        self.check_circuit_breakers()
        
        logger.info(f"Trade recorded: {trade['symbol']} {trade['side']} - P&L: ${trade['profit_loss']:.2f}")
        
        return trade
    
    def check_circuit_breakers(self):
        """
        Check if any circuit breakers should trigger
        """
        drawdown = self.get_drawdown()
        
        # Level 3: Emergency stop (20% drawdown)
        if drawdown >= self.emergency_drawdown_limit:
            self.circuit_breaker_status = CircuitBreakerStatus.LEVEL_3_TRIGGERED
            self.add_alert("CRITICAL", "EMERGENCY STOP - 20% drawdown reached. All trading halted.")
            return
        
        # Level 2: Switch to DCA only (15% drawdown)
        if drawdown >= self.max_drawdown_limit:
            self.circuit_breaker_status = CircuitBreakerStatus.LEVEL_2_TRIGGERED
            self.add_alert("CRITICAL", "Drawdown 15% - Switching to DCA mode only")
            return
        
        # Level 1: Pause all bots (5% daily loss)
        if self.daily_loss >= self.daily_loss_limit:
            self.circuit_breaker_status = CircuitBreakerStatus.LEVEL_1_TRIGGERED
            self.add_alert("CRITICAL", f"Daily loss limit hit (${self.daily_loss:.2f}). Pausing all bots for 24 hours.")
            return
        
        # Normal operation
        self.circuit_breaker_status = CircuitBreakerStatus.ACTIVE
    
    def get_drawdown(self):
        """
        Calculate current drawdown from peak
        """
        if self.peak_balance == 0:
            return 0
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        return drawdown
    
    def get_drawdown_percentage(self):
        """
        Get drawdown as percentage
        """
        return self.get_drawdown() * 100
    
    def get_daily_loss_percentage(self):
        """
        Get daily loss as percentage of capital
        """
        return (self.daily_loss / self.initial_capital) * 100
    
    def reset_daily_limits(self):
        """
        Reset daily limits (call at 12:00 AM UTC)
        """
        self.daily_loss = 0.0
        self.trades_today = []
        logger.info("Daily limits reset")
    
    def reset_weekly_limits(self):
        """
        Reset weekly limits (call every Monday 12:00 AM UTC)
        """
        self.weekly_loss = 0.0
        self.trades_this_week = []
        logger.info("Weekly limits reset")
    
    def add_alert(self, level, message):
        """
        Add an alert to the system
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.alerts.append(alert)
        logger.warning(f"[{level}] {message}")
    
    def should_pause_trading(self):
        """
        Determine if trading should be paused
        """
        return self.circuit_breaker_status in [
            CircuitBreakerStatus.LEVEL_1_TRIGGERED,
            CircuitBreakerStatus.LEVEL_2_TRIGGERED,
            CircuitBreakerStatus.LEVEL_3_TRIGGERED,
            CircuitBreakerStatus.PAUSED
        ]
    
    def should_emergency_stop(self):
        """
        Determine if emergency stop should be triggered
        """
        return self.circuit_breaker_status == CircuitBreakerStatus.LEVEL_3_TRIGGERED
    
    def get_active_bots(self):
        """
        Determine which bots should be active based on circuit breaker status
        """
        if self.circuit_breaker_status == CircuitBreakerStatus.LEVEL_3_TRIGGERED:
            return []  # All bots stopped
        elif self.circuit_breaker_status == CircuitBreakerStatus.LEVEL_2_TRIGGERED:
            return ['dca_accumulator']  # DCA only
        elif self.circuit_breaker_status == CircuitBreakerStatus.LEVEL_1_TRIGGERED:
            return []  # All bots paused for 24 hours
        else:
            return ['adaptive_grid', 'momentum_tracker', 'dca_accumulator', 'scalp_master', 'arb_finder']
    
    def get_risk_metrics(self):
        """
        Get comprehensive risk metrics
        """
        return {
            'current_balance': round(self.current_balance, 2),
            'peak_balance': round(self.peak_balance, 2),
            'initial_capital': self.initial_capital,
            'total_profit_loss': round(self.current_balance - self.initial_capital, 2),
            'roi_percentage': round(((self.current_balance - self.initial_capital) / self.initial_capital) * 100, 2),
            'drawdown': round(self.get_drawdown_percentage(), 2),
            'daily_loss': round(self.daily_loss, 2),
            'daily_loss_percentage': round(self.get_daily_loss_percentage(), 2),
            'daily_loss_limit': round(self.daily_loss_limit, 2),
            'weekly_loss': round(self.weekly_loss, 2),
            'circuit_breaker_status': self.circuit_breaker_status.value,
            'trading_paused': self.should_pause_trading(),
            'emergency_stop': self.should_emergency_stop(),
            'active_bots': self.get_active_bots(),
            'total_trades': len(self.trades_today),
            'win_rate': self.calculate_win_rate(),
            'recent_alerts': self.alerts[-5:] if self.alerts else []
        }
    
    def calculate_win_rate(self):
        """
        Calculate win rate from today's trades
        """
        if not self.trades_today:
            return 0
        
        wins = sum(1 for t in self.trades_today if t['profit_loss'] > 0)
        return round((wins / len(self.trades_today)) * 100, 2)
    
    def to_dict(self):
        """
        Convert risk manager state to dictionary
        """
        return {
            'initial_capital': self.initial_capital,
            'current_balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'daily_loss_limit': self.daily_loss_limit,
            'weekly_loss_limit': self.weekly_loss_limit,
            'max_drawdown_limit': self.max_drawdown_limit,
            'emergency_drawdown_limit': self.emergency_drawdown_limit,
            'circuit_breaker_status': self.circuit_breaker_status.value,
            'metrics': self.get_risk_metrics()
        }


# Initialize global risk manager
risk_manager = RiskManager(initial_capital=50.0)
