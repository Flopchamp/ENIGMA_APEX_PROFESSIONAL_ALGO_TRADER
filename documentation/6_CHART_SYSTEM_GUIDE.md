# 🎯 ENIGMA APEX - 6-CHART PROFESSIONAL SYSTEM GUIDE

## 🚀 Overview
This system is configured to run **6 simultaneous trading charts** with **predefined account management** for professional trading operations.

## 📊 6-Chart Configuration

### Chart Layout (3x2 Grid)
```
┌─────────────┬─────────────┬─────────────┐
│     ES      │     NQ      │     YM      │
│  S&P 500    │   Nasdaq    │  Dow Jones  │
│   5-min     │    5-min    │    5-min    │
│ ES_SCALPING │NQ_MOMENTUM  │  YM_SWING   │
└─────────────┼─────────────┼─────────────┤
│     RTY     │     GC      │     CL      │
│ Russell 2K  │    Gold     │ Crude Oil   │
│   5-min     │   15-min    │   15-min    │
│RTY_BREAKOUT │  GC_TREND   │ CL_INTRADAY │
└─────────────┴─────────────┴─────────────┘
```

## 💼 Predefined Account Settings

### Account 1: ES_SCALPING
- **Symbol:** ES (S&P 500 E-mini)
- **Account Size:** $15,000
- **Risk Level:** 2%
- **Max Contracts:** 2
- **Strategy:** Scalping
- **Stop Loss:** 8 points
- **Take Profit:** 12 points
- **Risk/Reward:** 1.5:1

### Account 2: NQ_MOMENTUM
- **Symbol:** NQ (Nasdaq E-mini)
- **Account Size:** $12,000
- **Risk Level:** 2.5%
- **Max Contracts:** 1
- **Strategy:** Momentum Trading
- **Stop Loss:** 25 points
- **Take Profit:** 50 points
- **Risk/Reward:** 2:1

### Account 3: YM_SWING
- **Symbol:** YM (Dow Jones E-mini)
- **Account Size:** $10,000
- **Risk Level:** 3%
- **Max Contracts:** 1
- **Strategy:** Swing Trading
- **Stop Loss:** 150 points
- **Take Profit:** 300 points
- **Risk/Reward:** 2:1

### Account 4: RTY_BREAKOUT
- **Symbol:** RTY (Russell 2000 E-mini)
- **Account Size:** $8,000
- **Risk Level:** 2.5%
- **Max Contracts:** 2
- **Strategy:** Breakout Trading
- **Stop Loss:** 15 points
- **Take Profit:** 30 points
- **Risk/Reward:** 2:1

### Account 5: GC_TREND
- **Symbol:** GC (Gold Futures)
- **Account Size:** $7,000
- **Risk Level:** 2%
- **Max Contracts:** 1
- **Strategy:** Trend Following
- **Stop Loss:** 8 points ($800)
- **Take Profit:** 16 points ($1,600)
- **Risk/Reward:** 2:1

### Account 6: CL_INTRADAY
- **Symbol:** CL (Crude Oil Futures)
- **Account Size:** $8,000
- **Risk Level:** 2.5%
- **Max Contracts:** 1
- **Strategy:** Intraday Trading
- **Stop Loss:** 0.5 points ($500)
- **Take Profit:** 1.0 points ($1,000)
- **Risk/Reward:** 2:1

## 🎯 System Features

### Multi-Chart Management
- **Synchronized Charts:** All charts update simultaneously
- **Layout Options:** 3x2, 2x3, 6x1, 1x6 arrangements
- **Real-time Updates:** Live data feeds for all symbols
- **Auto-arrangement:** Charts automatically position themselves

### Account Management
- **Individual Risk Settings:** Each account has its own risk parameters
- **Position Sizing:** Automatic calculation based on account size and risk
- **Strategy-specific Settings:** Customized parameters for each trading style
- **Multi-account P&L:** Consolidated profit/loss tracking

### Professional Interface
- **Dashboard:** Overview of all 6 charts and accounts
- **6-Chart Manager:** Dedicated chart configuration interface
- **Multi-Account Trades:** Bulk trading operations across accounts
- **Real-time Monitoring:** Live status updates for all positions

## 🚀 Quick Start Guide

### 1. Access the System
Navigate to: `https://enigma-apex-professional.streamlit.app/`

### 2. Dashboard Overview
The main dashboard shows:
- 6-chart visual layout
- Individual account performance
- Real-time P&L for each account
- System status indicators

### 3. Chart Management
Use the **"📊 6-Chart Manager"** section to:
- Configure chart layouts
- Synchronize timeframes
- Adjust individual chart settings
- Export/import configurations

### 4. Multi-Account Trading
Use the **"💼 Multi-Account Trades"** section to:
- Execute trades across multiple accounts
- Monitor all positions simultaneously
- Perform bulk operations
- View consolidated performance

### 5. Settings Configuration
In the **"⚙️ Settings"** section:
- Modify account parameters
- Adjust chart configurations
- Configure server connections
- Save/load system settings

## 📈 Trading Operations

### Signal Generation
Each chart generates signals based on:
- **Power Score Algorithm:** Proprietary scoring system
- **Risk Management:** Built-in position sizing
- **Strategy-specific Logic:** Customized for each trading style

### Position Management
- **Auto-sizing:** Positions calculated based on account risk
- **Stop Loss/Take Profit:** Automatic order placement
- **Risk Monitoring:** Continuous risk assessment
- **Multi-account Coordination:** Synchronized across all accounts

### Performance Tracking
- **Individual Account P&L:** Real-time profit/loss tracking
- **Consolidated Performance:** Total system performance
- **Risk Metrics:** Account-specific risk monitoring
- **Trade History:** Complete transaction records

## 🛡️ Risk Management

### Account-Level Risk
- **Maximum Risk per Trade:** Set percentage of account size
- **Position Limits:** Maximum number of contracts per account
- **Daily Loss Limits:** Built-in daily stop-loss protection
- **Account Isolation:** Each account operates independently

### System-Level Risk
- **Total Capital at Risk:** $60,000 across all accounts
- **Diversification:** Multiple symbols and strategies
- **Risk Correlation:** Monitoring cross-account exposure
- **Emergency Controls:** System-wide position closure

## 🔧 Configuration Files

### Environment Settings (.env)
```bash
CHART_COUNT=6
CHART_SYMBOLS=ES,NQ,YM,RTY,GC,CL
CHART_TIMEFRAMES=5min,5min,5min,5min,15min,15min
CHART_LAYOUT=3x2
```

### Account Configurations
Each account has predefined settings for:
- Account size and risk level
- Maximum position size
- Stop loss and take profit levels
- Trading hours and strategy type

## 🎛️ Advanced Features

### Chart Synchronization
- **Timeframe Sync:** All charts use same timeframe when enabled
- **Cross-symbol Analysis:** Compare performance across instruments
- **Layout Flexibility:** Switch between different arrangements
- **Custom Indicators:** Strategy-specific technical indicators

### Automated Trading
- **Signal-based Execution:** Automatic trade execution on signals
- **Risk-adjusted Sizing:** Position sizes calculated automatically
- **Multi-account Coordination:** Trades executed across relevant accounts
- **Performance Optimization:** Continuous strategy refinement

### Professional Interface
- **Real-time Updates:** Live data and position updates
- **Professional Styling:** Clean, trader-focused design
- **Mobile Responsive:** Access from any device
- **Export Capabilities:** Data export for analysis

## 🔗 NinjaTrader Integration

### Connection Setup
The system connects to NinjaTrader for:
- **Live Data Feeds:** Real-time market data
- **Order Execution:** Professional order routing
- **Account Management:** Direct broker integration
- **Risk Controls:** Built-in safety mechanisms

### Strategy Deployment
Automated strategies include:
- **EnigmaApexAutoTrader:** Main trading algorithm
- **EnigmaApexRiskManager:** Risk monitoring system
- **EnigmaApexPowerScore:** Signal generation engine

## 📞 Support & Documentation

### Available Resources
- **User Manual:** Complete system documentation
- **Visual Setup Guide:** Step-by-step configuration
- **FAQ:** Common questions and solutions
- **Quick Reference:** Key commands and features

### System Requirements
- **NinjaTrader 8:** Professional trading platform
- **Stable Internet:** Reliable connection for live data
- **Browser:** Modern web browser for interface
- **Windows OS:** Recommended for full functionality

## 🚨 Important Notes

### Live Trading Mode
- **Real Money:** System configured for live trading
- **Risk Warning:** Trading involves substantial risk
- **Capital Protection:** Use appropriate position sizes
- **Continuous Monitoring:** Watch positions actively

### Server Connection
- **IP Address:** 155.138.229.220
- **Port:** 8080
- **Connection Status:** Monitor connection health
- **Backup Plans:** Have contingency procedures

## 🎯 Success Tips

### Best Practices
1. **Start Small:** Begin with minimum position sizes
2. **Monitor Performance:** Track individual account metrics
3. **Risk Management:** Never exceed predefined risk limits
4. **Strategy Consistency:** Stick to account-specific strategies
5. **Continuous Learning:** Review and optimize regularly

### Performance Optimization
- **Regular Reviews:** Analyze account performance weekly
- **Strategy Adjustments:** Modify parameters based on results
- **Risk Reassessment:** Update risk levels as needed
- **Technology Updates:** Keep system updated

---

**🎯 ENIGMA APEX PROFESSIONAL - 6-CHART MULTI-ACCOUNT TRADING SYSTEM**  
*Advanced Trading Technology for Professional Traders*

For technical support or questions, refer to the documentation section in the application interface.
