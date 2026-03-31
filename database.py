#!/usr/bin/env python3
"""
Database Layer - SQLite for persistent storage
Tracks trades, performance, alerts, and system events
"""

import sqlite3
import json
import logging
from datetime import datetime
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """
    SQLite database for trading system
    """
    
    def __init__(self, db_path='crypto_bot.db'):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    bot_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    position_size REAL NOT NULL,
                    profit_loss REAL,
                    status TEXT DEFAULT 'open',
                    strategy TEXT,
                    notes TEXT
                )
            ''')
            
            # Bot configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT DEFAULT 'running',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    bot_id TEXT NOT NULL,
                    win_rate REAL,
                    profit_loss REAL,
                    total_trades INTEGER,
                    sharpe_ratio REAL,
                    max_drawdown REAL
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    bot_id TEXT,
                    action_taken TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
            ''')
            
            # System events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT,
                    details TEXT
                )
            ''')
            
            # Account balance history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    balance REAL NOT NULL,
                    peak_balance REAL,
                    drawdown_pct REAL
                )
            ''')
            
            logger.info("✅ Database initialized")
    
    # ========== TRADES ==========
    
    def record_trade(self, bot_id, symbol, side, entry_price, position_size, strategy):
        """Record a new trade"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades 
                (timestamp, bot_id, symbol, side, entry_price, position_size, status, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                bot_id,
                symbol,
                side,
                entry_price,
                position_size,
                'open',
                strategy
            ))
            return cursor.lastrowid
    
    def close_trade(self, trade_id, exit_price, profit_loss):
        """Close an open trade"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, profit_loss = ?, status = ?
                WHERE id = ?
            ''', (exit_price, profit_loss, 'closed', trade_id))
    
    def get_trades(self, bot_id=None, limit=100):
        """Get trade history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if bot_id:
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE bot_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (bot_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM trades 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_open_trades(self, bot_id=None):
        """Get open trades"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if bot_id:
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE status = 'open' AND bot_id = ?
                ''', (bot_id,))
            else:
                cursor.execute('''
                    SELECT * FROM trades 
                    WHERE status = 'open'
                ''')
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== BOT CONFIGS ==========
    
    def save_bot_config(self, bot_id, name, strategy, parameters):
        """Save bot configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO bot_configs 
                (bot_id, name, strategy, parameters, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                bot_id,
                name,
                strategy,
                json.dumps(parameters),
                now,
                now
            ))
    
    def get_bot_config(self, bot_id):
        """Get bot configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bot_configs WHERE bot_id = ?', (bot_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['parameters'] = json.loads(result['parameters'])
                return result
            return None
    
    # ========== PERFORMANCE METRICS ==========
    
    def record_performance(self, bot_id, win_rate, profit_loss, total_trades, sharpe_ratio, max_drawdown):
        """Record bot performance metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, bot_id, win_rate, profit_loss, total_trades, sharpe_ratio, max_drawdown)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                bot_id,
                win_rate,
                profit_loss,
                total_trades,
                sharpe_ratio,
                max_drawdown
            ))
    
    def get_performance_history(self, bot_id, days=7):
        """Get performance history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM performance_metrics 
                WHERE bot_id = ? AND timestamp > datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            ''', (bot_id, days))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== ALERTS ==========
    
    def record_alert(self, level, message, bot_id=None, action_taken=None):
        """Record an alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts 
                (timestamp, level, message, bot_id, action_taken)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                level,
                message,
                bot_id,
                action_taken
            ))
            return cursor.lastrowid
    
    def get_alerts(self, limit=50, unresolved_only=False):
        """Get alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if unresolved_only:
                cursor.execute('''
                    SELECT * FROM alerts 
                    WHERE resolved = 0
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            else:
                cursor.execute('''
                    SELECT * FROM alerts 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def resolve_alert(self, alert_id):
        """Mark alert as resolved"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE alerts SET resolved = 1 WHERE id = ?', (alert_id,))
    
    # ========== SYSTEM EVENTS ==========
    
    def record_event(self, event_type, description, details=None):
        """Record system event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_events 
                (timestamp, event_type, description, details)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                event_type,
                description,
                json.dumps(details) if details else None
            ))
    
    def get_events(self, event_type=None, limit=100):
        """Get system events"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if event_type:
                cursor.execute('''
                    SELECT * FROM system_events 
                    WHERE event_type = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (event_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM system_events 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== BALANCE HISTORY ==========
    
    def record_balance(self, balance, peak_balance, drawdown_pct):
        """Record account balance"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO balance_history 
                (timestamp, balance, peak_balance, drawdown_pct)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                balance,
                peak_balance,
                drawdown_pct
            ))
    
    def get_balance_history(self, days=7):
        """Get balance history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM balance_history 
                WHERE timestamp > datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            ''', (days,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== STATISTICS ==========
    
    def get_statistics(self):
        """Get overall statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total trades
            cursor.execute('SELECT COUNT(*) as count FROM trades')
            total_trades = cursor.fetchone()['count']
            
            # Closed trades
            cursor.execute('SELECT COUNT(*) as count FROM trades WHERE status = "closed"')
            closed_trades = cursor.fetchone()['count']
            
            # Total profit/loss
            cursor.execute('SELECT SUM(profit_loss) as total FROM trades WHERE status = "closed"')
            total_pl = cursor.fetchone()['total'] or 0
            
            # Win rate
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins
                FROM trades WHERE status = "closed"
            ''')
            row = cursor.fetchone()
            win_rate = (row['wins'] / row['total'] * 100) if row['total'] > 0 else 0
            
            return {
                'total_trades': total_trades,
                'closed_trades': closed_trades,
                'open_trades': total_trades - closed_trades,
                'total_profit_loss': round(total_pl, 2),
                'win_rate': round(win_rate, 2)
            }


# Initialize global database
db = Database('crypto_bot.db')
