# 🎯 MICHAEL'S 6-CHART ALGORITHMIC TRADING SYSTEM

**The Complete "Training Wheels" Solution for Apex Trader Funding**

## 📋 QUICK START GUIDE

### What You Get:
- ✅ **6-Chart Visual Control Panel** with Red/Green/Yellow status boxes
- ✅ **Overall Margin Indicator** (Most Important Feature - #3)
- ✅ **Individual Chart On/Off Switches** 
- ✅ **AlgoBox OCR Signal Reading** for all 6 charts
- ✅ **Apex Trader Funding 3.0 Compliance** protection
- ✅ **Kelly Criterion Position Sizing** with safety controls
- ✅ **Emergency Stop Button** for instant protection
- ✅ **NinjaTrader Integration** (Port 36973)

## 🚀 INSTALLATION & SETUP

### 1. **System Requirements**
```
✅ Windows 10/11
✅ Python 3.7+ 
✅ AlgoBox Enigma (6 charts visible)
✅ NinjaTrader 8 (optional but recommended)
✅ Tesseract OCR (for screen reading)
```

### 2. **Launch the System**
```bash
# Simple double-click launch:
python launch_michael_system.py

# Or from command line:
cd "C:\Users\Julimore\Desktop\confused\ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER"
python launch_michael_system.py
```

### 3. **First Time Setup**
1. **Position your 6 AlgoBox charts** in a 2x3 grid on your screen
2. **Calibrate OCR regions** - the system will prompt you
3. **Test each chart** using the individual on/off switches
4. **Verify NinjaTrader connection** on port 36973
5. **Test emergency stop** before live trading

## 📊 HOW TO USE THE VISUAL CONTROL PANEL

### **Chart Status Colors:**
- 🟢 **GREEN** = Strong signal, ready to trade (Power Score 70%+)
- 🟡 **YELLOW** = Weak signal or disabled (Power Score 40-69%)
- 🔴 **RED** = No signal, violation, or locked out (Power Score <40%)

### **Individual Chart Controls:**
- **ON/OFF Switch** for each chart
- **Chart Name** (ES-Account-1, NQ-Account-2, etc.)
- **Power Score** percentage from AlgoBox
- **Signal Strength** indicator
- **Position Size** calculated by Kelly Criterion

### **Overall System Status:**
- 💰 **Margin Remaining** (MOST IMPORTANT - #3)
- 📈 **Total Equity** in your account
- ⚖️ **Safety Ratio** (5-90% adjustable)
- 🚨 **Emergency Stop** button
- 📊 **Active Charts** count

### **Apex Compliance Protection:**
- ✅ **Trailing Drawdown** monitoring
- ✅ **30% Consistency Rule** enforcement  
- ✅ **Daily Loss Limits** protection
- ✅ **5:1 Risk-Reward** ratio compliance
- ✅ **Automatic lockout** on violations

## ⚙️ CONFIGURATION

### **Safety Settings:**
```python
# Adjust these in the GUI:
Safety Ratio: 25%        # Conservative (5-90% range)
Max Position: 5 contracts # Per chart maximum
Daily Loss Limit: $2000  # Emergency stop trigger
Account Size: $25,000    # Your Apex account
```

### **OCR Screen Regions** (Auto-configured):
```
Chart 1 (Top-Left):     Power Score, Confluence, Signal Color
Chart 2 (Top-Center):   Power Score, Confluence, Signal Color  
Chart 3 (Top-Right):    Power Score, Confluence, Signal Color
Chart 4 (Bottom-Left):  Power Score, Confluence, Signal Color
Chart 5 (Bottom-Center): Power Score, Confluence, Signal Color
Chart 6 (Bottom-Right): Power Score, Confluence, Signal Color
```

## 🔧 TROUBLESHOOTING

### **OCR Not Reading Charts:**
1. Check if AlgoBox charts are visible and not overlapped
2. Recalibrate screen regions in `config/multi_chart_ocr_config.json`
3. Ensure good contrast on your AlgoBox theme
4. Verify Tesseract OCR is installed correctly

### **NinjaTrader Connection Issues:**
1. Check port 36973 is open in NinjaTrader
2. Ensure ATI (Automated Trading Interface) is enabled
3. Verify account permissions for automated trading
4. Test connection with simple manual order

### **Apex Compliance Violations:**
1. Check the violation alerts in the system status
2. Review your trading consistency (30% rule)
3. Monitor trailing drawdown limits
4. Ensure 5:1 risk-reward ratios are maintained

### **Emergency Stop Activated:**
1. **DO NOT PANIC** - this is protecting your account
2. Check what triggered the stop in the alerts
3. Review your positions in NinjaTrader
4. Only reset after fixing the underlying issue

## 📁 FILE STRUCTURE

```
ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER/
├── launch_michael_system.py          # Main launcher (START HERE)
├── README_MICHAEL.md                 # This file
├── system/
│   ├── michael_6_chart_control_panel.py      # Visual GUI
│   ├── multi_chart_ocr_coordinator.py        # OCR for 6 charts
│   ├── system_integration_bridge.py          # Connects everything
│   ├── apex_compliance_guardian.py           # Apex rules (Harrison's)
│   ├── advanced_risk_manager.py              # Risk management
│   └── kelly_criterion_engine.py             # Position sizing
├── config/
│   ├── multi_chart_ocr_config.json          # OCR screen regions
│   └── apex_trading_rules.json              # Compliance settings
└── logs/
    └── michael_system_YYYYMMDD_HHMMSS.log   # System logs
```

## 💡 TRADING WORKFLOW

### **Daily Startup:**
1. ✅ Launch AlgoBox with 6 charts in 2x3 grid
2. ✅ Start NinjaTrader with your Apex account
3. ✅ Run `python launch_michael_system.py`
4. ✅ Verify all 6 charts show GREEN or YELLOW status
5. ✅ Check overall margin remaining is adequate
6. ✅ Test emergency stop once

### **During Trading:**
1. 👀 **Watch the overall margin indicator** (MOST IMPORTANT)
2. 🔍 Monitor individual chart colors for signals
3. ⚖️ Let Kelly Criterion calculate position sizes
4. 🚨 Trust the emergency stop if triggered
5. 📊 Review violation alerts regularly

### **End of Day:**
1. 🛑 Use emergency stop to halt all trading
2. 📈 Review performance in the logs
3. 💾 Save any configuration changes
4. 📊 Check Apex compliance metrics

## ⚠️ IMPORTANT SAFETY NOTES

1. **NEVER** disable the emergency stop
2. **ALWAYS** start with small position sizes
3. **TEST** extensively on demo accounts first
4. **MONITOR** the overall margin indicator constantly
5. **RESPECT** all Apex Trader Funding rules
6. **BACKUP** your configuration files regularly

## 🆘 SUPPORT & HELP

### **Log Files:**
All system activity is logged in `logs/` directory. Check the latest log file for errors or issues.

### **Configuration:**
- OCR regions: `config/multi_chart_ocr_config.json`
- Apex rules: `config/apex_trading_rules.json`
- System settings: Saved automatically

### **Harrison's Original System:**
This builds on Harrison's excellent foundation. His single-chart system (85% complete) has been adapted for your 6-chart visual needs.

---

## 🎉 CONGRATULATIONS!

You now have the complete "training wheels" system you requested:
- ✅ Red/Green/Yellow visual boxes for 6 charts
- ✅ Overall margin remaining indicator (#3 most important)
- ✅ Individual on/off switches
- ✅ Automatic Apex compliance protection
- ✅ Emergency stop safety

**Happy Trading with Confidence!** 🚀📈
