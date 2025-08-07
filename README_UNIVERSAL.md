# 🎯 UNIVERSAL APEX TRADING DASHBOARD

**Professional Streamlit-based trading dashboard for Apex Trader Funding compliance**
**Configurable for ANY trader, ANY setup, ANY number of charts**

## 🌟 KEY FEATURES

### ✅ **Universal Configuration**
- **Any Trader**: Fully configurable user profiles
- **Any Account Size**: $5K to $100K+ accounts supported
- **Any Number of Charts**: 1 to 12 charts (not hardcoded to 6)
- **Any Broker**: NinjaTrader, Tradovate, ThinkOrSwim, etc.
- **Any Strategy**: Customizable signal types and indicators

### 📊 **Visual Dashboard**
- **Red/Yellow/Green Status Boxes** for each chart
- **Customizable Priority Indicator** (margin, P&L, risk, drawdown)
- **Real-time Chart Grid** with individual controls
- **Professional Streamlit Interface** (web-based)
- **Responsive Design** works on any screen size

### 👁️ **Optional OCR Integration**
- **Screen Reading** from any trading platform
- **Configurable Regions** for each chart
- **Real-time Signal Detection** 
- **Multiple Data Types** (numbers, text, colors)
- **Easy Calibration** with visual tools

### ⚖️ **Apex Compliance**
- **Trailing Drawdown** monitoring
- **30% Consistency Rule** enforcement
- **Daily Loss Limits** protection
- **Risk Management** with Kelly Criterion
- **Emergency Stop** functionality

## 🚀 QUICK START

### 1. **Installation**
```bash
# Clone or download the system
cd ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER

# Launch with automatic dependency installation
python launch_streamlit_dashboard.py
```

### 2. **First Launch**
The launcher will:
- ✅ Check and install required dependencies
- 🌐 Open dashboard in your web browser
- ⚙️ Guide you through initial configuration
- 📊 Start with default 6-chart setup

### 3. **Basic Configuration**
1. **Open the sidebar** (⚙️ Configuration)
2. **Set your trader name** and account size
3. **Configure number of charts** (1-12)
4. **Name your charts** (ES-Primary, NQ-Scalp, etc.)
5. **Set your priority indicator** (Margin, P&L, Risk)
6. **Choose your broker platform**

## 📊 DASHBOARD OVERVIEW

### **Main Interface**
```
🎯 Priority Monitor: MARGIN REMAINING    [Most Important - Configurable]
💰 $18,450 Remaining | 📊 $6,550 Used | 📈 73.8% Available

📊 Chart Status Grid
┌─────────────┬─────────────┬─────────────┐
│ 🟢 ES-Primary │ 🟡 ES-Scalp  │ 🔴 NQ-Swing  │
│ Power: 85%   │ Power: 45%   │ Power: 15%   │
│ Pos: 2.5     │ Pos: 1.0     │ Pos: 0.0     │
│ P&L: +$340   │ P&L: -$120   │ P&L: $0      │
└─────────────┴─────────────┴─────────────┘

🎛️ System Controls
[🚀 Start] [⏸️ Pause] [🚨 EMERGENCY STOP] [🔄 Reset]
```

### **Configuration Sidebar**
- 👤 **User Settings**: Name, account size
- 📊 **Chart Settings**: Number, names, positions
- ⚖️ **Risk Management**: Safety ratios, limits
- 🎯 **Priority**: Most important indicator
- 💼 **Broker**: Platform selection

### **Advanced Tabs**
- 📈 **Performance**: Equity curves, metrics
- 👁️ **OCR Setup**: Screen reading configuration
- ⚙️ **Settings**: Advanced options, import/export
- 📋 **Logs**: System activity, alerts

## 👁️ OCR CONFIGURATION

### **Enable OCR** (Optional)
```bash
# Install OCR dependencies
pip install pytesseract opencv-python

# Download Tesseract OCR
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

### **Setup Process**
1. **Arrange your trading charts** on screen
2. **Go to OCR Setup tab** in dashboard
3. **Capture full screen** to see coordinates
4. **Configure regions** for each chart:
   - Power Score area
   - Signal Color area
   - Confluence Levels
5. **Test each region** with live capture
6. **Enable monitoring** when ready

### **OCR Region Types**
- 🔢 **Power Score**: Numbers (0-100%)
- 🎨 **Signal Color**: Color detection (Red/Green/Blue)
- 📊 **Confluence**: Multiple level regions
- 📈 **Custom**: Any text or numeric data

## ⚙️ CONFIGURATION OPTIONS

### **User Profiles**
```json
{
  "trader_name": "YourName",
  "account_size": 25000.0,
  "max_charts": 8,
  "chart_names": [
    "ES-Scalp", "ES-Swing", "NQ-Day", "NQ-Scalp",
    "YM-Primary", "RTY-Backup", "Custom-1", "Custom-2"
  ],
  "safety_ratio": 25.0,
  "daily_loss_limit": 2000.0,
  "priority_indicator": "margin",
  "broker": "ninjatrader"
}
```

### **Chart Configurations**
- **1-3 Charts**: Day trading focus
- **4-6 Charts**: Multi-timeframe approach  
- **7-12 Charts**: Professional setup
- **Custom Names**: Match your strategy

### **Priority Indicators**
- 💰 **Margin**: Shows remaining buying power
- 📈 **P&L**: Current profit/loss focus
- ⚖️ **Risk**: Risk exposure monitoring
- 📉 **Drawdown**: Maximum loss tracking

### **Broker Integration**
- **NinjaTrader**: Full automation support
- **Tradovate**: Web-based integration
- **ThinkOrSwim**: TOS compatibility
- **Other**: Generic setup for any platform

## 🛡️ SAFETY FEATURES

### **Emergency Stop System**
- 🚨 **Instant Stop**: Halts all trading immediately
- 🔴 **All Charts Red**: Visual confirmation
- 🚫 **Disable All**: Prevents new positions
- 🔄 **Manual Reset**: Requires deliberate action

### **Apex Compliance**
- **Trailing Drawdown**: Real-time monitoring
- **Daily Loss Limits**: Automatic enforcement
- **Consistency Rules**: 30% rule tracking
- **Position Limits**: Per-chart maximum sizes

### **Risk Management**
- **Kelly Criterion**: Mathematical position sizing
- **Safety Ratios**: Conservative 5-90% range
- **Account Protection**: Multiple safety layers
- **Violation Alerts**: Early warning system

## 📈 PERFORMANCE ANALYTICS

### **Real-time Metrics**
- 📊 **Equity Curve**: 30-day performance
- 💰 **P&L Tracking**: Daily/weekly/monthly
- 📈 **Win Rate**: Success percentage
- 🎯 **Profit Factor**: Risk-reward analysis
- 📉 **Drawdown**: Maximum loss periods

### **Chart-Level Analytics**
- **Individual P&L** per chart
- **Signal Strength** history
- **Position Sizing** effectiveness
- **Risk Contribution** analysis

## 🔧 CUSTOMIZATION

### **For Day Traders**
```python
# Quick setup for day trading
charts = ["ES-1min", "ES-5min", "NQ-1min"]
priority = "pnl"  # Focus on profit/loss
safety_ratio = 15.0  # Aggressive
```

### **For Swing Traders**
```python
# Setup for swing trading
charts = ["ES-Daily", "NQ-4hr", "YM-Daily", "RTY-Weekly"]
priority = "risk"  # Focus on risk management
safety_ratio = 35.0  # Conservative
```

### **For Scalpers**
```python
# High-frequency setup
charts = ["ES-15sec", "ES-30sec", "ES-1min", "ES-Tick"]
priority = "margin"  # Watch buying power
safety_ratio = 10.0  # Very aggressive
```

## 📁 FILE STRUCTURE

```
ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER/
├── 🚀 launch_streamlit_dashboard.py     # Main launcher
├── 📊 streamlit_trading_dashboard.py    # Core dashboard
├── 👁️ streamlit_ocr_module.py          # OCR integration
├── 📝 README_UNIVERSAL.md              # This file
├── config/
│   ├── user_config.json               # User settings
│   └── ocr_config.json                # OCR regions
└── logs/
    └── trading_YYYYMMDD.log           # System logs
```

## 🆘 TROUBLESHOOTING

### **Dashboard Won't Start**
```bash
# Check Python version
python --version  # Need 3.7+

# Install dependencies manually
pip install streamlit plotly pandas numpy

# Run directly
streamlit run streamlit_trading_dashboard.py
```

### **OCR Not Working**
```bash
# Install OCR dependencies
pip install pytesseract opencv-python pillow

# Check Tesseract installation
tesseract --version

# Windows: Add to PATH
# C:\Program Files\Tesseract-OCR\tesseract.exe
```

### **Browser Issues**
- Dashboard opens at: `http://localhost:8501`
- Try different browser (Chrome, Firefox, Edge)
- Disable ad blockers
- Check firewall settings

### **Performance Issues**
- Reduce number of charts
- Increase update intervals
- Disable OCR monitoring if not needed
- Close other browser tabs

## 🚀 GETTING STARTED CHECKLIST

### **Initial Setup** (5 minutes)
- [ ] Download/clone the system
- [ ] Run `python launch_streamlit_dashboard.py`
- [ ] Open dashboard in browser
- [ ] Configure your trader name
- [ ] Set your account size

### **Basic Configuration** (10 minutes)
- [ ] Set number of charts you want
- [ ] Name your charts meaningfully
- [ ] Choose your priority indicator
- [ ] Set safety ratios
- [ ] Select your broker

### **OCR Setup** (20 minutes - Optional)
- [ ] Install OCR dependencies
- [ ] Arrange trading charts on screen
- [ ] Capture full screen in dashboard
- [ ] Configure regions for each chart
- [ ] Test region capture
- [ ] Enable monitoring

### **Go Live** (After testing)
- [ ] Test with demo account first
- [ ] Verify emergency stop works
- [ ] Test all chart controls
- [ ] Monitor for 1 hour minimum
- [ ] Start with small positions

## 💡 TIPS FOR SUCCESS

### **Best Practices**
1. 🧪 **Test Everything**: Use demo accounts first
2. 🔄 **Start Small**: Begin with 1-2 charts
3. 📊 **Monitor Closely**: Watch for first few hours
4. 🚨 **Trust Safety**: Don't disable emergency stops
5. 📈 **Review Daily**: Check performance analytics

### **Common Mistakes**
- ❌ Disabling safety features
- ❌ Using too many charts initially  
- ❌ Not testing OCR regions properly
- ❌ Ignoring compliance alerts
- ❌ Starting with live account

### **Optimization**
- ⚡ Use fewer charts for better performance
- 🎯 Focus on your priority indicator
- 🔧 Customize for your trading style
- 📊 Regular review and adjustment

---

## 🎉 CONGRATULATIONS!

You now have a **professional, universal trading dashboard** that can be configured for:
- ✅ **Any trader** (not just "Michael")
- ✅ **Any number of charts** (not hardcoded to 6)
- ✅ **Any account size** (flexible configuration)
- ✅ **Any trading style** (day/swing/scalp)
- ✅ **Any priority** (margin/P&L/risk focus)

**Happy Trading with Confidence!** 🚀📈💰
