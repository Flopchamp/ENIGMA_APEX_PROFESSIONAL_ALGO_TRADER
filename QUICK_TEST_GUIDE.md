# 🎯 ENIGMA APEX - Quick Test Guide

## 🚀 Pre-Market Testing Steps

### 1️⃣ Configure Your Accounts
1. Open configuration tool:
   ```
   python configure_accounts.py
   ```
2. Set your account capitals
3. Adjust risk settings
4. Save configuration

### 2️⃣ Start NinjaTrader
1. Open NinjaTrader 8
2. Go to Tools > Options
3. Select "Automated Trading Interface"
4. **Note your ATI port** (default: 36973)
5. Enter this port in the configuration tool
6. Click OK in NinjaTrader

### 3️⃣ Run Quick Test
1. Open command prompt
2. Navigate to system folder
3. Run: `python quick_test.py`
4. Watch for green ✅ checkmarks

### 3️⃣ Verify 6-Chart Setup
Each chart should be ready:
- ✅ ES (S&P 500 E-mini)
- ✅ NQ (Nasdaq E-mini)
- ✅ YM (Dow Jones E-mini)
- ✅ RTY (Russell 2000)
- ✅ GC (Gold)
- ✅ CL (Crude Oil)

### 4️⃣ Check Account Configuration
For each account, verify your settings:
1. ES Account (S&P 500 E-mini)
   - Check capital amount
   - Verify risk percentage
   - Confirm max contracts
2. NQ Account (Nasdaq E-mini)
   - Check capital amount
   - Verify risk percentage
   - Confirm max contracts
3. YM Account (Dow Jones E-mini)
   - Check capital amount
   - Verify risk percentage
   - Confirm max contracts
4. RTY Account (Russell 2000)
   - Check capital amount
   - Verify risk percentage
   - Confirm max contracts
5. GC Account (Gold Futures)
   - Check capital amount
   - Verify risk percentage
   - Confirm max contracts
6. CL Account (Crude Oil)
   - Check capital amount
   - Verify risk percentage
   - Confirm max contracts

💡 TIP: Use the configuration tool to adjust any settings

### 5️⃣ Test AlgoBox Connection
1. Launch AlgoBox
2. Wait for automatic connection
3. Verify all 6 charts connect
4. Check signal generation

## 🔍 What to Look For

### ✅ Connection Status
- NinjaTrader shows "Connected"
- AlgoBox shows "Ready"
- All 6 charts active

### ✅ Chart Verification
Each chart should show:
- Correct symbol
- Correct timeframe
- Live data feed
- Signal indicators

### ✅ Account Status
For each account verify:
- Correct capital amount
- Risk settings active
- Position limits set
- Account protection active

## ⚠️ Common Issues & Solutions

### 1. NinjaTrader Connection Failed
**Fix:**
1. Check NinjaTrader is running
2. Verify port 36973 in Options
3. Restart NinjaTrader if needed
4. Run quick test again

### 2. Charts Not Connecting
**Fix:**
1. Check trading_config.json
2. Verify chart symbols
3. Restart AlgoBox
4. Run quick test

### 3. Account Issues
**Fix:**
1. Check account settings
2. Verify risk parameters
3. Confirm capital allocation
4. Run quick test

## 🎯 Final Checklist

✅ **NinjaTrader:**
- [ ] Running
- [ ] Port 36973 configured
- [ ] ATI enabled

✅ **Charts:**
- [ ] All 6 charts visible
- [ ] Correct symbols loaded
- [ ] Live data flowing
- [ ] Indicators active

✅ **Accounts:**
- [ ] All 6 accounts ready
- [ ] Risk settings correct
- [ ] Position limits set
- [ ] Protection active

✅ **AlgoBox:**
- [ ] Connected to NinjaTrader
- [ ] All charts responding
- [ ] Signals generating
- [ ] System ready

## 🚨 Important Notes

1. **Time Check:**
   - Test well before market open
   - Allow time for adjustments
   - Verify all connections

2. **Risk Management:**
   - All accounts have protection
   - Position limits enforced
   - Stop-loss orders ready

3. **System Health:**
   - Monitor CPU usage
   - Check memory allocation
   - Verify network stability

4. **Backup Plans:**
   - Keep manual trading ready
   - Know emergency procedures
   - Have support contacts ready

## 📞 Quick Support

If you encounter issues:
1. Run quick_test.py again
2. Check error messages
3. Verify NinjaTrader settings
4. Restart if necessary

## 🎯 Ready to Trade?

When all checks are ✅ green:
1. Monitor all 6 charts
2. Watch account status
3. Start with small positions
4. Scale up gradually

Remember: Test everything thoroughly before market hours!

---

**System Status:** Ready for Testing  
**Next Step:** Run `quick_test.py`
