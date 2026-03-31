#!/usr/bin/env python3
"""
Configuration Management
Centralized configuration for the trading system
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """
    Application configuration
    """
    
    # ========== KRAKEN API ==========
    KRAKEN_API_KEY = os.environ.get('KRAKEN_API_KEY', '')
    KRAKEN_PRIVATE_KEY = os.environ.get('KRAKEN_PRIVATE_KEY', '')
    
    # ========== TRADING PARAMETERS ==========
    INITIAL_CAPITAL = float(os.environ.get('INITIAL_CAPITAL', 50.0))
    
    # Risk management
    DAILY_LOSS_LIMIT_PCT = 5.0  # 5% of capital
    WEEKLY_LOSS_LIMIT_PCT = 10.0  # 10% of capital
    MAX_DRAWDOWN_PCT = 15.0  # 15% of capital
    EMERGENCY_DRAWDOWN_PCT = 20.0  # 20% of capital
    
    # Position sizing
    MAX_POSITION_SIZE_PCT = 10.0  # 10% per trade
    RISK_PER_TRADE_PCT = 1.0  # 1% per trade
    MAX_OPEN_POSITIONS = 5
    
    # ========== BOT CONFIGURATION ==========
    
    # Grid Trader
    GRID_TRADER_POSITION_SIZE = 0.30
    GRID_TRADER_LEVELS = 5
    GRID_TRADER_PROFIT_PER_LEVEL = 2.0
    GRID_TRADER_STOP_LOSS = -3.0
    GRID_TRADER_TAKE_PROFIT = 2.0
    
    # Momentum Tracker
    MOMENTUM_POSITION_SIZE = 0.20
    MOMENTUM_TREND_THRESHOLD = 1.5
    MOMENTUM_STOP_LOSS = -3.0
    MOMENTUM_TAKE_PROFIT = 8.0
    
    # DCA Accumulator
    DCA_POSITION_SIZE = 0.16
    DCA_BUY_INTERVAL_HOURS = 4
    DCA_STOP_LOSS = -5.0
    DCA_TAKE_PROFIT = 3.0
    
    # Scalp Master
    SCALP_POSITION_SIZE = 0.20
    SCALP_TRADE_DURATION_MIN = 15
    SCALP_PROFIT_PER_TRADE = 0.5
    SCALP_STOP_LOSS = -0.5
    SCALP_TAKE_PROFIT = 1.0
    SCALP_MAX_TRADES_PER_HOUR = 5
    
    # Arbitrage Finder
    ARB_POSITION_SIZE = 0.14
    ARB_MIN_SPREAD = 0.5
    ARB_STOP_LOSS = -1.0
    ARB_TAKE_PROFIT = 0.5
    
    # ========== TRADING PAIRS ==========
    TRADING_PAIRS = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD']
    MIN_ORDER_SIZE_USD = 10.0
    
    # ========== SYSTEM CONFIGURATION ==========
    
    # Flask
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Database
    DATABASE_PATH = 'crypto_bot.db'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_DIR = 'logs'
    
    # API Rate Limiting
    KRAKEN_RATE_LIMIT_MS = 3000  # 3 seconds between requests
    
    # ========== ALERT CONFIGURATION ==========
    
    # Alert thresholds
    ALERT_DAILY_LOSS_PCT = 3.0  # Alert at 3% daily loss
    ALERT_DRAWDOWN_PCT = 10.0  # Alert at 10% drawdown
    ALERT_WIN_RATE_LOW = 50.0  # Alert if win rate < 50%
    
    # ========== TRADING HOURS (UTC) ==========
    
    # When to run aggressive strategies
    AGGRESSIVE_HOURS = list(range(13, 21))  # 1 PM - 9 PM UTC (9 AM - 5 PM EST)
    
    # When to run conservative strategies
    CONSERVATIVE_HOURS = list(range(0, 8))  # 12 AM - 8 AM UTC
    
    # ========== PERFORMANCE TARGETS ==========
    
    TARGET_MONTHLY_ROI = 3.0  # 3% per month
    TARGET_WIN_RATE = 80.0  # 80% win rate
    TARGET_SHARPE_RATIO = 1.5
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.KRAKEN_API_KEY:
            errors.append("KRAKEN_API_KEY not set")
        
        if not cls.KRAKEN_PRIVATE_KEY:
            errors.append("KRAKEN_PRIVATE_KEY not set")
        
        if cls.INITIAL_CAPITAL <= 0:
            errors.append("INITIAL_CAPITAL must be > 0")
        
        if errors:
            raise ValueError("Configuration errors: " + ", ".join(errors))
        
        return True
    
    @classmethod
    def to_dict(cls):
        """Convert config to dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and key.isupper()
        }
    
    @classmethod
    def get_bot_config(cls, bot_id):
        """Get configuration for a specific bot"""
        configs = {
            'adaptive_grid': {
                'position_size': cls.GRID_TRADER_POSITION_SIZE,
                'grid_levels': cls.GRID_TRADER_LEVELS,
                'profit_per_level': cls.GRID_TRADER_PROFIT_PER_LEVEL,
                'stop_loss': cls.GRID_TRADER_STOP_LOSS,
                'take_profit': cls.GRID_TRADER_TAKE_PROFIT,
            },
            'momentum_tracker': {
                'position_size': cls.MOMENTUM_POSITION_SIZE,
                'trend_threshold': cls.MOMENTUM_TREND_THRESHOLD,
                'stop_loss': cls.MOMENTUM_STOP_LOSS,
                'take_profit': cls.MOMENTUM_TAKE_PROFIT,
            },
            'dca_accumulator': {
                'position_size': cls.DCA_POSITION_SIZE,
                'buy_interval_hours': cls.DCA_BUY_INTERVAL_HOURS,
                'stop_loss': cls.DCA_STOP_LOSS,
                'take_profit': cls.DCA_TAKE_PROFIT,
            },
            'scalp_master': {
                'position_size': cls.SCALP_POSITION_SIZE,
                'trade_duration_min': cls.SCALP_TRADE_DURATION_MIN,
                'profit_per_trade': cls.SCALP_PROFIT_PER_TRADE,
                'stop_loss': cls.SCALP_STOP_LOSS,
                'take_profit': cls.SCALP_TAKE_PROFIT,
                'max_trades_per_hour': cls.SCALP_MAX_TRADES_PER_HOUR,
            },
            'arb_finder': {
                'position_size': cls.ARB_POSITION_SIZE,
                'min_spread': cls.ARB_MIN_SPREAD,
                'stop_loss': cls.ARB_STOP_LOSS,
                'take_profit': cls.ARB_TAKE_PROFIT,
            }
        }
        return configs.get(bot_id, {})


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️ Configuration warning: {str(e)}")
