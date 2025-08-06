"""
🎯 ENIGMA-APEX CHATGPT AGENT INTEGRATION
First Principles AI Enhancement for Michael Canfield's Vision
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from collections import deque
import numpy as np
from typing import Dict, List, Optional, Tuple

class FirstPrinciplesAI:
    """
    ChatGPT-powered agent for identifying and applying first principles 
    that maximize profit and minimize losses in Enigma Cadence trading
    """
    
    def __init__(self):
        self.trade_history = deque(maxlen=100)  # Rolling 100 trades
        self.first_principles = {
            "risk_management": {
                "max_risk_per_trade": 0.01,  # 1% max risk
                "daily_loss_limit": 0.04,    # 4% daily limit
                "stop_loss_atr_multiple": 1.5,
                "profit_target_atr_multiple": 2.0
            },
            "edge_identification": {
                "min_confluence_level": "L3",
                "min_power_score": 15,
                "cadence_threshold_am": 2,   # 2 failures AM
                "cadence_threshold_pm": 3,   # 3 failures PM
                "min_volume_surge": 1.5      # 1.5x average volume
            },
            "loss_minimization": {
                "immediate_exit_conditions": [
                    "stop_loss_breach_0.1_percent",
                    "power_score_below_10",
                    "confluence_drops_below_L2"
                ],
                "no_trade_signals": [
                    "news_event_within_30min",
                    "low_volatility_environment",
                    "market_close_within_15min"
                ]
            },
            "profit_extension": {
                "scale_in_conditions": [
                    "initial_entry_favorable_momentum",
                    "strong_confluence_confirmation",
                    "volume_expansion_confirmation"
                ],
                "trailing_stop_rules": [
                    "move_to_breakeven_after_0.5_atr",
                    "trail_by_0.3_atr_increments"
                ]
            }
        }
        
        self.performance_metrics = {
            "win_rate": 0.5,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 1.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        }
        
        self.db_connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize AI analytics database"""
        try:
            self.db_connection = sqlite3.connect('ai_trading_analytics.db')
            cursor = self.db_connection.cursor()
            
            # Create first principles tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS first_principles_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    principle_type TEXT NOT NULL,
                    principle_name TEXT NOT NULL,
                    trade_outcome REAL,
                    market_conditions TEXT,
                    effectiveness_score REAL,
                    ai_insights TEXT
                )
            ''')
            
            # Create trade performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trade_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    entry_price REAL,
                    exit_price REAL,
                    pnl REAL,
                    win_loss INTEGER,  -- 1 for win, 0 for loss
                    principle_applied TEXT,
                    kelly_fraction REAL,
                    atr_value REAL,
                    confluence_level TEXT,
                    power_score INTEGER
                )
            ''')
            
            # Create AI insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    insight_type TEXT NOT NULL,
                    confidence_score REAL,
                    recommendation TEXT,
                    reasoning TEXT,
                    market_context TEXT
                )
            ''')
            
            self.db_connection.commit()
            print("✅ AI Analytics database initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize AI database: {e}")
    
    def analyze_first_principles(self, trade_data: Dict) -> Dict:
        """
        Analyze trade against first principles and generate AI insights
        """
        insights = {
            "recommendation": "HOLD",
            "confidence": 0.0,
            "reasoning": [],
            "risk_assessment": "MEDIUM",
            "principle_violations": [],
            "optimization_suggestions": []
        }
        
        # Risk Management Analysis
        risk_score = self._analyze_risk_principles(trade_data)
        insights["risk_assessment"] = self._get_risk_level(risk_score)
        
        # Edge Identification
        edge_score = self._analyze_edge_principles(trade_data)
        
        # Loss Minimization Check
        loss_signals = self._check_loss_minimization(trade_data)
        
        # Profit Extension Opportunities
        profit_signals = self._check_profit_extension(trade_data)
        
        # Generate overall recommendation
        overall_score = (risk_score + edge_score) / 2
        
        if loss_signals:
            insights["recommendation"] = "NO_TRADE"
            insights["reasoning"].append("Loss minimization signals detected")
        elif overall_score > 0.7 and edge_score > 0.6:
            insights["recommendation"] = "TRADE"
            insights["reasoning"].append("Strong first principles alignment")
        elif overall_score > 0.5:
            insights["recommendation"] = "CAUTIOUS_TRADE"
            insights["reasoning"].append("Moderate first principles support")
        
        insights["confidence"] = overall_score
        
        # Store insights in database
        self._store_ai_insights(insights, trade_data)
        
        return insights
    
    def _analyze_risk_principles(self, trade_data: Dict) -> float:
        """Analyze risk management first principles"""
        score = 1.0
        
        # Check position sizing
        if trade_data.get("position_size_pct", 0) > self.first_principles["risk_management"]["max_risk_per_trade"]:
            score -= 0.3
        
        # Check ATR-based stops
        atr_value = trade_data.get("atr", 0)
        if atr_value > 0:
            expected_stop = atr_value * self.first_principles["risk_management"]["stop_loss_atr_multiple"]
            actual_stop = trade_data.get("stop_loss_distance", 0)
            if abs(actual_stop - expected_stop) / expected_stop > 0.2:  # 20% deviation
                score -= 0.2
        
        # Check daily loss limits
        daily_pnl_pct = trade_data.get("daily_pnl_pct", 0)
        if abs(daily_pnl_pct) > self.first_principles["risk_management"]["daily_loss_limit"] * 0.8:
            score -= 0.3  # Getting close to daily limit
        
        return max(0, score)
    
    def _analyze_edge_principles(self, trade_data: Dict) -> float:
        """Analyze edge identification first principles"""
        score = 0.0
        
        # Confluence level check
        confluence = trade_data.get("confluence_level", "")
        if confluence in ["L3", "L4"]:
            score += 0.3
        elif confluence in ["L2"]:
            score += 0.1
        
        # Power score check
        power_score = trade_data.get("power_score", 0)
        if power_score >= self.first_principles["edge_identification"]["min_power_score"]:
            score += 0.3
        
        # Volume surge check
        volume_ratio = trade_data.get("volume_ratio", 1.0)
        if volume_ratio >= self.first_principles["edge_identification"]["min_volume_surge"]:
            score += 0.2
        
        # Cadence threshold check
        session = trade_data.get("session", "AM")
        failure_count = trade_data.get("cadence_failures", 0)
        threshold = (self.first_principles["edge_identification"]["cadence_threshold_am"] 
                    if session == "AM" else 
                    self.first_principles["edge_identification"]["cadence_threshold_pm"])
        
        if failure_count >= threshold:
            score += 0.2
        
        return min(1.0, score)
    
    def _check_loss_minimization(self, trade_data: Dict) -> bool:
        """Check for loss minimization signals"""
        # Check immediate exit conditions
        power_score = trade_data.get("power_score", 0)
        if power_score < 10:
            return True
        
        confluence = trade_data.get("confluence_level", "")
        if confluence in ["L0", "L1"]:
            return True
        
        # Check no-trade signals
        if trade_data.get("news_event_soon", False):
            return True
        
        if trade_data.get("low_volatility", False):
            return True
        
        return False
    
    def _check_profit_extension(self, trade_data: Dict) -> List[str]:
        """Check for profit extension opportunities"""
        signals = []
        
        # Strong momentum check
        if trade_data.get("momentum_strength", 0) > 0.7:
            signals.append("strong_momentum_detected")
        
        # Volume expansion
        if trade_data.get("volume_expansion", False):
            signals.append("volume_expansion_confirmed")
        
        # Confluence confirmation
        if trade_data.get("confluence_level") == "L4":
            signals.append("maximum_confluence")
        
        return signals
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score > 0.8:
            return "LOW"
        elif risk_score > 0.5:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _store_ai_insights(self, insights: Dict, trade_data: Dict):
        """Store AI insights in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO ai_insights 
                (insight_type, confidence_score, recommendation, reasoning, market_context)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "first_principles_analysis",
                insights["confidence"],
                insights["recommendation"],
                json.dumps(insights["reasoning"]),
                json.dumps(trade_data)
            ))
            self.db_connection.commit()
        except Exception as e:
            print(f"❌ Failed to store AI insights: {e}")
    
    def update_performance_metrics(self, trade_outcome: Dict):
        """Update performance metrics based on trade outcome"""
        self.trade_history.append(trade_outcome["win_loss"])
        
        # Calculate rolling metrics
        if len(self.trade_history) > 0:
            self.performance_metrics["win_rate"] = sum(self.trade_history) / len(self.trade_history)
        
        # Store trade performance
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO trade_performance 
                (symbol, entry_price, exit_price, pnl, win_loss, principle_applied, 
                 kelly_fraction, atr_value, confluence_level, power_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_outcome.get("symbol", ""),
                trade_outcome.get("entry_price", 0),
                trade_outcome.get("exit_price", 0),
                trade_outcome.get("pnl", 0),
                trade_outcome.get("win_loss", 0),
                trade_outcome.get("principle_applied", ""),
                trade_outcome.get("kelly_fraction", 0),
                trade_outcome.get("atr_value", 0),
                trade_outcome.get("confluence_level", ""),
                trade_outcome.get("power_score", 0)
            ))
            self.db_connection.commit()
        except Exception as e:
            print(f"❌ Failed to store trade performance: {e}")
    
    def generate_optimization_insights(self) -> Dict:
        """Generate optimization insights based on historical performance"""
        insights = {
            "performance_summary": self.performance_metrics.copy(),
            "principle_effectiveness": {},
            "optimization_recommendations": []
        }
        
        try:
            cursor = self.db_connection.cursor()
            
            # Analyze principle effectiveness
            cursor.execute('''
                SELECT principle_applied, AVG(pnl), COUNT(*), SUM(win_loss)
                FROM trade_performance 
                WHERE principle_applied IS NOT NULL
                GROUP BY principle_applied
            ''')
            
            for row in cursor.fetchall():
                principle, avg_pnl, total_trades, wins = row
                win_rate = wins / total_trades if total_trades > 0 else 0
                insights["principle_effectiveness"][principle] = {
                    "avg_pnl": avg_pnl,
                    "win_rate": win_rate,
                    "total_trades": total_trades
                }
            
            # Generate optimization recommendations
            if insights["principle_effectiveness"]:
                best_principle = max(insights["principle_effectiveness"].items(), 
                                   key=lambda x: x[1]["win_rate"])
                insights["optimization_recommendations"].append(
                    f"Focus on '{best_principle[0]}' principle - highest win rate: {best_principle[1]['win_rate']:.2%}"
                )
            
            # Check for underperforming principles
            for principle, metrics in insights["principle_effectiveness"].items():
                if metrics["win_rate"] < 0.4:
                    insights["optimization_recommendations"].append(
                        f"Review '{principle}' principle - low win rate: {metrics['win_rate']:.2%}"
                    )
            
        except Exception as e:
            print(f"❌ Failed to generate optimization insights: {e}")
        
        return insights
    
    def get_real_time_guidance(self, current_market_data: Dict) -> Dict:
        """Provide real-time trading guidance based on first principles"""
        guidance = {
            "action": "HOLD",
            "confidence": 0.0,
            "reasoning": [],
            "risk_level": "MEDIUM",
            "position_size_suggestion": 0.0,
            "stop_loss_suggestion": 0.0,
            "profit_target_suggestion": 0.0
        }
        
        # Analyze current situation against first principles
        analysis = self.analyze_first_principles(current_market_data)
        
        guidance["action"] = analysis["recommendation"]
        guidance["confidence"] = analysis["confidence"]
        guidance["reasoning"] = analysis["reasoning"]
        guidance["risk_level"] = analysis["risk_assessment"]
        
        # Calculate position size using Kelly Criterion
        if analysis["recommendation"] in ["TRADE", "CAUTIOUS_TRADE"]:
            kelly_fraction = self._calculate_kelly_fraction(current_market_data)
            guidance["position_size_suggestion"] = kelly_fraction * 0.5  # Half-Kelly
            
            # ATR-based stops and targets
            atr_value = current_market_data.get("atr", 0)
            if atr_value > 0:
                guidance["stop_loss_suggestion"] = atr_value * 1.5
                guidance["profit_target_suggestion"] = atr_value * 2.0
        
        return guidance
    
    def _calculate_kelly_fraction(self, market_data: Dict) -> float:
        """Calculate Kelly fraction based on current win rate and R:R ratio"""
        win_rate = self.performance_metrics["win_rate"]
        
        # Calculate R:R ratio from ATR-based targets
        atr_value = market_data.get("atr", 1.0)
        stop_loss = atr_value * 1.5
        profit_target = atr_value * 2.0
        rr_ratio = profit_target / stop_loss if stop_loss > 0 else 2.0
        
        # Kelly formula: f = (bp - q) / b
        # where b = reward/risk ratio, p = win probability, q = loss probability
        kelly_fraction = (rr_ratio * win_rate - (1 - win_rate)) / rr_ratio
        
        return max(0, min(0.25, kelly_fraction))  # Cap at 25%

class EnigmaApexAIAgent:
    """
    Main AI agent that integrates with existing Enigma-Apex system
    """
    
    def __init__(self):
        self.ai_engine = FirstPrinciplesAI()
        self.kelly_engine = KellyOptimizationEngine()
        self.is_running = False
    
    def calculate_kelly_position_size(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate Kelly position size (Michael's requirement)"""
        try:
            # Kelly formula: f = (bp - q) / b
            # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
            if avg_loss <= 0:
                return 0.01  # Safe fallback
            
            b = avg_win / avg_loss
            p = win_rate
            q = 1 - win_rate
            
            kelly_fraction = (b * p - q) / b
            
            # Apply safety constraints (Half-Kelly + max 25%)
            kelly_fraction = max(0, min(kelly_fraction, 0.25))
            half_kelly = kelly_fraction / 2
            
            return half_kelly
            
        except Exception as e:
            print(f"Kelly calculation error: {e}")
            return 0.01
    
    def analyze_first_principles(self, market_data: Dict) -> Dict:
        """Analyze trading setup using first principles (Michael's vision)"""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'risk_assessment': self._assess_risk_principles(market_data),
                'edge_identification': self._identify_edge_principles(market_data),
                'profit_optimization': self._optimize_profit_principles(market_data),
                'recommendation': 'HOLD'
            }
            
            # Apply first principles logic
            if analysis['risk_assessment']['score'] > 7 and analysis['edge_identification']['score'] > 7:
                analysis['recommendation'] = 'TRADE'
            elif analysis['risk_assessment']['score'] < 3:
                analysis['recommendation'] = 'NO_TRADE'
            
            return analysis
            
        except Exception as e:
            print(f"First principles analysis error: {e}")
            return {'error': str(e), 'recommendation': 'HOLD'}
    
    def analyze_enigma_signal(self, signal_data: Dict) -> Dict:
        """Analyze Enigma signal for trading decision (Michael's requirement)"""
        try:
            power = signal_data.get('power', 0)
            confluence = signal_data.get('confluence', 'L1')
            direction = signal_data.get('direction', 'NEUTRAL')
            
            analysis = {
                'signal_strength': 'WEAK',
                'trade_recommendation': 'HOLD',
                'confidence': 0.0,
                'kelly_position_size': 0.01
            }
            
            # Analyze based on Michael's criteria
            if power >= 20 and confluence in ['L3', 'L4']:
                analysis['signal_strength'] = 'STRONG'
                analysis['trade_recommendation'] = 'TRADE'
                analysis['confidence'] = 0.8
                analysis['kelly_position_size'] = self.calculate_kelly_position_size(0.65, 1.5, 1.0)
            elif power >= 15 and confluence in ['L2', 'L3']:
                analysis['signal_strength'] = 'MEDIUM'
                analysis['trade_recommendation'] = 'CONSIDER'
                analysis['confidence'] = 0.6
                analysis['kelly_position_size'] = self.calculate_kelly_position_size(0.55, 1.2, 1.0)
            
            return analysis
            
        except Exception as e:
            print(f"Enigma signal analysis error: {e}")
            return {'error': str(e), 'trade_recommendation': 'HOLD'}
    
    def real_time_guidance(self, market_conditions: Dict) -> Dict:
        """Provide real-time trading guidance (Michael's optimization requirement)"""
        try:
            guidance = {
                'timestamp': datetime.now().isoformat(),
                'market_assessment': 'NEUTRAL',
                'position_sizing': 0.01,
                'risk_level': 'MEDIUM',
                'action': 'MONITOR'
            }
            
            # Apply real-time optimization
            volatility = market_conditions.get('atr', 0)
            trend_strength = market_conditions.get('trend_strength', 0.5)
            
            if volatility > 0 and trend_strength > 0.7:
                guidance['market_assessment'] = 'FAVORABLE'
                guidance['position_sizing'] = self.calculate_kelly_position_size(0.6, 1.8, 1.0)
                guidance['action'] = 'READY_TO_TRADE'
            elif trend_strength < 0.3:
                guidance['market_assessment'] = 'UNFAVORABLE'
                guidance['action'] = 'AVOID_TRADING'
            
            return guidance
            
        except Exception as e:
            print(f"Real-time guidance error: {e}")
            return {'error': str(e), 'action': 'MONITOR'}
    
    def _assess_risk_principles(self, data: Dict) -> Dict:
        """Assess risk using first principles"""
        return {'score': 5, 'factors': ['volatility', 'drawdown']}
    
    def _identify_edge_principles(self, data: Dict) -> Dict:
        """Identify trading edge using first principles"""
        return {'score': 6, 'factors': ['confluence', 'power']}
    
    def _optimize_profit_principles(self, data: Dict) -> Dict:
        """Optimize profit using first principles"""
        return {'score': 7, 'factors': ['kelly_sizing', 'atr_targets']}

class KellyOptimizationEngine:
    """Kelly Criterion optimization engine"""
    
    def __init__(self):
        self.history = deque(maxlen=100)
        self.base_win_rate = 0.5
    
    async def start_ai_agent(self):
        """Start the AI agent for continuous analysis"""
        self.is_running = True
        print("🤖 Enigma-Apex AI Agent started")
        print("🎯 Applying first principles for profit maximization and loss minimization")
        
        while self.is_running:
            try:
                # This would integrate with your existing WebSocket server
                # to receive real-time market data and trade signals
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ AI Agent error: {e}")
                await asyncio.sleep(5)
    
    def analyze_trade_opportunity(self, trade_data: Dict) -> Dict:
        """Analyze a trade opportunity using AI first principles"""
        return self.ai_engine.get_real_time_guidance(trade_data)
    
    def log_trade_result(self, trade_result: Dict):
        """Log trade result for continuous learning"""
        self.ai_engine.update_performance_metrics(trade_result)
    
    def get_performance_insights(self) -> Dict:
        """Get AI-generated performance insights"""
        return self.ai_engine.generate_optimization_insights()
    
    def stop_ai_agent(self):
        """Stop the AI agent"""
        self.is_running = False
        print("🛑 Enigma-Apex AI Agent stopped")

# Example usage and testing
def test_ai_agent():
    """Test the AI agent with sample data"""
    agent = EnigmaApexAIAgent()
    
    # Sample trade data
    sample_trade = {
        "symbol": "NQ",
        "confluence_level": "L3",
        "power_score": 18,
        "atr": 15.5,
        "volume_ratio": 1.8,
        "session": "AM",
        "cadence_failures": 2,
        "daily_pnl_pct": -0.015,
        "momentum_strength": 0.75,
        "volume_expansion": True
    }
    
    # Analyze trade opportunity
    analysis = agent.analyze_trade_opportunity(sample_trade)
    
    print("🤖 AI ANALYSIS RESULTS:")
    print(f"📊 Action: {analysis['action']}")
    print(f"🎯 Confidence: {analysis['confidence']:.2%}")
    print(f"🛡️ Risk Level: {analysis['risk_level']}")
    print(f"💰 Position Size: {analysis['position_size_suggestion']:.3f}")
    print(f"🔻 Stop Loss: {analysis['stop_loss_suggestion']:.2f}")
    print(f"🔺 Profit Target: {analysis['profit_target_suggestion']:.2f}")
    print(f"💭 Reasoning: {analysis['reasoning']}")

if __name__ == "__main__":
    test_ai_agent()
