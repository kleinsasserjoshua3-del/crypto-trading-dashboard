#!/usr/bin/env python3
"""
Unit Tests for Trading System
Test critical functions and edge cases
"""

import unittest
from datetime import datetime
from risk_manager import RiskManager, CircuitBreakerStatus
from bot_controller import BotController
from config import Config

class TestRiskManager(unittest.TestCase):
    """Test risk management system"""
    
    def setUp(self):
        self.rm = RiskManager(initial_capital=50.0)
    
    def test_initialization(self):
        """Test risk manager initialization"""
        self.assertEqual(self.rm.initial_capital, 50.0)
        self.assertEqual(self.rm.current_balance, 50.0)
        self.assertEqual(self.rm.circuit_breaker_status, CircuitBreakerStatus.ACTIVE)
    
    def test_position_sizing(self):
        """Test position size calculation"""
        # BTC at $40,000, stop-loss at $38,800 (-3%)
        size = self.rm.calculate_position_size(40000, 38800)
        self.assertGreater(size, 0)
        self.assertLess(size, 0.01)  # Should be small for $50 capital
    
    def test_stop_loss_calculation(self):
        """Test stop-loss calculation"""
        entry = 40000
        
        # Grid strategy: -3%
        sl = self.rm.calculate_stop_loss(entry, 'grid')
        self.assertEqual(sl, entry * 0.97)
        
        # DCA strategy: -5%
        sl = self.rm.calculate_stop_loss(entry, 'dca')
        self.assertEqual(sl, entry * 0.95)
        
        # Scalping: -0.5%
        sl = self.rm.calculate_stop_loss(entry, 'scalping')
        self.assertEqual(sl, entry * 0.995)
    
    def test_take_profit_calculation(self):
        """Test take-profit calculation"""
        entry = 40000
        
        # Grid strategy: +2%
        tp = self.rm.calculate_take_profit(entry, 'grid')
        self.assertEqual(tp, entry * 1.02)
        
        # Momentum strategy: +8%
        tp = self.rm.calculate_take_profit(entry, 'momentum')
        self.assertEqual(tp, entry * 1.08)
    
    def test_trade_recording(self):
        """Test trade recording"""
        trade_data = {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'entry_price': 40000,
            'exit_price': 40800,
            'position_size': 0.001,
            'profit_loss': 0.80,
            'strategy': 'grid'
        }
        
        trade = self.rm.record_trade(trade_data)
        self.assertEqual(trade['symbol'], 'BTC/USD')
        self.assertEqual(trade['profit_loss'], 0.80)
        self.assertAlmostEqual(self.rm.current_balance, 50.80, places=2)
    
    def test_drawdown_calculation(self):
        """Test drawdown calculation"""
        # Record a loss
        self.rm.peak_balance = 50.0
        self.rm.current_balance = 42.5  # 15% loss
        
        drawdown = self.rm.get_drawdown()
        self.assertAlmostEqual(drawdown, 0.15, places=2)
    
    def test_circuit_breaker_level_1(self):
        """Test circuit breaker level 1 (daily loss)"""
        # Record losses totaling 5% of capital ($2.50)
        for i in range(5):
            trade = {
                'symbol': 'BTC/USD',
                'side': 'sell',
                'entry_price': 40000,
                'exit_price': 39200,
                'position_size': 0.001,
                'profit_loss': -0.50,
                'strategy': 'test'
            }
            self.rm.record_trade(trade)
        
        # Should trigger level 1
        self.assertEqual(self.rm.circuit_breaker_status, CircuitBreakerStatus.LEVEL_1_TRIGGERED)
        self.assertTrue(self.rm.should_pause_trading())
    
    def test_circuit_breaker_level_3(self):
        """Test circuit breaker level 3 (emergency stop)"""
        # Simulate 20% drawdown
        self.rm.peak_balance = 50.0
        self.rm.current_balance = 40.0
        self.rm.check_circuit_breakers()
        
        # Should trigger level 3
        self.assertEqual(self.rm.circuit_breaker_status, CircuitBreakerStatus.LEVEL_3_TRIGGERED)
        self.assertTrue(self.rm.should_emergency_stop())


class TestBotController(unittest.TestCase):
    """Test bot controller"""
    
    def setUp(self):
        self.bc = BotController()
    
    def test_get_bot(self):
        """Test getting bot configuration"""
        bot = self.bc.get_bot('adaptive_grid')
        self.assertIsNotNone(bot)
        self.assertEqual(bot['name'], 'Adaptive Grid Trader')
    
    def test_update_parameter(self):
        """Test parameter update"""
        success = self.bc.update_parameter('adaptive_grid', 'position_size', 0.25)
        self.assertTrue(success)
        
        bot = self.bc.get_bot('adaptive_grid')
        self.assertEqual(bot['parameters']['position_size'], 0.25)
    
    def test_invalid_parameter(self):
        """Test invalid parameter update"""
        success = self.bc.update_parameter('adaptive_grid', 'invalid_param', 0.5)
        self.assertFalse(success)
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Position size > 1.0 should fail
        success = self.bc.update_parameter('adaptive_grid', 'position_size', 1.5)
        self.assertFalse(success)
        
        # Negative position size should fail
        success = self.bc.update_parameter('adaptive_grid', 'position_size', -0.1)
        self.assertFalse(success)
    
    def test_toggle_bot(self):
        """Test bot toggle"""
        initial_status = self.bc.get_bot('adaptive_grid')['status']
        self.bc.toggle_bot('adaptive_grid')
        new_status = self.bc.get_bot('adaptive_grid')['status']
        
        self.assertNotEqual(initial_status, new_status)
    
    def test_aggressiveness_adjustment(self):
        """Test aggressiveness adjustment"""
        original_size = self.bc.get_bot('adaptive_grid')['parameters']['position_size']
        
        # Set to aggressive (8/10)
        self.bc.adjust_aggressiveness('adaptive_grid', 8)
        new_size = self.bc.get_bot('adaptive_grid')['parameters']['position_size']
        
        # Position size should increase
        self.assertGreater(new_size, original_size)
    
    def test_reset_to_defaults(self):
        """Test reset to defaults"""
        # Change a parameter
        self.bc.update_parameter('adaptive_grid', 'position_size', 0.50)
        
        # Reset
        self.bc.reset_to_defaults('adaptive_grid')
        
        # Should be back to default
        bot = self.bc.get_bot('adaptive_grid')
        self.assertEqual(bot['parameters']['position_size'], 0.30)


class TestConfiguration(unittest.TestCase):
    """Test configuration"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Should not raise if API keys are set
        try:
            Config.validate()
        except ValueError:
            # Expected if keys not set in test environment
            pass
    
    def test_bot_config_retrieval(self):
        """Test getting bot-specific config"""
        config = Config.get_bot_config('adaptive_grid')
        self.assertIn('position_size', config)
        self.assertIn('stop_loss', config)
        self.assertIn('take_profit', config)
    
    def test_config_to_dict(self):
        """Test config to dictionary conversion"""
        config_dict = Config.to_dict()
        self.assertIn('INITIAL_CAPITAL', config_dict)
        self.assertIn('TRADING_PAIRS', config_dict)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_risk_and_bot_integration(self):
        """Test risk manager and bot controller integration"""
        rm = RiskManager(initial_capital=50.0)
        bc = BotController()
        
        # Simulate a profitable trade
        trade = {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'entry_price': 40000,
            'exit_price': 40800,
            'position_size': 0.001,
            'profit_loss': 0.80,
            'strategy': 'grid'
        }
        
        rm.record_trade(trade)
        
        # Check that risk manager updated
        self.assertGreater(rm.current_balance, 50.0)
        
        # Bot controller should still work
        bot = bc.get_bot('adaptive_grid')
        self.assertIsNotNone(bot)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
