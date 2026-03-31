#!/usr/bin/env python3
"""
Intelligent Self-Adjusting Bots
Machine learning-based trading bots that optimize themselves
"""

import numpy as np
import logging
from datetime import datetime, timedelta
from enum import Enum
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    HIGHLY_VOLATILE = "highly_volatile"

class IntelligentBot:
    """
    Self-adjusting bot that learns and optimizes
    """
    
    def __init__(self, bot_id, initial_config):
        self.bot_id = bot_id
        self.config = initial_config.copy()
        
        # Performance tracking
        self.trades = deque(maxlen=100)  # Last 100 trades
        self.win_rate = 0
        self.profit_factor = 0
        self.sharpe_ratio = 0
        self.max_drawdown = 0
        
        # Learning parameters
        self.learning_rate = 0.01
        self.adjustment_threshold = 0.05  # 5% performance change triggers adjustment
        self.min_trades_for_adjustment = 5
        
        # State
        self.status = 'running'
        self.last_adjustment = datetime.now()
        self.adjustment_history = []
        self.market_regime = MarketRegime.SIDEWAYS
    
    def record_trade(self, trade_data):
        """Record a trade and trigger learning"""
        self.trades.append(trade_data)
        
        # Update metrics
        self._update_metrics()
        
        # Check if adjustment needed
        if len(self.trades) >= self.min_trades_for_adjustment:
            self._check_and_adjust()
    
    def _update_metrics(self):
        """Calculate performance metrics"""
        if len(self.trades) == 0:
            return
        
        trades = list(self.trades)
        
        # Win rate
        wins = sum(1 for t in trades if t.get('profit_loss', 0) > 0)
        self.win_rate = (wins / len(trades)) * 100
        
        # Profit factor
        gross_profit = sum(t.get('profit_loss', 0) for t in trades if t.get('profit_loss', 0) > 0)
        gross_loss = abs(sum(t.get('profit_loss', 0) for t in trades if t.get('profit_loss', 0) < 0))
        self.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Sharpe ratio (simplified)
        returns = [t.get('profit_loss', 0) for t in trades]
        if len(returns) > 1:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            self.sharpe_ratio = (mean_return / std_return) if std_return > 0 else 0
        
        # Max drawdown
        cumulative = 0
        peak = 0
        max_dd = 0
        for t in trades:
            cumulative += t.get('profit_loss', 0)
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown
        self.max_drawdown = max_dd
    
    def _check_and_adjust(self):
        """Check if bot should adjust parameters"""
        # Only adjust every 10 minutes
        if (datetime.now() - self.last_adjustment).total_seconds() < 600:
            return
        
        # Get last 10 trades
        recent_trades = list(self.trades)[-10:]
        
        if len(recent_trades) < 5:
            return
        
        recent_win_rate = sum(1 for t in recent_trades if t.get('profit_loss', 0) > 0) / len(recent_trades)
        
        # If win rate is high, increase position size
        if recent_win_rate > 0.80:
            self._increase_position_size()
        
        # If win rate is low, decrease position size
        elif recent_win_rate < 0.50:
            self._decrease_position_size()
        
        # Adjust stop-loss based on volatility
        self._adjust_stop_loss()
        
        # Adjust take-profit based on market regime
        self._adjust_take_profit()
        
        self.last_adjustment = datetime.now()
    
    def _increase_position_size(self):
        """Increase position size"""
        old_size = self.config['position_size']
        new_size = min(old_size * 1.1, 0.5)  # Increase by 10%, cap at 50%
        
        if new_size != old_size:
            self.config['position_size'] = new_size
            self.adjustment_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'increase_position',
                'old_value': old_size,
                'new_value': new_size,
                'reason': f'High win rate: {self.win_rate:.1f}%'
            })
            logger.info(f"{self.bot_id}: Increased position size to {new_size:.2%}")
    
    def _decrease_position_size(self):
        """Decrease position size"""
        old_size = self.config['position_size']
        new_size = max(old_size * 0.9, 0.05)  # Decrease by 10%, floor at 5%
        
        if new_size != old_size:
            self.config['position_size'] = new_size
            self.adjustment_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'decrease_position',
                'old_value': old_size,
                'new_value': new_size,
                'reason': f'Low win rate: {self.win_rate:.1f}%'
            })
            logger.info(f"{self.bot_id}: Decreased position size to {new_size:.2%}")
    
    def _adjust_stop_loss(self):
        """Adjust stop-loss based on volatility"""
        # Calculate recent volatility
        recent_trades = list(self.trades)[-20:]
        if len(recent_trades) < 5:
            return
        
        returns = [t.get('profit_loss', 0) for t in recent_trades]
        volatility = np.std(returns)
        
        old_sl = self.config.get('stop_loss', -3.0)
        
        # Higher volatility = wider stop-loss
        if volatility > 0.5:
            new_sl = old_sl * 1.2  # Widen by 20%
        elif volatility < 0.1:
            new_sl = old_sl * 0.9  # Tighten by 10%
        else:
            new_sl = old_sl
        
        if new_sl != old_sl:
            self.config['stop_loss'] = new_sl
            self.adjustment_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'adjust_stop_loss',
                'old_value': old_sl,
                'new_value': new_sl,
                'reason': f'Volatility: {volatility:.3f}'
            })
    
    def _adjust_take_profit(self):
        """Adjust take-profit based on market regime"""
        old_tp = self.config.get('take_profit', 2.0)
        
        # In bullish market, increase take-profit target
        if self.market_regime == MarketRegime.BULLISH:
            new_tp = old_tp * 1.2
        
        # In bearish market, decrease take-profit target
        elif self.market_regime == MarketRegime.BEARISH:
            new_tp = old_tp * 0.8
        
        # In sideways, keep moderate
        else:
            new_tp = old_tp
        
        if new_tp != old_tp:
            self.config['take_profit'] = new_tp
            self.adjustment_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'adjust_take_profit',
                'old_value': old_tp,
                'new_value': new_tp,
                'reason': f'Market regime: {self.market_regime.value}'
            })
    
    def detect_market_regime(self, price_data):
        """Detect current market regime"""
        if len(price_data) < 20:
            self.market_regime = MarketRegime.SIDEWAYS
            return
        
        prices = np.array(price_data)
        returns = np.diff(prices) / prices[:-1]
        
        # Calculate trend
        trend = np.mean(returns) * 252  # Annualized
        volatility = np.std(returns) * np.sqrt(252)
        
        # Determine regime
        if volatility > 0.5:
            self.market_regime = MarketRegime.HIGHLY_VOLATILE
        elif trend > 0.05:
            self.market_regime = MarketRegime.BULLISH
        elif trend < -0.05:
            self.market_regime = MarketRegime.BEARISH
        else:
            self.market_regime = MarketRegime.SIDEWAYS
    
    def should_pause(self):
        """Determine if bot should pause"""
        # Pause if losing more than 3 trades in a row
        if len(self.trades) >= 3:
            recent = list(self.trades)[-3:]
            if all(t.get('profit_loss', 0) < 0 for t in recent):
                return True
        
        # Pause if win rate drops below 30%
        if self.win_rate < 30 and len(self.trades) >= 10:
            return True
        
        return False
    
    def get_status(self):
        """Get bot status"""
        return {
            'bot_id': self.bot_id,
            'status': self.status,
            'config': self.config,
            'performance': {
                'win_rate': round(self.win_rate, 2),
                'profit_factor': round(self.profit_factor, 2),
                'sharpe_ratio': round(self.sharpe_ratio, 2),
                'max_drawdown': round(self.max_drawdown, 2),
                'trades_count': len(self.trades)
            },
            'market_regime': self.market_regime.value,
            'recent_adjustments': self.adjustment_history[-5:] if self.adjustment_history else []
        }


class IntelligentBotManager:
    """
    Manages all intelligent bots
    """
    
    def __init__(self):
        self.bots = {}
        self._initialize_bots()
    
    def _initialize_bots(self):
        """Initialize all bots"""
        bot_configs = {
            'adaptive_grid': {
                'name': 'Adaptive Grid Trader',
                'position_size': 0.30,
                'grid_levels': 5,
                'stop_loss': -3.0,
                'take_profit': 2.0,
            },
            'momentum_tracker': {
                'name': 'Momentum Tracker',
                'position_size': 0.20,
                'stop_loss': -3.0,
                'take_profit': 8.0,
            },
            'dca_accumulator': {
                'name': 'DCA Accumulator',
                'position_size': 0.16,
                'stop_loss': -5.0,
                'take_profit': 3.0,
            },
            'scalp_master': {
                'name': 'Scalp Master',
                'position_size': 0.20,
                'stop_loss': -0.5,
                'take_profit': 1.0,
            },
            'arb_finder': {
                'name': 'Arbitrage Finder',
                'position_size': 0.14,
                'stop_loss': -1.0,
                'take_profit': 0.5,
            }
        }
        
        for bot_id, config in bot_configs.items():
            self.bots[bot_id] = IntelligentBot(bot_id, config)
    
    def record_trade(self, bot_id, trade_data):
        """Record trade for a bot"""
        if bot_id in self.bots:
            self.bots[bot_id].record_trade(trade_data)
    
    def get_best_performing_bot(self):
        """Get the best performing bot"""
        if not self.bots:
            return None
        
        return max(
            self.bots.values(),
            key=lambda b: b.profit_factor if b.profit_factor > 0 else 0
        )
    
    def get_bot_status(self, bot_id):
        """Get bot status"""
        if bot_id in self.bots:
            return self.bots[bot_id].get_status()
        return None
    
    def get_all_status(self):
        """Get status of all bots"""
        return {
            bot_id: bot.get_status()
            for bot_id, bot in self.bots.items()
        }
    
    def reallocate_capital(self, total_capital):
        """
        Reallocate capital to best-performing bots
        """
        # Get bot performance
        performances = [
            (bot_id, bot.profit_factor)
            for bot_id, bot in self.bots.items()
        ]
        
        # Sort by profit factor
        performances.sort(key=lambda x: x[1], reverse=True)
        
        # Allocate more capital to top performers
        allocations = {}
        
        for i, (bot_id, profit_factor) in enumerate(performances):
            if i == 0:  # Top performer gets 35%
                allocations[bot_id] = 0.35
            elif i == 1:  # 2nd gets 25%
                allocations[bot_id] = 0.25
            elif i == 2:  # 3rd gets 20%
                allocations[bot_id] = 0.20
            else:  # Others split remaining
                allocations[bot_id] = 0.10
        
        # Update bot allocations
        for bot_id, allocation in allocations.items():
            self.bots[bot_id].config['position_size'] = allocation
        
        logger.info(f"Capital reallocated: {allocations}")
        return allocations
    
    def detect_market_regimes(self, price_data):
        """Detect market regimes for all bots"""
        for bot in self.bots.values():
            bot.detect_market_regime(price_data)
    
    def get_health_report(self):
        """Get system health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'bots': {}
        }
        
        for bot_id, bot in self.bots.items():
            status = bot.get_status()
            report['bots'][bot_id] = {
                'status': bot.status,
                'win_rate': status['performance']['win_rate'],
                'should_pause': bot.should_pause(),
                'market_regime': status['market_regime'],
                'recent_adjustments': len(status['recent_adjustments'])
            }
        
        return report


# Initialize global intelligent bot manager
intelligent_bot_manager = IntelligentBotManager()
