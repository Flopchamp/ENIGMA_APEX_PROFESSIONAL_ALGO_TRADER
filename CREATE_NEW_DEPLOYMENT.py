#!/usr/bin/env python3
"""
🚀 ENIGMA APEX - NEW DEPLOYMENT HELPER
Creates a new Streamlit Cloud deployment using the deploy branch
"""

import webbrowser
import sys
from datetime import datetime

def main():
    """Create new Streamlit deployment"""
    
    print("🚀 ENIGMA APEX - NEW STREAMLIT DEPLOYMENT")
    print("=" * 60)
    print("🎯 CREATING NEW APP WITH DEPLOY BRANCH")
    print("📅 Setup Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    print()
    
    print("📋 DEPLOYMENT CONFIGURATION:")
    print("-" * 40)
    print("🔗 Repository: Flopchamp/ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER")
    print("🌿 Branch: deploy (your current branch with all updates)")
    print("📄 Main File: STREAMLIT_PRODUCTION_APP.py")
    print("🌐 Suggested URL: enigma-apex-professional")
    print("🎯 Features: Complete 8-module trading platform")
    print()
    
    print("✅ WHAT'S INCLUDED IN DEPLOY BRANCH:")
    features = [
        "Professional Trading Dashboard",
        "Live Trading Interface (LIVE mode ready)",
        "Real-time Signal Detection",
        "Advanced Risk Management",
        "NinjaTrader Integration",
        "Server Connection (155.138.229.220)",
        "Desktop Notifications",
        "Complete Documentation"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"  {i}. ✅ {feature}")
    
    print("\n🚀 DEPLOYMENT OPTIONS:")
    print("=" * 50)
    
    choice = input("\nSelect deployment method:\n1. Open Streamlit Cloud (manual setup)\n2. Show deployment instructions\n3. Exit\n\nChoice (1-3): ").strip()
    
    if choice == "1":
        open_streamlit_cloud()
    elif choice == "2":
        show_deployment_instructions()
    elif choice == "3":
        print("👋 Deployment cancelled")
    else:
        print("❌ Invalid choice")

def open_streamlit_cloud():
    """Open Streamlit Cloud for manual deployment"""
    
    print("\n🌐 OPENING STREAMLIT CLOUD...")
    print("-" * 40)
    
    try:
        webbrowser.open("https://share.streamlit.io/")
        print("✅ Streamlit Cloud opened in your browser")
        print()
        print("📋 FOLLOW THESE STEPS:")
        print("1. Click 'New app'")
        print("2. Repository: Flopchamp/ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER")
        print("3. Branch: deploy ← IMPORTANT!")
        print("4. Main file: STREAMLIT_PRODUCTION_APP.py ← IMPORTANT!")
        print("5. App URL: enigma-apex-professional (or your choice)")
        print("6. Click 'Deploy!'")
        print()
        print("⏱️ Your new app will be ready in 2-3 minutes!")
        
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print("🌐 Please manually visit: https://share.streamlit.io/")

def show_deployment_instructions():
    """Show detailed deployment instructions"""
    
    print("\n📋 DETAILED DEPLOYMENT INSTRUCTIONS:")
    print("=" * 50)
    
    steps = [
        {
            "step": "1. Access Streamlit Cloud",
            "action": "Visit https://share.streamlit.io/",
            "details": "Sign in with your GitHub account"
        },
        {
            "step": "2. Create New App",
            "action": "Click 'New app' button",
            "details": "Start the deployment process"
        },
        {
            "step": "3. Repository Settings",
            "action": "Select your repository",
            "details": "Flopchamp/ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER"
        },
        {
            "step": "4. Branch Selection",
            "action": "Change branch to 'deploy'",
            "details": "⚠️ CRITICAL: Must be 'deploy' not 'main'"
        },
        {
            "step": "5. Main File Path",
            "action": "Set main file path",
            "details": "STREAMLIT_PRODUCTION_APP.py"
        },
        {
            "step": "6. App URL",
            "action": "Choose custom URL",
            "details": "enigma-apex-professional (suggested)"
        },
        {
            "step": "7. Deploy",
            "action": "Click 'Deploy!' button",
            "details": "Wait 2-3 minutes for deployment"
        }
    ]
    
    for step in steps:
        print(f"\n{step['step']}:")
        print(f"   Action: {step['action']}")
        print(f"   Details: {step['details']}")
    
    print("\n🎯 RESULT:")
    print("Your new URL will be something like:")
    print("https://enigma-apex-professional.streamlit.app/")
    print()
    print("🏆 FEATURES YOU'LL GET:")
    print("✅ Professional 8-module trading interface")
    print("✅ LIVE trading mode ready")
    print("✅ Server connection configured")
    print("✅ Complete documentation")
    print("✅ All latest updates and improvements")

def create_deployment_summary():
    """Create deployment summary file"""
    
    summary = f"""
# 🚀 NEW STREAMLIT DEPLOYMENT SUMMARY

## 📅 Deployment Setup
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Branch:** deploy
**Main File:** STREAMLIT_PRODUCTION_APP.py

## 🎯 Deployment Configuration

### Required Settings:
```
Repository: Flopchamp/ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER
Branch: deploy
Main file path: STREAMLIT_PRODUCTION_APP.py
App URL: enigma-apex-professional
```

### Features Included:
- ✅ Professional Trading Dashboard
- ✅ Live Trading Mode (LIVE ready)
- ✅ 8 Complete Trading Modules
- ✅ Server Connection (155.138.229.220)
- ✅ Risk Management (Conservative settings)
- ✅ NinjaTrader Integration
- ✅ Complete Documentation

## 🌐 Expected Result:
New URL: https://enigma-apex-professional.streamlit.app/

## 🎯 Advantages of New Deployment:
1. Uses latest deploy branch with all updates
2. Professional STREAMLIT_PRODUCTION_APP.py interface
3. LIVE trading mode pre-configured
4. All 8 modules fully functional
5. Server connection ready
6. Conservative risk settings
7. Complete client documentation

## 🚀 Your client will have a production-ready trading platform!
"""
    
    with open('NEW_DEPLOYMENT_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ Deployment summary saved to: NEW_DEPLOYMENT_SUMMARY.md")

if __name__ == "__main__":
    main()
    create_deployment_summary()
