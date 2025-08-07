"""
Advanced Risk Management Dashboard for Enigma-Apex Pro
Real-time risk monitoring with prop firm compliance features
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np
from pathlib import Path

@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    account_balance: float
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    max_drawdown: float
    current_drawdown: float
    sharpe_ratio: float
    win_rate: float
    risk_score: int  # 1-100
    kelly_percentage: float
    
@dataclass
class PositionRisk:
    """Individual position risk data"""
    symbol: str
    position_size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    risk_percentage: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    time_in_position: int  # minutes

class AdvancedRiskManager:
    """Professional risk management system for prop trading"""
    
    def __init__(self, db_path: str = 'enigma_apex_pro.db'):
        self.db_path = db_path
        self.risk_limits = {
            'max_daily_loss': 1000,  # $1000 daily loss limit
            'max_weekly_loss': 3000,  # $3000 weekly loss limit
            'max_monthly_loss': 10000,  # $10000 monthly loss limit
            'max_position_risk': 2.0,  # 2% risk per position
            'max_portfolio_risk': 6.0,  # 6% total portfolio risk
            'max_drawdown': 8.0,  # 8% maximum drawdown
            'min_win_rate': 50.0,  # Minimum 50% win rate
            'max_correlation': 0.7,  # Maximum position correlation
        }
        
        self.current_positions: List[PositionRisk] = []
        self.risk_alerts: List[Dict] = []
        self.performance_metrics = {}
        
        # Kelly history tracking (FIX for error)
        self.kelly_history: List[Dict] = []
        self.kelly_calculations = {}
        self.kelly_performance_tracking = True
        
        self._init_database()
    
    def _init_database(self):
        """Initialize risk management database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Risk metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    account_balance REAL,
                    daily_pnl REAL,
                    weekly_pnl REAL,
                    monthly_pnl REAL,
                    max_drawdown REAL,
                    current_drawdown REAL,
                    sharpe_ratio REAL,
                    win_rate REAL,
                    risk_score INTEGER,
                    kelly_percentage REAL
                )
            ''')
            
            # Position risk table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS position_risk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    position_size REAL,
                    entry_price REAL,
                    current_price REAL,
                    unrealized_pnl REAL,
                    risk_percentage REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    time_in_position INTEGER
                )
            ''')
            
            # Risk alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    auto_action TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Risk management database initialized")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    async def calculate_kelly_criterion_historical(self, symbol: str, lookback_days: int = 30) -> float:
        """Calculate optimal position size using Kelly Criterion from historical data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get historical trade data
            query = '''
                SELECT * FROM trade_performance 
                WHERE symbol = ? AND timestamp > datetime('now', '-{} days')
            '''.format(lookback_days)
            
            df = pd.read_sql_query(query, conn, params=(symbol,))
            conn.close()
            
            if len(df) < 10:  # Need minimum trades for reliable calculation
                return 0.01  # Conservative 1% default
            
            # Calculate win rate and average win/loss
            wins = df[df['pnl'] > 0]['pnl']
            losses = df[df['pnl'] < 0]['pnl'].abs()
            
            if len(wins) == 0 or len(losses) == 0:
                return 0.01
            
            win_rate = len(wins) / len(df)
            avg_win = wins.mean()
            avg_loss = losses.mean()
            
            # Kelly formula: f* = (bp - q) / b
            # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
            b = avg_win / avg_loss
            p = win_rate
            q = 1 - win_rate
            
            kelly_fraction = (b * p - q) / b
            
            # Apply safety constraints
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            
            return kelly_fraction
            
        except Exception as e:
            print(f"❌ Kelly calculation error: {e}")
            return 0.01
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float = 1.0) -> float:
        """
        Calculate Kelly Criterion for position sizing (simple version for testing)
        
        Kelly % = (bp - q) / b
        where:
        b = odds received on the wager (avg_win / avg_loss)
        p = probability of winning (win_rate)
        q = probability of losing (1 - win_rate)
        """
        if win_rate <= 0 or win_rate >= 1:
            return 0.0
            
        if avg_win <= 0 or avg_loss <= 0:
            return 0.0
        
        # Kelly formula: (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Apply safety constraints (Half-Kelly + max 25%)
        kelly_fraction = max(0, min(kelly_fraction, 0.25))
        half_kelly = kelly_fraction / 2
        
        # Store in history if available (FIX for Kelly history tracking)
        if hasattr(self, 'kelly_history'):
            from datetime import datetime as dt
            self.kelly_history.append({
                'timestamp': dt.now(),
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'kelly_fraction': kelly_fraction,
                'half_kelly': half_kelly
            })
            
            # Keep only last 100 calculations
            if len(self.kelly_history) > 100:
                self.kelly_history = self.kelly_history[-100:]
        
        return half_kelly
    
    async def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get account balance (latest)
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(account_balance) FROM system_metrics')
            account_balance = cursor.fetchone()[0] or 10000  # Default $10k
            
            # Calculate P&L periods
            daily_pnl = self._calculate_period_pnl(conn, days=1)
            weekly_pnl = self._calculate_period_pnl(conn, days=7)
            monthly_pnl = self._calculate_period_pnl(conn, days=30)
            
            # Calculate drawdown
            max_drawdown, current_drawdown = self._calculate_drawdown(conn)
            
            # Calculate Sharpe ratio
            sharpe_ratio = self._calculate_sharpe_ratio(conn)
            
            # Calculate win rate
            win_rate = self._calculate_win_rate(conn)
            
            # Calculate overall risk score (1-100)
            risk_score = self._calculate_risk_score(
                current_drawdown, daily_pnl, win_rate, account_balance
            )
            
            # Average Kelly percentage across all symbols
            kelly_percentage = await self._calculate_average_kelly()
            
            conn.close()
            
            return RiskMetrics(
                account_balance=account_balance,
                daily_pnl=daily_pnl,
                weekly_pnl=weekly_pnl,
                monthly_pnl=monthly_pnl,
                max_drawdown=max_drawdown,
                current_drawdown=current_drawdown,
                sharpe_ratio=sharpe_ratio,
                win_rate=win_rate,
                risk_score=risk_score,
                kelly_percentage=kelly_percentage
            )
            
        except Exception as e:
            print(f"❌ Risk metrics calculation error: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 50, 0.01)
    
    def _calculate_period_pnl(self, conn, days: int) -> float:
        """Calculate P&L for specified period"""
        query = '''
            SELECT SUM(pnl) FROM trade_performance 
            WHERE timestamp > datetime('now', '-{} days')
        '''.format(days)
        
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return result or 0.0
    
    def _calculate_drawdown(self, conn) -> tuple:
        """Calculate maximum and current drawdown"""
        query = '''
            SELECT timestamp, SUM(pnl) OVER (ORDER BY timestamp) as cumulative_pnl
            FROM trade_performance 
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(query, conn)
        
        if len(df) == 0:
            return 0.0, 0.0
        
        # Calculate running maximum
        running_max = df['cumulative_pnl'].expanding().max()
        drawdown = (df['cumulative_pnl'] - running_max) / running_max * 100
        
        max_drawdown = abs(drawdown.min())
        current_drawdown = abs(drawdown.iloc[-1])
        
        return max_drawdown, current_drawdown
    
    def _calculate_sharpe_ratio(self, conn, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        query = '''
            SELECT pnl FROM trade_performance 
            WHERE timestamp > datetime('now', '-30 days')
        '''
        
        df = pd.read_sql_query(query, conn)
        
        if len(df) < 10:
            return 0.0
        
        returns = df['pnl']
        excess_returns = returns.mean() - (risk_free_rate / 252)  # Daily risk-free rate
        
        if returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns / returns.std() * np.sqrt(252)  # Annualized
        return sharpe
    
    def _calculate_win_rate(self, conn) -> float:
        """Calculate win rate percentage"""
        query = '''
            SELECT 
                COUNT(CASE WHEN pnl > 0 THEN 1 END) as wins,
                COUNT(*) as total
            FROM trade_performance 
            WHERE timestamp > datetime('now', '-30 days')
        '''
        
        cursor = conn.cursor()
        cursor.execute(query)
        wins, total = cursor.fetchone()
        
        if total == 0:
            return 0.0
        
        return (wins / total) * 100
    
    def _calculate_risk_score(self, drawdown: float, daily_pnl: float, 
                            win_rate: float, account_balance: float) -> int:
        """Calculate overall risk score (1-100, higher is riskier)"""
        score = 50  # Base score
        
        # Drawdown impact (30% weight)
        if drawdown > 10:
            score += 30
        elif drawdown > 5:
            score += 15
        elif drawdown < 2:
            score -= 10
        
        # Daily P&L impact (25% weight)
        daily_risk = abs(daily_pnl) / account_balance * 100
        if daily_risk > 5:
            score += 25
        elif daily_risk > 2:
            score += 10
        elif daily_risk < 0.5:
            score -= 5
        
        # Win rate impact (25% weight)
        if win_rate < 40:
            score += 25
        elif win_rate < 50:
            score += 10
        elif win_rate > 70:
            score -= 15
        
        # Additional risk factors (20% weight)
        if account_balance < 5000:
            score += 20
        elif account_balance > 50000:
            score -= 10
        
        return max(1, min(100, score))
    
    async def _calculate_average_kelly(self) -> float:
        """Calculate average Kelly percentage across active symbols"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT DISTINCT symbol FROM trading_signals')
            symbols = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not symbols:
                return 0.01
            
            kelly_values = []
            for symbol in symbols:
                kelly = await self.calculate_kelly_criterion_historical(symbol)
                kelly_values.append(kelly)
            
            return np.mean(kelly_values)
            
        except Exception as e:
            print(f"❌ Average Kelly calculation error: {e}")
            return 0.01
    
    async def check_risk_violations(self, metrics: RiskMetrics) -> List[Dict]:
        """Check for risk limit violations"""
        violations = []
        
        # Daily loss limit
        if metrics.daily_pnl < -self.risk_limits['max_daily_loss']:
            violations.append({
                'type': 'daily_loss_limit',
                'severity': 'CRITICAL',
                'message': f'Daily loss ${abs(metrics.daily_pnl):.2f} exceeds limit ${self.risk_limits["max_daily_loss"]}',
                'auto_action': 'close_all_positions'
            })
        
        # Weekly loss limit
        if metrics.weekly_pnl < -self.risk_limits['max_weekly_loss']:
            violations.append({
                'type': 'weekly_loss_limit',
                'severity': 'HIGH',
                'message': f'Weekly loss ${abs(metrics.weekly_pnl):.2f} exceeds limit ${self.risk_limits["max_weekly_loss"]}',
                'auto_action': 'reduce_position_sizes'
            })
        
        # Maximum drawdown
        if metrics.current_drawdown > self.risk_limits['max_drawdown']:
            violations.append({
                'type': 'max_drawdown',
                'severity': 'CRITICAL',
                'message': f'Drawdown {metrics.current_drawdown:.2f}% exceeds limit {self.risk_limits["max_drawdown"]}%',
                'auto_action': 'close_all_positions'
            })
        
        # Low win rate
        if metrics.win_rate < self.risk_limits['min_win_rate']:
            violations.append({
                'type': 'low_win_rate',
                'severity': 'MEDIUM',
                'message': f'Win rate {metrics.win_rate:.1f}% below minimum {self.risk_limits["min_win_rate"]}%',
                'auto_action': 'review_strategy'
            })
        
        # High risk score
        if metrics.risk_score > 80:
            violations.append({
                'type': 'high_risk_score',
                'severity': 'HIGH',
                'message': f'Risk score {metrics.risk_score} indicates high portfolio risk',
                'auto_action': 'reduce_position_sizes'
            })
        
        return violations
    
    async def save_risk_alert(self, alert: Dict):
        """Save risk alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO risk_alerts (alert_type, severity, message, auto_action)
                VALUES (?, ?, ?, ?)
            ''', (alert['type'], alert['severity'], alert['message'], alert['auto_action']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving risk alert: {e}")
    
    async def get_risk_dashboard_data(self) -> Dict:
        """Get comprehensive risk dashboard data"""
        try:
            # Calculate current metrics
            metrics = await self.calculate_risk_metrics()
            
            # Check for violations
            violations = await self.check_risk_violations(metrics)
            
            # Save any new violations
            for violation in violations:
                await self.save_risk_alert(violation)
            
            # Get recent alerts
            conn = sqlite3.connect(self.db_path)
            recent_alerts = pd.read_sql_query('''
                SELECT * FROM risk_alerts 
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC LIMIT 10
            ''', conn)
            conn.close()
            
            return {
                'metrics': {
                    'account_balance': metrics.account_balance,
                    'daily_pnl': metrics.daily_pnl,
                    'weekly_pnl': metrics.weekly_pnl,
                    'monthly_pnl': metrics.monthly_pnl,
                    'max_drawdown': metrics.max_drawdown,
                    'current_drawdown': metrics.current_drawdown,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'win_rate': metrics.win_rate,
                    'risk_score': metrics.risk_score,
                    'kelly_percentage': metrics.kelly_percentage
                },
                'violations': violations,
                'recent_alerts': recent_alerts.to_dict('records') if not recent_alerts.empty else [],
                'risk_limits': self.risk_limits,
                'status': 'SAFE' if len(violations) == 0 else 'WARNING' if any(v['severity'] in ['MEDIUM', 'HIGH'] for v in violations) else 'CRITICAL',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error generating dashboard data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

async def main():
    """Test the advanced risk management system"""
    print("🛡️  TESTING ADVANCED RISK MANAGEMENT SYSTEM")
    print("=" * 50)
    
    risk_manager = AdvancedRiskManager()
    
    # Get dashboard data
    dashboard_data = await risk_manager.get_risk_dashboard_data()
    
    print("📊 RISK DASHBOARD SUMMARY")
    print("-" * 30)
    
    if 'error' in dashboard_data:
        print(f"❌ Error: {dashboard_data['error']}")
        return
    
    metrics = dashboard_data['metrics']
    print(f"💰 Account Balance: ${metrics['account_balance']:,.2f}")
    print(f"📈 Daily P&L: ${metrics['daily_pnl']:,.2f}")
    print(f"📊 Weekly P&L: ${metrics['weekly_pnl']:,.2f}")
    print(f"📅 Monthly P&L: ${metrics['monthly_pnl']:,.2f}")
    print(f"📉 Current Drawdown: {metrics['current_drawdown']:.2f}%")
    print(f"🎯 Win Rate: {metrics['win_rate']:.1f}%")
    print(f"⚡ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"🎲 Kelly %: {metrics['kelly_percentage']:.1f}%")
    print(f"🛡️  Risk Score: {metrics['risk_score']}/100")
    
    print(f"\n🚦 SYSTEM STATUS: {dashboard_data['status']}")
    
    if dashboard_data['violations']:
        print(f"\n⚠️  RISK VIOLATIONS ({len(dashboard_data['violations'])})")
        for violation in dashboard_data['violations']:
            severity_emoji = "🔴" if violation['severity'] == 'CRITICAL' else "🟡" if violation['severity'] == 'HIGH' else "🟠"
            print(f"  {severity_emoji} {violation['message']}")
            print(f"     Action: {violation['auto_action']}")
    else:
        print("\n✅ NO RISK VIOLATIONS")
    
    print(f"\n📋 Recent Alerts: {len(dashboard_data['recent_alerts'])}")
    
    print("\n🎯 NEXT STEPS:")
    if dashboard_data['status'] == 'CRITICAL':
        print("  1. IMMEDIATE: Review all open positions")
        print("  2. IMMEDIATE: Consider closing high-risk trades")
        print("  3. IMMEDIATE: Reduce position sizes")
    elif dashboard_data['status'] == 'WARNING':
        print("  1. Monitor positions closely")
        print("  2. Avoid new high-risk trades")
        print("  3. Consider partial profit taking")
    else:
        print("  1. Continue normal trading operations")
        print("  2. Monitor for new opportunities")
        print("  3. Consider increasing position sizes (within limits)")

if __name__ == "__main__":
    asyncio.run(main())
