#!/usr/bin/env python3
"""
Bot Controller - Manage and adjust individual bot parameters
Allows real-time tuning of trading strategies
"""

import logging
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotStrategy(Enum):
    GRID_TRADING = "grid"
    MOMENTUM = "momentum"
    DCA = "dca"
    SCALPING = "scalping"
    ARBITRAGE = "arbitrage"

class BotController:
    """
    Controls and adjusts individual bot parameters
    """
    
    def __init__(self):
        self.bots = {
            'adaptive_grid': {
                'name': 'Adaptive Grid Trader',
                'strategy': BotStrategy.GRID_TRADING,
                'status': 'running',
                'parameters': {
                    'position_size': 0.30,  # 30% of capital
                    'grid_levels': 5,
                    'profit_per_level': 2.0,  # 2% per level
                    'stop_loss': -3.0,  # -3%
                    'take_profit': 2.0,  # +2%
                    'max_open_positions': 5,
                },
                'performance': {
                    'win_rate': 82.3,
                    'trades': 0,
                    'profit': 0,
                    'last_trade': None
                }
            },
            'momentum_tracker': {
                'name': 'Momentum Tracker',
                'strategy': BotStrategy.MOMENTUM,
                'status': 'running',
                'parameters': {
                    'position_size': 0.20,  # 20% of capital
                    'trend_strength_threshold': 1.5,
                    'stop_loss': -3.0,  # -3%
                    'take_profit': 8.0,  # +8%
                    'max_open_positions': 3,
                    'leverage': 1.0,  # No leverage for $50
                },
                'performance': {
                    'win_rate': 76.5,
                    'trades': 0,
                    'profit': 0,
                    'last_trade': None
                }
            },
            'dca_accumulator': {
                'name': 'DCA Accumulator',
                'strategy': BotStrategy.DCA,
                'status': 'running',
                'parameters': {
                    'position_size': 0.16,  # 16% of capital
                    'buy_interval_hours': 4,
                    'buy_amount': 0.50,  # $0.50 per buy
                    'stop_loss': -5.0,  # -5%
                    'take_profit': 3.0,  # +3%
                    'accumulation_target': 0.001,  # 0.001 BTC
                },
                'performance': {
                    'win_rate': 100,
                    'trades': 0,
                    'profit': 0,
                    'last_trade': None
                }
            },
            'scalp_master': {
                'name': 'Scalp Master',
                'strategy': BotStrategy.SCALPING,
                'status': 'running',
                'parameters': {
                    'position_size': 0.20,  # 20% of capital
                    'trade_duration_minutes': 15,
                    'profit_per_trade': 0.5,  # 0.5% per trade
                    'stop_loss': -0.5,  # -0.5% (tight)
                    'take_profit': 1.0,  # +1%
                    'max_trades_per_hour': 5,
                },
                'performance': {
                    'win_rate': 71.2,
                    'trades': 0,
                    'profit': 0,
                    'last_trade': None
                }
            },
            'arb_finder': {
                'name': 'Arbitrage Finder',
                'strategy': BotStrategy.ARBITRAGE,
                'status': 'running',
                'parameters': {
                    'position_size': 0.14,  # 14% of capital
                    'min_spread': 0.5,  # 0.5% minimum spread
                    'stop_loss': -1.0,  # -1%
                    'take_profit': 0.5,  # +0.5%
                    'execution_speed': 'fast',
                },
                'performance': {
                    'win_rate': 95.8,
                    'trades': 0,
                    'profit': 0,
                    'last_trade': None
                }
            }
        }
    
    def get_bot(self, bot_id):
        """Get bot configuration"""
        return self.bots.get(bot_id)
    
    def get_all_bots(self):
        """Get all bots"""
        return self.bots
    
    def update_parameter(self, bot_id, parameter_name, value):
        """
        Update a bot parameter
        
        Args:
            bot_id: Bot identifier
            parameter_name: Parameter to update
            value: New value
        """
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
        
        bot = self.bots[bot_id]
        
        # Validate parameter exists
        if parameter_name not in bot['parameters']:
            logger.error(f"Parameter {parameter_name} not found in {bot_id}")
            return False
        
        # Validate value ranges
        if not self._validate_parameter(bot_id, parameter_name, value):
            logger.error(f"Invalid value {value} for {parameter_name}")
            return False
        
        # Update parameter
        old_value = bot['parameters'][parameter_name]
        bot['parameters'][parameter_name] = value
        
        logger.info(f"Updated {bot_id}.{parameter_name}: {old_value} → {value}")
        return True
    
    def _validate_parameter(self, bot_id, parameter_name, value):
        """
        Validate parameter values
        """
        # Position size: 0-1 (0-100%)
        if parameter_name == 'position_size':
            return 0 < value <= 1.0
        
        # Percentages: -100 to +100
        if parameter_name in ['stop_loss', 'take_profit', 'profit_per_trade', 'profit_per_level']:
            return -100 < value < 100
        
        # Grid levels: 1-20
        if parameter_name == 'grid_levels':
            return 1 <= value <= 20
        
        # Intervals: 1-24 hours
        if parameter_name == 'buy_interval_hours':
            return 1 <= value <= 24
        
        # Trades per hour: 1-20
        if parameter_name == 'max_trades_per_hour':
            return 1 <= value <= 20
        
        # Spread: 0.1-5%
        if parameter_name == 'min_spread':
            return 0.1 <= value <= 5.0
        
        # Leverage: 1-3x
        if parameter_name == 'leverage':
            return 1.0 <= value <= 3.0
        
        # Threshold: 0-10
        if parameter_name == 'trend_strength_threshold':
            return 0 < value <= 10
        
        # Duration: 1-60 minutes
        if parameter_name == 'trade_duration_minutes':
            return 1 <= value <= 60
        
        # Max positions: 1-10
        if parameter_name == 'max_open_positions':
            return 1 <= value <= 10
        
        return True
    
    def toggle_bot(self, bot_id):
        """Toggle bot on/off"""
        if bot_id not in self.bots:
            return False
        
        bot = self.bots[bot_id]
        bot['status'] = 'stopped' if bot['status'] == 'running' else 'running'
        logger.info(f"Bot {bot_id} toggled to {bot['status']}")
        return True
    
    def get_bot_status(self, bot_id):
        """Get bot status"""
        if bot_id not in self.bots:
            return None
        
        bot = self.bots[bot_id]
        return {
            'bot_id': bot_id,
            'name': bot['name'],
            'strategy': bot['strategy'].value,
            'status': bot['status'],
            'parameters': bot['parameters'],
            'performance': bot['performance']
        }
    
    def get_all_status(self):
        """Get status of all bots"""
        return {
            bot_id: self.get_bot_status(bot_id)
            for bot_id in self.bots
        }
    
    def adjust_aggressiveness(self, bot_id, level):
        """
        Adjust bot aggressiveness (1-10 scale)
        1 = conservative, 10 = aggressive
        """
        if bot_id not in self.bots:
            return False
        
        if not 1 <= level <= 10:
            logger.error(f"Aggressiveness level must be 1-10, got {level}")
            return False
        
        bot = self.bots[bot_id]
        
        # Scale adjustments based on aggressiveness
        # Conservative (1-3): Smaller positions, wider stops
        # Moderate (4-7): Normal positions
        # Aggressive (8-10): Larger positions, tighter stops
        
        if level <= 3:
            # Conservative
            bot['parameters']['position_size'] = bot['parameters']['position_size'] * 0.5
            bot['parameters']['stop_loss'] = bot['parameters']['stop_loss'] * 1.5  # Wider
        elif level >= 8:
            # Aggressive
            bot['parameters']['position_size'] = min(bot['parameters']['position_size'] * 1.5, 0.5)
            bot['parameters']['stop_loss'] = bot['parameters']['stop_loss'] * 0.7  # Tighter
        
        logger.info(f"Bot {bot_id} aggressiveness set to {level}/10")
        return True
    
    def reset_to_defaults(self, bot_id):
        """Reset bot parameters to defaults"""
        if bot_id not in self.bots:
            return False
        
        # Store original defaults
        defaults = {
            'adaptive_grid': {
                'position_size': 0.30,
                'grid_levels': 5,
                'profit_per_level': 2.0,
                'stop_loss': -3.0,
                'take_profit': 2.0,
            },
            'momentum_tracker': {
                'position_size': 0.20,
                'trend_strength_threshold': 1.5,
                'stop_loss': -3.0,
                'take_profit': 8.0,
            },
            'dca_accumulator': {
                'position_size': 0.16,
                'buy_interval_hours': 4,
                'stop_loss': -5.0,
                'take_profit': 3.0,
            },
            'scalp_master': {
                'position_size': 0.20,
                'trade_duration_minutes': 15,
                'profit_per_trade': 0.5,
                'stop_loss': -0.5,
                'take_profit': 1.0,
            },
            'arb_finder': {
                'position_size': 0.14,
                'min_spread': 0.5,
                'stop_loss': -1.0,
                'take_profit': 0.5,
            }
        }
        
        if bot_id in defaults:
            self.bots[bot_id]['parameters'].update(defaults[bot_id])
            logger.info(f"Bot {bot_id} reset to defaults")
            return True
        
        return False
    
    def get_recommendations(self, bot_id):
        """Get optimization recommendations for a bot"""
        if bot_id not in self.bots:
            return None
        
        bot = self.bots[bot_id]
        perf = bot['performance']
        
        recommendations = []
        
        # Win rate analysis
        if perf['win_rate'] < 50:
            recommendations.append({
                'type': 'warning',
                'message': f"Win rate is {perf['win_rate']}%. Consider adjusting strategy.",
                'action': 'reduce_position_size'
            })
        elif perf['win_rate'] > 80:
            recommendations.append({
                'type': 'positive',
                'message': f"Strong win rate of {perf['win_rate']}%. Consider increasing position size.",
                'action': 'increase_position_size'
            })
        
        # Profit analysis
        if perf['profit'] > 0 and perf['trades'] > 10:
            recommendations.append({
                'type': 'positive',
                'message': f"Profitable with {perf['trades']} trades. System is working well.",
                'action': 'maintain'
            })
        
        return recommendations


# Initialize global bot controller
bot_controller = BotController()
