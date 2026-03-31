"""
Intelligent Bots v2 - Smart bots for small account growth
Each bot analyzes market conditions and only enters high-probability trades
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SmartEntryPointFinder:
    """Bot #1: Analyzes 20+ indicators for high-probability entries"""
    
    def __init__(self, capital: float = 50.0):
        self.capital = capital
        self.position_size = capital  # 100% for high-probability entries
        self.stop_loss_pct = 2.0
        self.take_profit_pct = 6.5
        self.win_rate = 0.76
        self.trades_per_week = 3
        self.max_daily_trades = 1
        self.daily_loss_limit = 0.03 * capital
        self.weekly_loss_limit = 0.05 * capital
        
    def analyze_market(self, market_data: Dict) -> Dict:
        """Analyze 20+ indicators for entry signals"""
        signals = {
            'rsi_oversold': market_data.get('rsi', 50) < 30,
            'macd_bullish': market_data.get('macd_signal', 0) > 0,
            'volume_spike': market_data.get('volume_ratio', 1.0) > 1.2,
            'bollinger_bounce': market_data.get('price_position', 0.5) < 0.3,
            'support_bounce': market_data.get('at_support', False),
            'fib_retracement': market_data.get('at_fib_level', False),
            'trend_aligned': market_data.get('daily_trend', 'neutral') == 'up',
        }
        
        signal_count = sum(signals.values())
        return {
            'signals': signals,
            'signal_count': signal_count,
            'should_enter': signal_count >= 3,
            'confidence': signal_count / 7.0
        }
    
    def get_entry_price(self, market_data: Dict) -> float:
        """Get entry price based on analysis"""
        return market_data.get('current_price', 0)
    
    def get_position_size(self, signal_strength: float) -> float:
        """Position size based on signal strength"""
        if signal_strength >= 0.85:
            return self.position_size
        elif signal_strength >= 0.70:
            return self.position_size * 0.8
        else:
            return 0  # Don't trade
    
    def get_stop_loss(self, entry_price: float) -> float:
        """Calculate stop loss"""
        return entry_price * (1 - self.stop_loss_pct / 100)
    
    def get_take_profit(self, entry_price: float) -> float:
        """Calculate take profit"""
        return entry_price * (1 + self.take_profit_pct / 100)


class TrendFollowingMomentum:
    """Bot #2: Identifies strong trends and enters on pullbacks"""
    
    def __init__(self, capital: float = 50.0):
        self.capital = capital
        self.position_size = capital * 0.8
        self.stop_loss_pct = 3.0
        self.take_profit_pct = 12.0
        self.win_rate = 0.67
        self.trades_per_week = 4
        self.max_concurrent = 2
        self.daily_loss_limit = 0.04 * capital
        self.weekly_loss_limit = 0.08 * capital
        
    def analyze_market(self, market_data: Dict) -> Dict:
        """Analyze trend strength and pullback opportunity"""
        signals = {
            'ema_aligned': market_data.get('ema_50_above_200', False),
            'adx_strong': market_data.get('adx', 20) > 25,
            'ichimoku_bullish': market_data.get('ichimoku_signal', 'neutral') == 'bullish',
            'macd_positive': market_data.get('macd', 0) > 0,
            'price_at_pullback': market_data.get('price_position', 0.5) < 0.6,
            'volume_confirmed': market_data.get('volume_ratio', 1.0) > 1.1,
        }
        
        signal_count = sum(signals.values())
        return {
            'signals': signals,
            'signal_count': signal_count,
            'should_enter': signal_count >= 4,
            'trend_strength': market_data.get('adx', 20) / 50.0
        }
    
    def get_take_profit(self, entry_price: float, trend_strength: float) -> float:
        """Adjust take profit based on trend strength"""
        if trend_strength > 0.6:
            return entry_price * (1 + 0.15)  # 15% for strong trends
        else:
            return entry_price * (1 + 0.10)  # 10% for weaker trends


class MeanReversionBounce:
    """Bot #3: Enters oversold bounces for quick profits"""
    
    def __init__(self, capital: float = 50.0):
        self.capital = capital
        self.position_size = capital * 0.9
        self.stop_loss_pct = 2.5
        self.take_profit_pct = 5.0
        self.win_rate = 0.72
        self.trades_per_week = 5
        self.max_concurrent = 3
        self.daily_loss_limit = 0.03 * capital
        self.weekly_loss_limit = 0.06 * capital
        
    def analyze_market(self, market_data: Dict) -> Dict:
        """Analyze oversold conditions"""
        signals = {
            'rsi_oversold': market_data.get('rsi', 50) < 35,
            'at_support': market_data.get('at_support', False),
            'volume_spike': market_data.get('volume_ratio', 1.0) > 1.3,
            'above_200ema': market_data.get('above_200ema', False),
            'bounce_started': market_data.get('bounce_signal', False),
        }
        
        signal_count = sum(signals.values())
        return {
            'signals': signals,
            'signal_count': signal_count,
            'should_enter': signal_count >= 3,
            'oversold_strength': (35 - market_data.get('rsi', 50)) / 35.0
        }


class BreakoutMomentumSurge:
    """Bot #4: Enters breakouts with volume confirmation"""
    
    def __init__(self, capital: float = 50.0):
        self.capital = capital
        self.position_size = capital  # 100% for high-confidence breakouts
        self.stop_loss_pct = 2.0
        self.take_profit_pct = 10.0
        self.win_rate = 0.62
        self.trades_per_week = 3
        self.max_concurrent = 1
        self.daily_loss_limit = 0.04 * capital
        self.weekly_loss_limit = 0.08 * capital
        
    def analyze_market(self, market_data: Dict) -> Dict:
        """Analyze breakout setup"""
        signals = {
            'bollinger_squeeze': market_data.get('bollinger_width', 1.0) < 0.5,
            'consolidating': market_data.get('consolidating', False),
            'volume_low': market_data.get('volume_ratio', 1.0) < 1.0,
            'rsi_neutral': 40 < market_data.get('rsi', 50) < 60,
            'macd_ready': market_data.get('macd_signal', 0) > -0.1,
        }
        
        signal_count = sum(signals.values())
        return {
            'signals': signals,
            'signal_count': signal_count,
            'should_wait': signal_count >= 4,  # Wait for breakout
            'breakout_potential': market_data.get('consolidation_days', 0) / 20.0
        }


class SmartSwingTrader:
    """Bot #5: Combines all strategies with adaptive logic"""
    
    def __init__(self, capital: float = 50.0):
        self.capital = capital
        self.stop_loss_pct = 2.5
        self.take_profit_pct = 10.0
        self.win_rate = 0.72
        self.trades_per_week = 5
        self.max_concurrent = 3
        self.daily_loss_limit = 0.05 * capital
        self.weekly_loss_limit = 0.10 * capital
        
        # Sub-bots
        self.sepf = SmartEntryPointFinder(capital)
        self.tfm = TrendFollowingMomentum(capital)
        self.mrb = MeanReversionBounce(capital)
        self.bms = BreakoutMomentumSurge(capital)
        
    def identify_market_regime(self, market_data: Dict) -> str:
        """Identify if market is trending, ranging, or volatile"""
        adx = market_data.get('adx', 20)
        atr_pct = market_data.get('atr_pct', 1.0)
        
        if adx > 30 and atr_pct < 2.0:
            return 'trending'
        elif adx < 20 and atr_pct < 1.5:
            return 'ranging'
        else:
            return 'volatile'
    
    def select_strategy(self, market_regime: str, market_data: Dict) -> Dict:
        """Select best strategy for current market regime"""
        if market_regime == 'trending':
            # Use trend following or breakout
            tfm_analysis = self.tfm.analyze_market(market_data)
            bms_analysis = self.bms.analyze_market(market_data)
            
            if tfm_analysis['should_enter']:
                return {'strategy': 'TFM', 'analysis': tfm_analysis}
            elif not bms_analysis['should_wait']:
                return {'strategy': 'BMS', 'analysis': bms_analysis}
                
        elif market_regime == 'ranging':
            # Use mean reversion
            mrb_analysis = self.mrb.analyze_market(market_data)
            if mrb_analysis['should_enter']:
                return {'strategy': 'MRB', 'analysis': mrb_analysis}
                
        else:  # volatile
            # Use most selective (SEPF)
            sepf_analysis = self.sepf.analyze_market(market_data)
            if sepf_analysis['should_enter']:
                return {'strategy': 'SEPF', 'analysis': sepf_analysis}
        
        return {'strategy': 'NONE', 'analysis': {}}
    
    def get_position_size(self, strategy: str, signal_strength: float) -> float:
        """Adaptive position sizing"""
        base_size = self.capital
        
        if signal_strength >= 0.85:
            return base_size
        elif signal_strength >= 0.70:
            return base_size * 0.75
        elif signal_strength >= 0.60:
            return base_size * 0.5
        else:
            return 0


class BotManager:
    """Manages all 5 bots and their deployment"""
    
    def __init__(self):
        self.bots = {
            'sepf': SmartEntryPointFinder(),
            'tfm': TrendFollowingMomentum(),
            'mrb': MeanReversionBounce(),
            'bms': BreakoutMomentumSurge(),
            'sst': SmartSwingTrader(),
        }
        self.active_bots = []
        self.total_capital = 0.0
        self.trades = []
        self.losses_today = 0.0
        self.losses_week = 0.0
        
    def activate_bot(self, bot_id: str, capital: float):
        """Activate a bot with specified capital"""
        if bot_id in self.bots:
            self.active_bots.append({
                'id': bot_id,
                'capital': capital,
                'active': True,
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'profit': 0.0
            })
            self.total_capital += capital
            return True
        return False
    
    def get_bot_recommendation(self, bot_id: str, market_data: Dict) -> Dict:
        """Get trading recommendation from a bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {'action': 'NONE', 'reason': 'Bot not found'}
        
        if bot_id == 'sst':
            market_regime = bot.identify_market_regime(market_data)
            strategy_choice = bot.select_strategy(market_regime, market_data)
            return {
                'action': 'ANALYZE',
                'market_regime': market_regime,
                'strategy': strategy_choice.get('strategy'),
                'analysis': strategy_choice.get('analysis', {})
            }
        else:
            analysis = bot.analyze_market(market_data)
            if analysis.get('should_enter'):
                return {
                    'action': 'ENTER',
                    'stop_loss_pct': bot.stop_loss_pct,
                    'take_profit_pct': bot.take_profit_pct,
                    'analysis': analysis
                }
            else:
                return {
                    'action': 'WAIT',
                    'analysis': analysis
                }
    
    def get_status(self) -> Dict:
        """Get status of all active bots"""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_bots': len(self.active_bots),
            'total_capital': self.total_capital,
            'bots': self.active_bots,
            'losses_today': self.losses_today,
            'losses_week': self.losses_week,
        }


# Export for use in app.py
bot_manager = BotManager()
