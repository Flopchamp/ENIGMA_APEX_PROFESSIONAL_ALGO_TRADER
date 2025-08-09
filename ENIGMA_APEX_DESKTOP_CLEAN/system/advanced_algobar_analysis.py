#!/usr/bin/env python3
"""
📊 ADVANCED ALGOBAR ANALYSIS SYSTEM
Comprehensive market structure analysis using AlgoBox AlgoBar technology
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

class MarketPhase(Enum):
    """Market phase classification"""
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"
    CONSOLIDATION = "consolidation"

class TrendStrength(Enum):
    """Trend strength classification"""
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NO_TREND = "no_trend"

@dataclass
class VolumeProfile:
    """Volume profile analysis"""
    volume_weighted_average_price: float = 0.0
    high_volume_nodes: List[float] = None
    low_volume_nodes: List[float] = None
    point_of_control: float = 0.0
    value_area_high: float = 0.0
    value_area_low: float = 0.0
    volume_distribution: Dict[str, float] = None

@dataclass
class OrderFlowAnalysis:
    """Order flow and delta analysis"""
    cumulative_delta: int = 0
    delta_divergence: bool = False
    absorption_levels: List[float] = None
    aggressive_buying: float = 0.0
    aggressive_selling: float = 0.0
    order_flow_imbalance: float = 0.0
    delta_momentum: str = "neutral"

@dataclass
class MarketStructureAnalysis:
    """Market structure analysis results"""
    higher_highs: List[float] = None
    higher_lows: List[float] = None
    lower_highs: List[float] = None
    lower_lows: List[float] = None
    support_levels: List[float] = None
    resistance_levels: List[float] = None
    market_phase: MarketPhase = MarketPhase.CONSOLIDATION
    trend_strength: TrendStrength = TrendStrength.NO_TREND
    
@dataclass
class AlgoBarMetrics:
    """Comprehensive AlgoBar metrics"""
    efficiency_ratio: float = 0.0
    volatility_index: float = 0.0
    momentum_score: float = 0.0
    market_participation: float = 0.0
    price_rejection: float = 0.0
    volume_spread_analysis: str = "neutral"
    bar_range_analysis: str = "normal"

class AdvancedAlgoBarAnalyzer:
    """Advanced AlgoBar analysis with comprehensive market structure"""
    
    def __init__(self):
        self.bars_history = []
        self.analysis_cache = {}
        self.support_resistance_levels = []
        self.market_profile_data = {}
        
        # Analysis parameters
        self.lookback_periods = {
            'short': 20,
            'medium': 50,
            'long': 100
        }
        
        # Volume profile parameters
        self.volume_profile_bins = 50
        self.value_area_percentage = 70  # 70% of volume
        
    def add_bars(self, bars: List[Dict]):
        """Add new bars to analysis"""
        self.bars_history.extend(bars)
        
        # Keep reasonable history size
        if len(self.bars_history) > 1000:
            self.bars_history = self.bars_history[-1000:]
        
        # Clear cache when new data is added
        self.analysis_cache.clear()
    
    def analyze_volume_profile(self, bars: List[Dict]) -> VolumeProfile:
        """Analyze volume profile from AlgoBar data"""
        
        if not bars:
            return VolumeProfile()
        
        try:
            # Extract price and volume data
            prices = []
            volumes = []
            
            for bar in bars:
                # Use high, low, and close for price distribution
                bar_prices = [bar['high'], bar['low'], bar['close']]
                bar_volume = bar['volume']
                
                for price in bar_prices:
                    prices.append(price)
                    volumes.append(bar_volume / 3)  # Distribute volume across price levels
            
            if not prices:
                return VolumeProfile()
            
            # Create price bins
            price_min, price_max = min(prices), max(prices)
            price_range = price_max - price_min
            
            if price_range == 0:
                return VolumeProfile()
            
            bin_size = price_range / self.volume_profile_bins
            
            # Calculate volume profile
            volume_by_price = {}
            
            for price, volume in zip(prices, volumes):
                bin_index = int((price - price_min) / bin_size)
                bin_price = price_min + (bin_index * bin_size)
                
                if bin_price not in volume_by_price:
                    volume_by_price[bin_price] = 0
                volume_by_price[bin_price] += volume
            
            # Calculate VWAP
            total_volume = sum(volumes)
            total_price_volume = sum(p * v for p, v in zip(prices, volumes))
            vwap = total_price_volume / total_volume if total_volume > 0 else 0
            
            # Find Point of Control (highest volume price)
            poc = max(volume_by_price.keys(), key=lambda x: volume_by_price[x]) if volume_by_price else 0
            
            # Calculate Value Area (70% of volume)
            sorted_levels = sorted(volume_by_price.items(), key=lambda x: x[1], reverse=True)
            
            value_area_volume = 0
            value_area_prices = []
            target_volume = total_volume * (self.value_area_percentage / 100)
            
            for price, volume in sorted_levels:
                value_area_volume += volume
                value_area_prices.append(price)
                if value_area_volume >= target_volume:
                    break
            
            va_high = max(value_area_prices) if value_area_prices else poc
            va_low = min(value_area_prices) if value_area_prices else poc
            
            # Identify high and low volume nodes
            avg_volume = sum(volume_by_price.values()) / len(volume_by_price) if volume_by_price else 0
            
            high_volume_nodes = [price for price, volume in volume_by_price.items() 
                               if volume > avg_volume * 1.5]
            low_volume_nodes = [price for price, volume in volume_by_price.items() 
                              if volume < avg_volume * 0.5]
            
            return VolumeProfile(
                volume_weighted_average_price=vwap,
                high_volume_nodes=high_volume_nodes,
                low_volume_nodes=low_volume_nodes,
                point_of_control=poc,
                value_area_high=va_high,
                value_area_low=va_low,
                volume_distribution=volume_by_price
            )
            
        except Exception as e:
            logging.error(f"Volume profile analysis failed: {e}")
            return VolumeProfile()
    
    def analyze_order_flow(self, bars: List[Dict]) -> OrderFlowAnalysis:
        """Analyze order flow and delta patterns"""
        
        if not bars:
            return OrderFlowAnalysis()
        
        try:
            # Calculate cumulative delta
            cumulative_delta = sum(bar.get('delta', 0) for bar in bars)
            
            # Analyze delta momentum
            recent_delta = sum(bar.get('delta', 0) for bar in bars[-10:]) if len(bars) >= 10 else 0
            older_delta = sum(bar.get('delta', 0) for bar in bars[-20:-10]) if len(bars) >= 20 else 0
            
            delta_momentum = "neutral"
            if recent_delta > older_delta * 1.2:
                delta_momentum = "bullish"
            elif recent_delta < older_delta * 0.8:
                delta_momentum = "bearish"
            
            # Calculate aggressive buying/selling
            aggressive_buying = sum(bar.get('delta', 0) for bar in bars if bar.get('delta', 0) > 0)
            aggressive_selling = abs(sum(bar.get('delta', 0) for bar in bars if bar.get('delta', 0) < 0))
            
            # Order flow imbalance
            total_volume = sum(bar.get('volume', 0) for bar in bars)
            imbalance = (aggressive_buying - aggressive_selling) / total_volume if total_volume > 0 else 0
            
            # Detect delta divergence (price up, delta down or vice versa)
            if len(bars) >= 2:
                price_change = bars[-1]['close'] - bars[0]['open']
                delta_change = recent_delta - older_delta if len(bars) >= 20 else recent_delta
                
                delta_divergence = (
                    (price_change > 0 and delta_change < 0) or 
                    (price_change < 0 and delta_change > 0)
                )
            else:
                delta_divergence = False
            
            # Identify absorption levels (high volume with small price movement)
            absorption_levels = []
            for i, bar in enumerate(bars[-20:]):  # Last 20 bars
                if i > 0:
                    price_range = bar['high'] - bar['low']
                    volume = bar.get('volume', 0)
                    
                    # High volume, small range indicates absorption
                    if volume > 0 and price_range > 0:
                        volume_per_tick = volume / price_range
                        if volume_per_tick > np.percentile([b.get('volume', 0) / max(0.01, b['high'] - b['low']) 
                                                           for b in bars[-20:]], 80):
                            absorption_levels.append(bar['close'])
            
            return OrderFlowAnalysis(
                cumulative_delta=cumulative_delta,
                delta_divergence=delta_divergence,
                absorption_levels=absorption_levels,
                aggressive_buying=aggressive_buying,
                aggressive_selling=aggressive_selling,
                order_flow_imbalance=imbalance,
                delta_momentum=delta_momentum
            )
            
        except Exception as e:
            logging.error(f"Order flow analysis failed: {e}")
            return OrderFlowAnalysis()
    
    def analyze_market_structure(self, bars: List[Dict]) -> MarketStructureAnalysis:
        """Analyze market structure patterns"""
        
        if len(bars) < 10:
            return MarketStructureAnalysis()
        
        try:
            # Extract swing highs and lows
            highs = [bar['high'] for bar in bars]
            lows = [bar['low'] for bar in bars]
            closes = [bar['close'] for bar in bars]
            
            # Find swing points using rolling window
            window = 5
            swing_highs = []
            swing_lows = []
            
            for i in range(window, len(bars) - window):
                # Check if current high is higher than surrounding bars
                if all(highs[i] >= highs[j] for j in range(i-window, i+window+1)):
                    swing_highs.append((i, highs[i]))
                
                # Check if current low is lower than surrounding bars
                if all(lows[i] <= lows[j] for j in range(i-window, i+window+1)):
                    swing_lows.append((i, lows[i]))
            
            # Analyze trend structure
            higher_highs = []
            higher_lows = []
            lower_highs = []
            lower_lows = []
            
            # Compare recent swing points
            if len(swing_highs) >= 2:
                for i in range(1, len(swing_highs)):
                    if swing_highs[i][1] > swing_highs[i-1][1]:
                        higher_highs.append(swing_highs[i][1])
                    else:
                        lower_highs.append(swing_highs[i][1])
            
            if len(swing_lows) >= 2:
                for i in range(1, len(swing_lows)):
                    if swing_lows[i][1] > swing_lows[i-1][1]:
                        higher_lows.append(swing_lows[i][1])
                    else:
                        lower_lows.append(swing_lows[i][1])
            
            # Determine market phase
            market_phase = MarketPhase.CONSOLIDATION
            
            if len(higher_highs) >= 2 and len(higher_lows) >= 2:
                market_phase = MarketPhase.MARKUP
            elif len(lower_highs) >= 2 and len(lower_lows) >= 2:
                market_phase = MarketPhase.MARKDOWN
            elif len(higher_highs) >= 1 and len(lower_lows) >= 1:
                market_phase = MarketPhase.DISTRIBUTION
            elif len(lower_highs) >= 1 and len(higher_lows) >= 1:
                market_phase = MarketPhase.ACCUMULATION
            
            # Calculate trend strength
            price_range = max(closes) - min(closes)
            trend_efficiency = abs(closes[-1] - closes[0]) / price_range if price_range > 0 else 0
            
            if trend_efficiency > 0.8:
                trend_strength = TrendStrength.VERY_STRONG
            elif trend_efficiency > 0.6:
                trend_strength = TrendStrength.STRONG
            elif trend_efficiency > 0.4:
                trend_strength = TrendStrength.MODERATE
            elif trend_efficiency > 0.2:
                trend_strength = TrendStrength.WEAK
            else:
                trend_strength = TrendStrength.NO_TREND
            
            # Identify support and resistance levels
            support_levels = [point[1] for point in swing_lows]
            resistance_levels = [point[1] for point in swing_highs]
            
            return MarketStructureAnalysis(
                higher_highs=higher_highs,
                higher_lows=higher_lows,
                lower_highs=lower_highs,
                lower_lows=lower_lows,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                market_phase=market_phase,
                trend_strength=trend_strength
            )
            
        except Exception as e:
            logging.error(f"Market structure analysis failed: {e}")
            return MarketStructureAnalysis()
    
    def calculate_algobar_metrics(self, bars: List[Dict]) -> AlgoBarMetrics:
        """Calculate advanced AlgoBar-specific metrics"""
        
        if not bars:
            return AlgoBarMetrics()
        
        try:
            # Efficiency Ratio (Kaufman's Adaptive Moving Average concept)
            if len(bars) >= 10:
                direction = abs(bars[-1]['close'] - bars[-10]['close'])
                volatility = sum(abs(bars[i]['close'] - bars[i-1]['close']) 
                               for i in range(-9, 0))
                efficiency_ratio = direction / volatility if volatility > 0 else 0
            else:
                efficiency_ratio = 0
            
            # Volatility Index (based on bar ranges)
            ranges = [bar['high'] - bar['low'] for bar in bars]
            avg_range = np.mean(ranges) if ranges else 0
            volatility_index = np.std(ranges) / avg_range if avg_range > 0 else 0
            
            # Momentum Score (price acceleration)
            if len(bars) >= 3:
                recent_change = bars[-1]['close'] - bars[-2]['close']
                previous_change = bars[-2]['close'] - bars[-3]['close']
                momentum_score = recent_change - previous_change
            else:
                momentum_score = 0
            
            # Market Participation (volume analysis)
            volumes = [bar.get('volume', 0) for bar in bars]
            avg_volume = np.mean(volumes) if volumes else 0
            recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else avg_volume
            market_participation = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Price Rejection (wick analysis)
            total_rejection = 0
            for bar in bars:
                body_size = abs(bar['close'] - bar['open'])
                total_range = bar['high'] - bar['low']
                
                if total_range > 0:
                    rejection = (total_range - body_size) / total_range
                    total_rejection += rejection
            
            price_rejection = total_rejection / len(bars) if bars else 0
            
            # Volume Spread Analysis
            if len(bars) >= 2:
                last_bar = bars[-1]
                body_size = abs(last_bar['close'] - last_bar['open'])
                range_size = last_bar['high'] - last_bar['low']
                volume = last_bar.get('volume', 0)
                
                if range_size > 0 and volume > 0:
                    volume_spread_ratio = volume / range_size
                    
                    if volume_spread_ratio > np.percentile([b.get('volume', 0) / max(0.01, b['high'] - b['low']) 
                                                           for b in bars[-10:]], 75):
                        volume_spread_analysis = "high_volume_narrow_spread"
                    elif volume_spread_ratio < np.percentile([b.get('volume', 0) / max(0.01, b['high'] - b['low']) 
                                                             for b in bars[-10:]], 25):
                        volume_spread_analysis = "low_volume_wide_spread"
                    else:
                        volume_spread_analysis = "normal"
                else:
                    volume_spread_analysis = "neutral"
            else:
                volume_spread_analysis = "neutral"
            
            # Bar Range Analysis
            if ranges:
                recent_range = np.mean(ranges[-5:]) if len(ranges) >= 5 else ranges[-1]
                historical_range = np.mean(ranges)
                
                if recent_range > historical_range * 1.5:
                    bar_range_analysis = "expanding"
                elif recent_range < historical_range * 0.5:
                    bar_range_analysis = "contracting"
                else:
                    bar_range_analysis = "normal"
            else:
                bar_range_analysis = "normal"
            
            return AlgoBarMetrics(
                efficiency_ratio=efficiency_ratio,
                volatility_index=volatility_index,
                momentum_score=momentum_score,
                market_participation=market_participation,
                price_rejection=price_rejection,
                volume_spread_analysis=volume_spread_analysis,
                bar_range_analysis=bar_range_analysis
            )
            
        except Exception as e:
            logging.error(f"AlgoBar metrics calculation failed: {e}")
            return AlgoBarMetrics()
    
    def generate_comprehensive_analysis(self, timeframe: str = "medium") -> Dict:
        """Generate comprehensive AlgoBar analysis report"""
        
        if not self.bars_history:
            return {"error": "No bar data available for analysis"}
        
        # Get bars for analysis based on timeframe
        lookback = self.lookback_periods.get(timeframe, 50)
        analysis_bars = self.bars_history[-lookback:] if len(self.bars_history) >= lookback else self.bars_history
        
        try:
            # Perform all analyses
            volume_profile = self.analyze_volume_profile(analysis_bars)
            order_flow = self.analyze_order_flow(analysis_bars)
            market_structure = self.analyze_market_structure(analysis_bars)
            algobar_metrics = self.calculate_algobar_metrics(analysis_bars)
            
            # Generate trading signals based on analysis
            signals = self.generate_trading_signals(volume_profile, order_flow, market_structure, algobar_metrics)
            
            # Create comprehensive report
            analysis_report = {
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "bars_analyzed": len(analysis_bars),
                "volume_profile": asdict(volume_profile),
                "order_flow": asdict(order_flow),
                "market_structure": asdict(market_structure),
                "algobar_metrics": asdict(algobar_metrics),
                "trading_signals": signals,
                "market_summary": self.generate_market_summary(volume_profile, order_flow, market_structure, algobar_metrics)
            }
            
            return analysis_report
            
        except Exception as e:
            logging.error(f"Comprehensive analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_trading_signals(self, volume_profile: VolumeProfile, order_flow: OrderFlowAnalysis, 
                               market_structure: MarketStructureAnalysis, metrics: AlgoBarMetrics) -> Dict:
        """Generate trading signals based on comprehensive analysis"""
        
        signals = {
            "bias": "neutral",
            "strength": 0,  # -5 to +5 scale
            "key_levels": [],
            "entry_signals": [],
            "risk_assessment": "medium"
        }
        
        try:
            strength_score = 0
            
            # Market structure signals
            if market_structure.market_phase == MarketPhase.MARKUP:
                strength_score += 2
                signals["entry_signals"].append("Bullish market structure - higher highs and lows")
            elif market_structure.market_phase == MarketPhase.MARKDOWN:
                strength_score -= 2
                signals["entry_signals"].append("Bearish market structure - lower highs and lows")
            
            # Order flow signals
            if order_flow.delta_momentum == "bullish":
                strength_score += 1
                signals["entry_signals"].append("Positive delta momentum")
            elif order_flow.delta_momentum == "bearish":
                strength_score -= 1
                signals["entry_signals"].append("Negative delta momentum")
            
            if order_flow.order_flow_imbalance > 0.1:
                strength_score += 1
            elif order_flow.order_flow_imbalance < -0.1:
                strength_score -= 1
            
            # Volume profile signals
            if volume_profile.point_of_control:
                signals["key_levels"].append(f"POC: {volume_profile.point_of_control:.2f}")
            if volume_profile.value_area_high and volume_profile.value_area_low:
                signals["key_levels"].extend([
                    f"VA High: {volume_profile.value_area_high:.2f}",
                    f"VA Low: {volume_profile.value_area_low:.2f}"
                ])
            
            # AlgoBar metrics signals
            if metrics.efficiency_ratio > 0.7:
                strength_score += 1
                signals["entry_signals"].append("High trend efficiency")
            
            if metrics.market_participation > 1.2:
                signals["entry_signals"].append("Increased market participation")
            
            # Determine overall bias
            if strength_score >= 2:
                signals["bias"] = "bullish"
            elif strength_score <= -2:
                signals["bias"] = "bearish"
            else:
                signals["bias"] = "neutral"
            
            signals["strength"] = max(-5, min(5, strength_score))
            
            # Risk assessment
            if metrics.volatility_index > 2:
                signals["risk_assessment"] = "high"
            elif metrics.volatility_index < 0.5:
                signals["risk_assessment"] = "low"
            else:
                signals["risk_assessment"] = "medium"
            
            return signals
            
        except Exception as e:
            logging.error(f"Signal generation failed: {e}")
            return signals
    
    def generate_market_summary(self, volume_profile: VolumeProfile, order_flow: OrderFlowAnalysis,
                              market_structure: MarketStructureAnalysis, metrics: AlgoBarMetrics) -> str:
        """Generate human-readable market summary"""
        
        summary_parts = []
        
        try:
            # Market phase summary
            phase_description = {
                MarketPhase.MARKUP: "Market is in an uptrend with higher highs and lows",
                MarketPhase.MARKDOWN: "Market is in a downtrend with lower highs and lows",
                MarketPhase.ACCUMULATION: "Market showing accumulation characteristics",
                MarketPhase.DISTRIBUTION: "Market showing distribution characteristics",
                MarketPhase.CONSOLIDATION: "Market is consolidating in a range"
            }
            
            summary_parts.append(phase_description.get(market_structure.market_phase, "Market phase unclear"))
            
            # Trend strength
            strength_description = {
                TrendStrength.VERY_STRONG: "with very strong momentum",
                TrendStrength.STRONG: "with strong momentum",
                TrendStrength.MODERATE: "with moderate momentum",
                TrendStrength.WEAK: "with weak momentum",
                TrendStrength.NO_TREND: "with no clear trend"
            }
            
            summary_parts.append(strength_description.get(market_structure.trend_strength, ""))
            
            # Order flow summary
            if order_flow.cumulative_delta > 1000:
                summary_parts.append("Strong buying pressure evident in order flow")
            elif order_flow.cumulative_delta < -1000:
                summary_parts.append("Strong selling pressure evident in order flow")
            
            # Volume analysis
            if metrics.market_participation > 1.5:
                summary_parts.append("Above-average market participation")
            elif metrics.market_participation < 0.5:
                summary_parts.append("Below-average market participation")
            
            # Volatility assessment
            if metrics.volatility_index > 2:
                summary_parts.append("High volatility environment - use appropriate position sizing")
            elif metrics.volatility_index < 0.5:
                summary_parts.append("Low volatility environment - potential for expansion")
            
            return ". ".join(summary_parts) + "."
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

def main():
    """Test the advanced AlgoBar analyzer"""
    
    print("🚀 Testing Advanced AlgoBar Analysis System")
    
    # Create analyzer
    analyzer = AdvancedAlgoBarAnalyzer()
    
    # Generate sample AlgoBar data for testing
    sample_bars = []
    base_price = 4580.0
    
    for i in range(100):
        # Simulate price movement
        price_change = np.random.normal(0, 2)  # Random walk
        new_price = base_price + price_change
        
        # Create bar with realistic OHLC
        high = new_price + abs(np.random.normal(0, 1))
        low = new_price - abs(np.random.normal(0, 1))
        
        bar = {
            'open': base_price,
            'high': high,
            'low': low,
            'close': new_price,
            'volume': np.random.randint(100, 1000),
            'delta': np.random.randint(-500, 500),
            'timestamp': datetime.now() - timedelta(minutes=100-i),
            'is_bullish': new_price > base_price
        }
        
        sample_bars.append(bar)
        base_price = new_price
    
    # Add bars to analyzer
    analyzer.add_bars(sample_bars)
    
    # Generate comprehensive analysis
    analysis = analyzer.generate_comprehensive_analysis("medium")
    
    if "error" not in analysis:
        print("✅ Analysis completed successfully!")
        print(f"\n📊 Market Summary: {analysis['market_summary']}")
        print(f"\n🎯 Trading Bias: {analysis['trading_signals']['bias'].upper()}")
        print(f"💪 Signal Strength: {analysis['trading_signals']['strength']}/5")
        print(f"⚠️ Risk Assessment: {analysis['trading_signals']['risk_assessment'].upper()}")
        
        if analysis['trading_signals']['entry_signals']:
            print(f"\n📈 Entry Signals:")
            for signal in analysis['trading_signals']['entry_signals']:
                print(f"  • {signal}")
        
        if analysis['trading_signals']['key_levels']:
            print(f"\n🎯 Key Levels:")
            for level in analysis['trading_signals']['key_levels']:
                print(f"  • {level}")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")

if __name__ == "__main__":
    main()
