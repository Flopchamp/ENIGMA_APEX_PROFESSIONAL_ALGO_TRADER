#!/usr/bin/env python3
"""
Create a clean distribution package for the desktop version
Only includes essential files needed to run the application
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_clean_distribution():
    """Create a clean distribution ZIP with only essential files"""
    
    # Define essential files to include
    essential_files = [
        # Main application files
        "streamlit_app_desktop.py",
        "app.py",
        
        # Launch scripts
        "LAUNCH_TRAINING_WHEELS_DESKTOP.py",
        "launch_streamlit_dashboard.py",
        "launch_streamlit.py",
        
        # Configuration and setup
        "requirements.txt",
        "requirements_simple.txt",
        "apex_settings.json",
        
        # Core system files
        "harrison_original_complete_clean.py",
        "universal_trading_app.py",
        "production_api_manager.py",
        "secure_credential_manager.py",
        "prop_firm_compliance_engine.py",
        
        # Launcher batch files
        "LAUNCH_TRAINING_WHEELS_DESKTOP.bat",
        "QUICK_LAUNCH_HARRISON.bat",
        
        # Essential documentation
        "README.md",
        "SETUP_GUIDE.md",
        "HARRISON_SETUP_GUIDE.md",
        
        # Database files (if they exist and are small)
        "enigma_apex_pro.db",
        "trading_database.db",
    ]
    
    # Essential directories to include (with selective content)
    essential_directories = [
        "config/",
        "system/",
        "templates/",
    ]
    
    # Files/directories to explicitly exclude
    exclude_patterns = [
        "__pycache__/",
        "*.pyc",
        "*.log",
        "test_*",
        "*_test*",
        "*.tmp",
        ".git/",
        ".vscode/",
        "documentation/",
        "*TESTING*",
        "*TEST*",
        "PC_TESTING*",
        "system_test*",
        "test_system*",
        "VALIDATE_*",
        "comprehensive_functionality_validator.py",
        "pc_troubleshooter.py",
        "enigma_system_test.py",
        "test_components.py",
        "test_core_system.py",
        "test_integration.db",
        "system_integration_test.log",
        "production_test.log",
        "PRODUCTION_TEST_RESULTS.txt",
        "functionality_validation_report.json",
        "system_test_report.json",
        "apex_compliance.log",
        "ai_trading_analytics.db",
        "compliance_database.db",
    ]
    
    # Create clean distribution directory
    dist_dir = Path("ENIGMA_APEX_DESKTOP_CLEAN")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    print("Creating clean desktop distribution...")
    
    # Copy essential files
    for file_name in essential_files:
        file_path = Path(file_name)
        if file_path.exists():
            dest_path = dist_dir / file_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
            print(f"✅ Copied: {file_name}")
        else:
            print(f"⚠️  Missing: {file_name}")
    
    # Copy essential directories
    for dir_name in essential_directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            dest_dir = dist_dir / dir_name
            shutil.copytree(dir_path, dest_dir, 
                          ignore=shutil.ignore_patterns(*exclude_patterns))
            print(f"✅ Copied directory: {dir_name}")
    
    # Create a simple launcher script
    launcher_content = '''@echo off
echo Starting ENIGMA APEX Professional Desktop Version...
echo.
echo Installing required packages...
pip install -r requirements.txt
echo.
echo Launching Trading Dashboard...
python -m streamlit run streamlit_app_desktop.py --server.port=8501
pause
'''
    
    with open(dist_dir / "START_DESKTOP_VERSION.bat", "w") as f:
        f.write(launcher_content)
    
    # Create README for distribution
    readme_content = '''# ENIGMA APEX Professional Desktop Version

## Quick Start
1. Extract this ZIP file to a folder
2. Double-click `START_DESKTOP_VERSION.bat`
3. Wait for the browser to open automatically
4. Configure your NinjaTrader/Tradovate connections

## What's Included
- Full desktop version with all features
- Real desktop notifications and alerts
- NinjaTrader socket and ATM connections
- Tradovate REST API and WebSocket support
- OCR screen capture capabilities
- Audio alert system
- No cloud limitations

## Requirements
- Windows 10/11
- Python 3.8+ (will be installed if missing)
- Internet connection for initial setup

## Support
- Full setup guide: SETUP_GUIDE.md
- Harrison system: HARRISON_SETUP_GUIDE.md
- Issues: GitHub repository

Enjoy professional-grade prop firm trading!
'''
    
    with open(dist_dir / "README_DESKTOP.md", "w") as f:
        f.write(readme_content)
    
    # Create the clean ZIP file
    zip_filename = "ENIGMA_APEX_DESKTOP_CLEAN.zip"
    print(f"\nCreating ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
                print(f"📦 Added to ZIP: {arcname}")
    
    # Cleanup temp directory
    shutil.rmtree(dist_dir)
    
    # Get file size
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"\n✅ Clean distribution created: {zip_filename}")
    print(f"📦 File size: {zip_size:.2f} MB")
    print(f"🎯 Ready for distribution!")
    
    return zip_filename

if __name__ == "__main__":
    create_clean_distribution()
