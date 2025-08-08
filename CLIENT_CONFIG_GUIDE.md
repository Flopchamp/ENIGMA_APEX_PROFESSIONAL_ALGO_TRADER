# 🎯 ENIGMA APEX - Client Configuration Guide

## Quick Start Configuration

### 1️⃣ Configure Your Accounts
Run the configuration tool:
```powershell
cd system
python configure_accounts.py
```

This will open a user-friendly interface where you can:
- Set capital for each account
- Adjust risk percentages
- Set maximum contracts
- Configure NinjaTrader port

### 2️⃣ Account Setup Guide

For each trading account, you can configure:

#### Capital Allocation
- Enter your desired capital amount
- No preset minimums
- Adjust based on your trading plan

#### Risk Settings
- Set risk percentage (recommended: 1-3%)
- Adjust max contracts per trade
- Set according to your risk tolerance

#### Example Configuration
```
ES (S&P 500):
- Capital: Your choice (e.g., $10,000)
- Risk: Your choice (e.g., 2%)
- Max Contracts: Your choice (e.g., 1)

NQ (Nasdaq):
- Capital: Your choice
- Risk: Your choice
- Max Contracts: Your choice

... (and so on for all 6 accounts)
```

### 3️⃣ Save Your Configuration
1. Click "💾 Save Configuration"
2. Verify settings in status display
3. Configuration is saved automatically

### 4️⃣ NinjaTrader Setup
1. Open NinjaTrader
2. Go to Tools > Options
3. Check your ATI port
4. Enter this port in configuration tool

## 🔧 Making Changes

Need to adjust settings?
1. Run `configure_accounts.py` again
2. Make your changes
3. Click Save
4. Run quick test to verify

## ✅ Verification

After configuration:
1. Run the quick test:
```powershell
python quick_test.py
```
2. Verify all accounts show correct values
3. Check NinjaTrader connection
4. Confirm settings are as desired

## 🚨 Important Notes

1. **Capital Flexibility**
   - All capital amounts are flexible
   - Adjust to your account size
   - No minimum requirements

2. **Risk Management**
   - Set risk % appropriate for you
   - Position sizing auto-adjusts
   - Can be changed anytime

3. **Changes are Safe**
   - Configuration tool prevents errors
   - All changes are validated
   - Easy to reset if needed

## 💡 Tips

1. **Start Conservative**
   - Begin with smaller positions
   - Test with minimal risk
   - Scale up gradually

2. **Regular Checks**
   - Verify settings before trading
   - Run quick test daily
   - Monitor risk levels

3. **Making Adjustments**
   - Use configuration tool for all changes
   - Don't edit files directly
   - Test after any changes

## 🆘 Need Help?

If you need assistance:
1. Run quick test for diagnostics
2. Check the error messages
3. All settings can be adjusted
4. Configuration tool is always available

Remember: Your capital, your rules - the system adapts to your needs!
