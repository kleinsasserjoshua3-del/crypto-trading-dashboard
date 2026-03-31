#!/usr/bin/env python3
"""
Kraken Exchange Integration
Real-time market data, order execution, and account management
"""

import ccxt
import os
import logging
from datetime import datetime, timedelta
from risk_manager import risk_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExchangeManager:
    """
    Manages all interactions with Kraken exchange
    """
    
    def __init__(self):
        # Initialize Kraken exchange
        self.kraken = ccxt.kraken({
            'apiKey': os.environ.get('KRAKEN_API_KEY', ''),
            'secret': os.environ.get('KRAKEN_PRIVATE_KEY', ''),
            'enableRateLimit': True,
            'rateLimit': 3000  # 3 seconds between requests
        })
        
        self.trading_pairs = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'XRP/USD']
        self.min_order_size = 10  # Minimum $10 per order
        self.open_orders = {}
        self.trade_history = []
        
        logger.info("Kraken exchange manager initialized")
    
    def test_connection(self):
        """
        Test connection to Kraken API
        """
        try:
            balance = self.kraken.fetch_balance()
            logger.info("✅ Kraken connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Kraken connection failed: {str(e)}")
            return False
    
    def get_balance(self):
        """
        Get current account balance
        """
        try:
            balance = self.kraken.fetch_balance()
            return {
                'total': balance.get('total', {}),
                'free': balance.get('free', {}),
                'used': balance.get('used', {}),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return None
    
    def get_ticker(self, symbol):
        """
        Get current price and market data for a symbol
        """
        try:
            ticker = self.kraken.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'volume': ticker['quoteVolume'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            return None
    
    def get_all_tickers(self):
        """
        Get prices for all trading pairs
        """
        tickers = {}
        for pair in self.trading_pairs:
            ticker = self.get_ticker(pair)
            if ticker:
                tickers[pair] = ticker
        return tickers
    
    def place_limit_order(self, symbol, side, amount, price, bot_id):
        """
        Place a limit order
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Limit price
            bot_id: Which bot is placing the order
        """
        try:
            # Validate order size
            if amount * price < self.min_order_size:
                logger.warning(f"Order size ${amount * price:.2f} below minimum ${self.min_order_size}")
                return None
            
            # Check risk limits
            if risk_manager.should_pause_trading():
                logger.warning(f"Trading paused - order rejected for {symbol}")
                return None
            
            # Place order
            order = self.kraken.create_limit_order(symbol, side, amount, price)
            
            # Record order
            self.open_orders[order['id']] = {
                'id': order['id'],
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'bot_id': bot_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'open'
            }
            
            logger.info(f"Order placed: {side} {amount} {symbol} @ ${price} (Bot: {bot_id})")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """
        Cancel an open order
        """
        try:
            result = self.kraken.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return None
    
    def get_open_orders(self, symbol=None):
        """
        Get all open orders
        """
        try:
            if symbol:
                orders = self.kraken.fetch_open_orders(symbol)
            else:
                orders = self.kraken.fetch_open_orders()
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {str(e)}")
            return []
    
    def get_closed_orders(self, symbol=None, limit=50):
        """
        Get closed orders
        """
        try:
            if symbol:
                orders = self.kraken.fetch_closed_orders(symbol, limit=limit)
            else:
                orders = self.kraken.fetch_closed_orders(limit=limit)
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching closed orders: {str(e)}")
            return []
    
    def get_my_trades(self, symbol, limit=50):
        """
        Get trade history
        """
        try:
            trades = self.kraken.fetch_my_trades(symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"Error fetching trades: {str(e)}")
            return []
    
    def calculate_slippage(self, symbol, side, amount):
        """
        Estimate slippage for an order
        """
        try:
            ticker = self.get_ticker(symbol)
            if not ticker:
                return None
            
            if side == 'buy':
                # For buy orders, we pay the ask price
                execution_price = ticker['ask']
                mid_price = (ticker['bid'] + ticker['ask']) / 2
            else:
                # For sell orders, we get the bid price
                execution_price = ticker['bid']
                mid_price = (ticker['bid'] + ticker['ask']) / 2
            
            slippage_pct = abs(execution_price - mid_price) / mid_price * 100
            return {
                'estimated_price': execution_price,
                'mid_price': mid_price,
                'slippage_pct': slippage_pct,
                'acceptable': slippage_pct < 0.5  # Accept if < 0.5% slippage
            }
        except Exception as e:
            logger.error(f"Error calculating slippage: {str(e)}")
            return None
    
    def get_market_conditions(self):
        """
        Analyze current market conditions
        """
        try:
            tickers = self.get_all_tickers()
            
            # Calculate average price change
            price_changes = []
            for pair, ticker in tickers.items():
                if ticker:
                    change_pct = ((ticker['price'] - ticker['low_24h']) / ticker['low_24h']) * 100
                    price_changes.append(change_pct)
            
            avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
            
            # Determine market condition
            if avg_change > 5:
                condition = 'bullish'
            elif avg_change < -5:
                condition = 'bearish'
            else:
                condition = 'neutral'
            
            return {
                'condition': condition,
                'avg_24h_change': round(avg_change, 2),
                'volatility': 'high' if abs(avg_change) > 5 else 'low',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {str(e)}")
            return None
    
    def get_exchange_status(self):
        """
        Get Kraken exchange status
        """
        try:
            status = self.kraken.status()
            return {
                'status': status.get('status'),
                'updated': status.get('updated'),
                'ok': status.get('status') == 'ok'
            }
        except Exception as e:
            logger.error(f"Error getting exchange status: {str(e)}")
            return {'ok': False, 'error': str(e)}


# Initialize global exchange manager
exchange_manager = ExchangeManager()
