# 🚀 QUICK SETUP GUIDE - NinjaTrader + Tradovate Dashboard

## How to Test and Use the System

### 🎮 **DEMO MODE (Start Here)**
Perfect for testing without any real connections:

1. **Launch the Dashboard:**
   ```bash
   python launch_ninjatrader.py
   ```

2. **Demo Features:**
   - ✅ Full interface testing
   - ✅ Simulated account data
   - ✅ All controls functional
   - ✅ No real money involved
   - ✅ Safe for experimentation

3. **What You'll See:**
   - 6 simulated Tradovate accounts
   - Fake but realistic trading data
   - All buttons and controls work
   - Connection status shows "Demo Mode"

---

### 🧪 **TEST REAL CONNECTIONS**

#### **Step 1: Test NinjaTrader Connection**
1. **Make sure NinjaTrader is running** on your computer
2. In the dashboard sidebar, select **"Live Connection Test"**
3. Click **🥷 Test NinjaTrader** button
4. System will check:
   - ✅ Is NinjaTrader process running?
   - ✅ Can it connect to NinjaTrader API?
   - ✅ What version is detected?

#### **Step 2: Test Tradovate Connection**
1. Enter your **Tradovate username/password** in sidebar
2. Click **🏛️ Test Tradovate** button
3. System will attempt to:
   - ✅ Connect to Tradovate API
   - ✅ Fetch your real account data
   - ✅ Display actual balances/positions

---

### ⚡ **LIVE TRADING MODE (Advanced)**

**⚠️ WARNING: Real money at risk!**

1. **Prerequisites:**
   - NinjaTrader 8 installed and running
   - Connected to Tradovate broker
   - Valid Tradovate account(s)
   - API access enabled

2. **Enable Live Mode:**
   - Select **"Full Live Trading"** in sidebar
   - Confirm you understand risks
   - System connects to real data

3. **Live Features:**
   - Real account balances
   - Actual position data
   - Live P&L tracking
   - Real margin calculations

---

## 🔧 **CONNECTION TROUBLESHOOTING**

### **NinjaTrader Not Connecting?**
1. ✅ **Check NinjaTrader is running**
2. ✅ **Enable NinjaTrader API:**
   - Tools → Options → Automated Trading Interface
   - Check "Enable NTI"
   - Set port to 36001
3. ✅ **Check Windows firewall** isn't blocking connections
4. ✅ **Restart NinjaTrader** and try again

### **Tradovate Not Connecting?**
1. ✅ **Verify credentials** are correct
2. ✅ **Check API access** is enabled in your Tradovate account
3. ✅ **Ensure account is funded** and active
4. ✅ **Try demo credentials** first if available

### **Dashboard Not Loading?**
1. ✅ **Install dependencies:**
   ```bash
   pip install streamlit pandas plotly psutil
   ```
2. ✅ **Check Python version** (3.8+ required)
3. ✅ **Run from correct directory**
4. ✅ **Try the launcher script:**
   ```bash
   python launch_ninjatrader.py
   ```

---

## 🎯 **WHAT EACH MODE DOES**

| Mode | Purpose | Data Source | Risk Level |
|------|---------|------------|------------|
| **Demo** | Learning/Testing | Simulated | 🟢 Zero Risk |
| **Connection Test** | Verify Setup | Mixed Real/Demo | 🟡 Read-Only |
| **Live Trading** | Real Trading | 100% Live | 🔴 Real Money |

---

## 📊 **HOW TO INTERPRET THE DASHBOARD**

### **Overall Margin Bar (Most Important!)**
- 🟢 **Green (70%+)**: Safe to trade
- 🟡 **Yellow (40-70%)**: Caution required  
- 🔴 **Red (<40%)**: Stop trading immediately!

### **Individual Account Boxes**
- **NT Connection**: 🟢 = Connected to NinjaTrader, 🔴 = Disconnected
- **Active Checkbox**: Turn account monitoring on/off
- **Instruments**: Which futures you're trading (ES, NQ, etc.)
- **Balance/Available**: Account equity and margin remaining

### **Controls**
- **🛑 Emergency Stop**: Halt ALL trading immediately
- **⏸️ Pause All**: Temporarily disable monitoring
- **▶️ Resume All**: Re-enable monitoring
- **🔄 Refresh Data**: Update all account information

---

## 🚀 **READY TO START?**

1. **First Time:** Start with Demo Mode
2. **Learning:** Test all buttons and features
3. **Setup:** Configure your trader profile in sidebar
4. **Test:** Try connection tests when ready
5. **Trade:** Switch to live mode only when confident

```bash
# Start here:
python launch_ninjatrader.py
```

**The system is designed to be safe - it starts in demo mode so you can't accidentally risk real money while learning!**
