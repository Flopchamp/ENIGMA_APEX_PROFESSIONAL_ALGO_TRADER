# Apex Compliance Guardian - Streamlit Cloud

## Streamlit Cloud Deployment

This is a cloud-optimized version of the Apex Compliance Guardian for prop firm traders.

### Main Entry Point
- **File**: `streamlit_app.py`
- **Requirements**: `requirements.txt`

### Features
- ✅ Apex Trader Funding rule compliance monitoring
- ✅ Real-time risk meters and gauges  
- ✅ P&L tracking and visualization
- ✅ Daily loss and trailing drawdown monitoring
- ✅ Consistency rule checking
- ✅ Cloud-optimized with minimal dependencies

### Deployment Steps for Streamlit Cloud

1. Push this repository to GitHub
2. Go to https://share.streamlit.io/
3. Sign in with your GitHub account
4. Click "New app"
5. Select this repository
6. Set the main file path to: `streamlit_app.py`
7. Deploy!

### Configuration

The app is configured for Apex Trader Funding rules:
- 5% daily loss limit
- 5% trailing drawdown threshold  
- 8% profit target (Evaluation) / 5% (PA)
- 30% consistency rule
- Position size limits

### Usage

1. Set your account balance and phase in the sidebar
2. Enter your current daily P&L and total P&L
3. Monitor compliance status in real-time
4. Use the risk meters to stay within limits

---
**Training Wheels for Prop Firm Traders** 🛡️
