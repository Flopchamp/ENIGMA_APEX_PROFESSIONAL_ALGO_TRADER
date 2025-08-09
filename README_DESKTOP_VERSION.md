# Training Wheels Desktop Version - Installation & Usage Guide

## 🖥️ DESKTOP VERSION - FULL FUNCTIONALITY

This is the **DESKTOP VERSION** of Training Wheels for Prop Firm Traders that includes ALL features:

✅ **Desktop notifications and audio alerts**  
✅ **Full NinjaTrader 8 connectivity (Socket + ATM)**  
✅ **Complete Tradovate API integration**  
✅ **OCR signal reading capabilities**  
✅ **Real-time WebSocket connections**  
✅ **Advanced Kelly Criterion calculations**  
✅ **Professional margin monitoring**  
✅ **Emergency stop functionality**  

---

## 🚀 QUICK START

### Method 1: One-Click Launch (Recommended)
1. **Double-click:** `LAUNCH_TRAINING_WHEELS_DESKTOP.bat`
2. **Wait for installation** (first time only)
3. **Dashboard opens** automatically in your browser

### Method 2: Manual Installation
```bash
# Install desktop requirements
pip install -r requirements_desktop.txt

# Launch desktop version
streamlit run streamlit_app_desktop.py --server.port=8502
```

---

## 📋 SYSTEM REQUIREMENTS

### Minimum Requirements
- **Windows 10/11** (recommended) or **macOS 10.14+** or **Linux**
- **Python 3.8+** installed and in PATH
- **8GB RAM** minimum, 16GB recommended
- **Internet connection** for package installation

### Trading Platform Requirements
- **NinjaTrader 8** (for NT8 connectivity)
- **Tradovate account** (for Tradovate integration)
- **Admin privileges** (for desktop notifications on Windows)

---

## 🔧 DESKTOP FEATURES

### 🔔 Desktop Notifications
- **Windows 10/11:** Native toast notifications
- **Cross-platform:** Plyer notifications
- **Audio alerts:** Beep patterns for different priorities
- **Customizable:** Enable/disable per notification type

### 🔌 NinjaTrader Integration
- **Socket Connection:** Direct TCP connection to NT8
- **ATM Integration:** Process-based connection detection
- **Real-time Data:** Account info, positions, orders
- **Order Placement:** Market, limit, and stop orders
- **Connection Monitoring:** Auto-reconnect functionality

### 📊 Tradovate Integration
- **REST API:** Account data and order management
- **WebSocket:** Real-time market data and updates
- **Demo/Live:** Support for both environments
- **Authentication:** Secure token-based login

### 👁️ OCR Signal Reading
- **Screen Capture:** Monitor specific screen regions
- **Text Recognition:** Extract trading signals from images
- **Pattern Matching:** Detect BUY/SELL/LONG/SHORT signals
- **Multi-region:** Monitor multiple areas simultaneously

---

## 📁 FILE STRUCTURE

```
ENIGMA_APEX_PROFESSIONAL_CLIENT_PACKAGE/
├── streamlit_app_desktop.py           # 🖥️ Desktop version (FULL features)
├── streamlit_app.py                   # ☁️ Cloud version (limited features)
├── requirements_desktop.txt           # Desktop dependencies
├── requirements.txt                   # Cloud dependencies  
├── LAUNCH_TRAINING_WHEELS_DESKTOP.bat # Desktop launcher
└── README_DESKTOP_VERSION.md          # This file
```

---

## ⚙️ CONFIGURATION

### NinjaTrader Setup
1. **Enable NTWebSocket:** In NT8 go to Tools → Options → General → check "Enable NTWebSocket"
2. **Socket Port:** Default is 36973 (configurable in settings)
3. **ATM Detection:** Automatically detects running NT8 processes

### Tradovate Setup
1. **Account:** Create demo or live Tradovate account
2. **Credentials:** Enter username/password in desktop settings
3. **Environment:** Choose demo or live environment

### Notification Setup
1. **Windows:** First notification will prompt for permissions
2. **Customization:** Configure per notification type in settings
3. **Audio:** Adjust volume levels and enable/disable per priority

---

## 🔧 TROUBLESHOOTING

### Common Issues

**"Python not found"**
- Install Python 3.8+ from https://python.org
- Make sure to check "Add to PATH" during installation

**"pip install failed"**
- Some packages are platform-specific (normal)
- Desktop version will still work with core functionality

**"NinjaTrader connection failed"**
- Ensure NT8 is running
- Check NTWebSocket is enabled in NT8 options
- Verify firewall isn't blocking port 36973

**"Desktop notifications not working"**
- On Windows: Allow notifications for Python.exe
- Run as administrator if needed
- Check Windows notification settings

**"Audio alerts not working"**
- Install `pygame` for cross-platform audio
- On Windows, `winsound` is used by default
- Check system volume levels

### Reset Installation
```bash
# Clean install
pip uninstall -r requirements_desktop.txt -y
pip install -r requirements_desktop.txt --upgrade --force-reinstall
```

---

## 📞 SUPPORT

### Documentation
- **Trading Guide:** `HARRISON_SETUP_GUIDE.md`
- **System Testing:** `PC_TESTING_CHECKLIST.md` 
- **Production Guide:** `PRODUCTION_DEPLOYMENT.md`

### Logging
- **Desktop logs:** `training_wheels_desktop.log`
- **Debug mode:** Set logging level to DEBUG in code
- **Error tracking:** All errors logged with timestamps

### Contact
- **GitHub Issues:** Report bugs and feature requests
- **Documentation:** Comprehensive guides included
- **Community:** Trading community support

---

## 🆚 DESKTOP vs CLOUD COMPARISON

| Feature | Desktop Version | Cloud Version |
|---------|----------------|---------------|
| **Notifications** | ✅ Full desktop alerts | ❌ Disabled |
| **NinjaTrader** | ✅ Socket + ATM connection | ❌ Cloud disabled |
| **Tradovate** | ✅ Full API integration | ⚠️ Limited (demo) |
| **OCR Reading** | ✅ Screen capture + recognition | ❌ Not available |
| **Audio Alerts** | ✅ System beeps + tones | ❌ Silent mode |
| **File Access** | ✅ Local file system | ❌ Sandboxed |
| **WebSockets** | ✅ Real-time connections | ⚠️ HTTP only |
| **Performance** | 🚀 Native speed | 🐌 Cloud limitations |
| **Installation** | 📦 One-time setup | 🌐 Instant access |

---

## 🔄 UPDATES

### Automatic Updates
- **Git integration:** Pull latest changes
- **Package updates:** `pip install --upgrade`
- **Version check:** Built-in version comparison

### Manual Updates
```bash
git pull origin main
pip install -r requirements_desktop.txt --upgrade
```

---

## 🎯 GETTING STARTED

1. **Run:** `LAUNCH_TRAINING_WHEELS_DESKTOP.bat`
2. **Connect:** Link your NinjaTrader and/or Tradovate accounts
3. **Configure:** Set up notification preferences
4. **Test:** Use the notification test feature
5. **Trade:** Start using the full desktop functionality!

**Happy Trading! 🚀**

---

*This is the complete desktop version with no compromises - all features enabled for serious prop firm traders.*
