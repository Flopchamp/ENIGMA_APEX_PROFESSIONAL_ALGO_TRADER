# 🎯 ENIGMA APEX - First Principles Trading System
## For Michael Canfield - Live Trading Implementation

---

## 🧠 Philosophy: Back to First Principles

**Core Decision Logic:**
```
IF remaining_drawdown > 0 AND enigma_probability > threshold
THEN position_size = function(drawdown, probability)
ELSE skip_trade
```

---

## 🎯 The Only Two Things That Matter

### 1️⃣ **Remaining Drawdown (Per Apex Account)**
- Daily loss limit remaining: `$2,500 - losses_today`  
- Trailing drawdown remaining: `$8,000 - (peak - current)`
- Effective drawdown: `min(daily_remaining, trailing_remaining)`

### 2️⃣ **Enigma Signal Success Probability (Per Instrument)**
- Base success rate (your historical data)
- Time of day adjustments
- Market volatility factors  
- Recent performance weighting
- **NO HARD CODING** - You configure everything

---

## 🚀 How to Use the System

### Step 1: Launch the Interface
```bash
cd system
python launch_app.py
```

### Step 2: Configure Your Accounts (Dynamic)
- **No predetermined accounts** - You create them
- Add any Apex account: "APEX_ES_Michael", "APEX_NQ_Main", etc.
- Set your starting balance, daily limits, trailing limits
- System tracks current balance and calculates remaining drawdown

### Step 3: Configure Enigma Models (Per Instrument)
- Set base success rate for ES (e.g., 65%)
- Set base success rate for NQ (e.g., 70%) 
- Add volatility boosts, time factors, recent performance weights
- **You control every parameter**

### Step 4: Real-Time Trading
- System shows live decision matrix
- For each Enigma signal:
  - ✅ **GO**: Good drawdown + high probability
  - 🛑 **STOP**: No drawdown remaining  
  - ⚠️ **CAUTION**: Low drawdown or low probability
  - ⏸️ **SKIP**: Poor probability

---

## 🔧 Technical Implementation

### Files Created:
1. **`first_principles_trader.py`** - Main Streamlit interface
2. **`michael_trading_config.json`** - Dynamic configuration (no hard coding)
3. **`launch_app.py`** - Easy launcher
4. Integration with existing NinjaTrader (port 36973)

### Key Features:
- ✅ **No Hard Coding** - Everything is configurable
- ✅ **Real-time drawdown calculation**
- ✅ **Dynamic Enigma probability models** 
- ✅ **Instant trading decisions**
- ✅ **Export/import configurations**
- ✅ **Works with your existing AlgoBox setup**

---

## 📊 Example Live Decision Matrix

| Account | Instrument | Remaining DD | Enigma Prob | Decision |
|---------|------------|--------------|-------------|----------|
| APEX_ES_1 | ES | $1,300 | 78% | 🟢 **GO** - 2 contracts |
| APEX_NQ_1 | NQ | $200 | 82% | ⚠️ **CAUTION** - 1 contract |
| APEX_YM_1 | YM | $0 | 65% | 🛑 **STOP** - No trades |
| APEX_RTY_1 | RTY | $1,800 | 45% | ⏸️ **SKIP** - Low probability |

---

## 🎯 What Changed from Previous Version

### OLD (Complex):
- Hard-coded 6 accounts
- Fixed risk percentages
- Complex Kelly Criterion calculations
- Too many settings

### NEW (First Principles):
- Dynamic account creation
- Focus only on: Drawdown + Probability
- Simple decision logic
- User controls everything
- No complexity hiding the essentials

---

## 🚀 Next Steps for Testing

1. **Launch the system**: `python launch_app.py`
2. **Add your real Apex accounts** with actual balances
3. **Configure Enigma success rates** based on your experience
4. **Test with paper trading** first
5. **Go live** when confident

---

## 📞 Status: Ready for Michael's Testing

✅ **System Status**: Complete and ready  
✅ **Philosophy**: Back to first principles  
✅ **Flexibility**: No hard coding, fully dynamic  
✅ **Integration**: Works with existing NinjaTrader/AlgoBox  
✅ **Focus**: Drawdown + Enigma Probability = Decision  

**The system now does exactly what you asked for - focuses on the two things that actually matter for live trading decisions.**
