#!/usr/bin/env python3
"""
Monitoring & Logging System
Comprehensive logging, health checks, and system monitoring
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

class MonitoringSystem:
    """
    Production-grade monitoring and logging
    """
    
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup all logging handlers"""
        
        # Main application logger
        self.app_logger = self.create_logger(
            'app',
            'app.log',
            logging.INFO
        )
        
        # Trading logger (detailed trade info)
        self.trading_logger = self.create_logger(
            'trading',
            'trading.log',
            logging.INFO
        )
        
        # Error logger (errors and warnings)
        self.error_logger = self.create_logger(
            'error',
            'error.log',
            logging.WARNING
        )
        
        # API logger (Kraken API calls)
        self.api_logger = self.create_logger(
            'api',
            'api.log',
            logging.DEBUG
        )
        
        # Risk logger (risk management events)
        self.risk_logger = self.create_logger(
            'risk',
            'risk.log',
            logging.INFO
        )
    
    def create_logger(self, name, filename, level):
        """Create a logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # File handler (rotating)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_trade(self, bot_id, symbol, side, entry_price, position_size):
        """Log trade execution"""
        self.trading_logger.info(
            f"Trade: {bot_id} | {side.upper()} {position_size} {symbol} @ ${entry_price:.2f}"
        )
    
    def log_api_call(self, endpoint, method, status):
        """Log API call"""
        self.api_logger.debug(
            f"API: {method} {endpoint} | Status: {status}"
        )
    
    def log_risk_event(self, event_type, message):
        """Log risk management event"""
        self.risk_logger.warning(f"{event_type}: {message}")
    
    def log_error(self, error_type, message, details=None):
        """Log error"""
        if details:
            self.error_logger.error(f"{error_type}: {message} | Details: {details}")
        else:
            self.error_logger.error(f"{error_type}: {message}")
    
    def get_log_file(self, log_type):
        """Get path to log file"""
        log_files = {
            'app': 'app.log',
            'trading': 'trading.log',
            'error': 'error.log',
            'api': 'api.log',
            'risk': 'risk.log'
        }
        return self.log_dir / log_files.get(log_type, 'app.log')


class HealthChecker:
    """
    System health monitoring
    """
    
    def __init__(self):
        self.checks = {}
        self.last_check = None
    
    def check_kraken_connection(self, exchange_manager):
        """Check Kraken API connection"""
        try:
            balance = exchange_manager.get_balance()
            return balance is not None
        except Exception as e:
            return False
    
    def check_database(self, db):
        """Check database connectivity"""
        try:
            stats = db.get_statistics()
            return stats is not None
        except Exception as e:
            return False
    
    def check_risk_manager(self, risk_manager):
        """Check risk manager status"""
        try:
            metrics = risk_manager.get_risk_metrics()
            return metrics is not None
        except Exception as e:
            return False
    
    def run_all_checks(self, exchange_manager, db, risk_manager):
        """Run all health checks"""
        self.checks = {
            'kraken_api': self.check_kraken_connection(exchange_manager),
            'database': self.check_database(db),
            'risk_manager': self.check_risk_manager(risk_manager)
        }
        self.last_check = datetime.now()
        
        return self.checks
    
    def is_healthy(self):
        """Check if system is healthy"""
        return all(self.checks.values())
    
    def get_status(self):
        """Get health status"""
        return {
            'healthy': self.is_healthy(),
            'checks': self.checks,
            'last_check': self.last_check.isoformat() if self.last_check else None
        }


class PerformanceMonitor:
    """
    Track system performance metrics
    """
    
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'trades_executed': 0,
            'errors': 0,
            'avg_response_time': 0,
            'uptime_seconds': 0
        }
        self.start_time = datetime.now()
    
    def record_api_call(self, response_time):
        """Record API call"""
        self.metrics['api_calls'] += 1
        # Update average response time
        current_avg = self.metrics['avg_response_time']
        total_calls = self.metrics['api_calls']
        self.metrics['avg_response_time'] = (
            (current_avg * (total_calls - 1) + response_time) / total_calls
        )
    
    def record_trade(self):
        """Record trade execution"""
        self.metrics['trades_executed'] += 1
    
    def record_error(self):
        """Record error"""
        self.metrics['errors'] += 1
    
    def get_metrics(self):
        """Get performance metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        self.metrics['uptime_seconds'] = uptime
        
        return {
            **self.metrics,
            'uptime_hours': round(uptime / 3600, 2)
        }


# Initialize global monitoring
monitoring = MonitoringSystem()
health_checker = HealthChecker()
performance_monitor = PerformanceMonitor()
