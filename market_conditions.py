"""
Market Condition Detector & Adaptive Bot Settings
Automatically adjusts bot parameters based on market conditions
"""

import random
from datetime import datetime

class MarketConditionDetector:
    """Detects market conditions and recommends bot settings"""
    
    def __init__(self):
        self.conditions = {
            'volatile': False,
            'trending': False,
            'sideways': False,
            'high_volume': False,
            'low_volume': False,
            'bull_market': False,
            'bear_market': False
        }
        self.volatility_level = 0  # 0-10 scale
        self.trend_strength = 0    # 0-10 scale
        self.volume_level = 0      # 0-10 scale
    
    def detect_conditions(self):
        """Detect current market conditions (simulated)"""
        # In production, this would read real market data
        self.volatility_level = random.randint(2, 8)
        self.trend_strength = random.randint(1, 9)
        self.volume_level = random.randint(3, 9)
        
        # Determine conditions
        self.conditions['volatile'] = self.volatility_level > 6
        self.conditions['trending'] = self.trend_strength > 6
        self.conditions['sideways'] = self.trend_strength <= 4
        self.conditions['high_volume'] = self.volume_level > 7
        self.conditions['low_volume'] = self.volume_level < 4
        self.conditions['bull_market'] = random.choice([True, False])
        self.conditions['bear_market'] = not self.conditions['bull_market']
        
        return self.conditions
    
    def get_market_regime(self):
        """Get overall market regime"""
        if self.conditions['volatile'] and self.conditions['trending']:
            return 'aggressive'
        elif self.conditions['sideways'] and self.conditions['low_volume']:
            return 'conservative'
        elif self.conditions['trending'] and self.conditions['high_volume']:
            return 'strong_trend'
        elif self.conditions['sideways']:
            return 'range_bound'
        else:
            return 'moderate'


class AdaptiveBotSettings:
    """Generates adaptive settings based on market conditions"""
    
    def __init__(self):
        self.detector = MarketConditionDetector()
    
    def get_settings_for_market(self):
        """Get bot settings based on current market conditions"""
        conditions = self.detector.detect_conditions()
        regime = self.detector.get_market_regime()
        
        settings = {
            'regime': regime,
            'volatility': self.detector.volatility_level,
            'trend_strength': self.detector.trend_strength,
            'volume': self.detector.volume_level,
            'bots': self._generate_bot_settings(regime, conditions)
        }
        
        return settings
    
    def _generate_bot_settings(self, regime, conditions):
        """Generate bot-specific settings based on regime"""
        
        base_settings = {
            'grid_trader': {
                'name': 'Adaptive Grid Trader',
                'position_size': 30,
                'stop_loss': 2,
                'take_profit': 5
            },
            'momentum': {
                'name': 'Momentum Tracker',
                'position_size': 20,
                'stop_loss': 4,  # UPDATED from 3%
                'take_profit': 8
            },
            'dca': {
                'name': 'DCA Accumulator',
                'position_size': 16,
                'stop_loss': 2,  # UPDATED from 1%
                'take_profit': 3
            },
            'scalp': {
                'name': 'Scalp Master',
                'position_size': 20,
                'stop_loss': 1.5,  # UPDATED from 0.5%
                'take_profit': 2
            },
            'arb': {
                'name': 'Arbitrage Finder',
                'position_size': 14,
                'stop_loss': 0.3,
                'take_profit': 1
            }
        }
        
        # Adjust based on market regime
        if regime == 'aggressive':
            # High volatility + trending = increase stops, reduce positions
            base_settings['grid_trader']['stop_loss'] = 3
            base_settings['momentum']['stop_loss'] = 5
            base_settings['scalp']['stop_loss'] = 2
            base_settings['dca']['position_size'] = 12
            
        elif regime == 'conservative':
            # Low volume + sideways = tight stops, small positions
            base_settings['grid_trader']['position_size'] = 20
            base_settings['momentum']['position_size'] = 15
            base_settings['scalp']['position_size'] = 10
            base_settings['dca']['position_size'] = 12
            
        elif regime == 'strong_trend':
            # Strong trend + high volume = widen stops, increase positions
            base_settings['momentum']['position_size'] = 25
            base_settings['momentum']['stop_loss'] = 5
            base_settings['momentum']['take_profit'] = 10
            base_settings['grid_trader']['position_size'] = 35
            
        elif regime == 'range_bound':
            # Sideways market = grid trading optimal
            base_settings['grid_trader']['position_size'] = 40
            base_settings['grid_trader']['take_profit'] = 3
            base_settings['scalp']['position_size'] = 25
            
        # Apply volatility adjustments
        if conditions['volatile']:
            # Increase stops in volatile markets
            for bot in base_settings.values():
                bot['stop_loss'] = min(bot['stop_loss'] * 1.3, 8)
        
        if conditions['low_volume']:
            # Reduce positions in low volume
            for bot in base_settings.values():
                bot['position_size'] = max(bot['position_size'] * 0.7, 5)
        
        return base_settings
    
    def get_aggressiveness_for_market(self, regime):
        """Get aggressiveness levels based on market regime"""
        aggressiveness = {
            'aggressive': {
                'grid_trader': 6,
                'momentum': 8,
                'dca': 2,
                'scalp': 5,  # REDUCED from 9
                'arb': 4
            },
            'conservative': {
                'grid_trader': 4,
                'momentum': 5,
                'dca': 2,
                'scalp': 3,
                'arb': 3
            },
            'strong_trend': {
                'grid_trader': 5,
                'momentum': 9,
                'dca': 3,
                'scalp': 6,
                'arb': 4
            },
            'range_bound': {
                'grid_trader': 8,
                'momentum': 4,
                'dca': 2,
                'scalp': 7,
                'arb': 4
            },
            'moderate': {
                'grid_trader': 5,
                'momentum': 7,
                'dca': 3,
                'scalp': 6,
                'arb': 4
            }
        }
        
        return aggressiveness.get(regime, aggressiveness['moderate'])


def get_adaptive_settings():
    """Get current adaptive settings based on market conditions"""
    adapter = AdaptiveBotSettings()
    settings = adapter.get_settings_for_market()
    aggressiveness = adapter.get_aggressiveness_for_market(settings['regime'])
    
    # Combine settings
    for bot_id, bot_settings in settings['bots'].items():
        bot_settings['aggressiveness'] = aggressiveness[bot_id]
    
    return settings
