#!/usr/bin/env python3
"""
📥 ENIGMA APEX CLIENT DOWNLOAD PACKAGE CREATOR
Creates downloadable package for client distribution
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class ClientPackageCreator:
    """Creates client download package"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.package_name = f"ENIGMA_APEX_CLIENT_PACKAGE_{datetime.now().strftime('%Y%m%d')}"
        self.output_dir = self.base_path / "dist"
        
    def create_package_structure(self):
        """Create package directory structure"""
        print("📁 Creating package structure...")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        package_dir = self.output_dir / self.package_name
        
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir()
        
        # Core directories to include
        core_dirs = [
            'system',
            'ninjatrader',
            'documentation',
            '.streamlit'
        ]
        
        # Core files to include
        core_files = [
            'ENIGMA_APEX_COMPLETE_SYSTEM.py',
            'TRAINING_MODE_LAUNCHER.py',
            'CLIENT_NOTIFICATION_DEMO.py',
            'PRODUCTION_VALIDATION.py',
            'requirements.txt',
            '.env',
            'README.md',
            'SOFTWARE_DOWNLOAD_GUIDE.md',
            'NINJATRADER_ALGOBOX_CONNECTION_GUIDE.md',
            'PRODUCTION_RELEASE_GUIDE.md'
        ]
        
        # Copy directories
        for dir_name in core_dirs:
            src_dir = self.base_path / dir_name
            if src_dir.exists():
                dst_dir = package_dir / dir_name
                shutil.copytree(src_dir, dst_dir)
                print(f"✅ Copied directory: {dir_name}")
            else:
                print(f"⚠️ Directory not found: {dir_name}")
        
        # Copy files
        for file_name in core_files:
            src_file = self.base_path / file_name
            if src_file.exists():
                dst_file = package_dir / file_name
                shutil.copy2(src_file, dst_file)
                print(f"✅ Copied file: {file_name}")
            else:
                print(f"⚠️ File not found: {file_name}")
        
        return package_dir
        
    def create_client_readme(self, package_dir):
        """Create client-specific README"""
        readme_content = """# 🎯 ENIGMA APEX PROFESSIONAL TRADING SYSTEM
**Client Download Package**

## 🚀 QUICK START

### Option 1: Web Access (Recommended)
1. Open browser and go to: **https://your-streamlit-app.streamlit.app**
2. Enable browser notifications when prompted
3. Start trading with professional risk management

### Option 2: Local Installation
1. Extract this package to `C:\\EnigmaApex\\`
2. Install Python 3.11+ from python.org
3. Run: `pip install -r requirements.txt`
4. Start training: `python TRAINING_MODE_LAUNCHER.py`

## 📚 DOCUMENTATION
- **SOFTWARE_DOWNLOAD_GUIDE.md** - Complete download and setup instructions
- **NINJATRADER_ALGOBOX_CONNECTION_GUIDE.md** - Connect to NinjaTrader
- **PRODUCTION_RELEASE_GUIDE.md** - Production trading setup
- **documentation/** - Complete user manuals and guides

## 🔧 VALIDATION
Run system check: `python PRODUCTION_VALIDATION.py`

## 🎯 TRAINING
Safe learning environment: `python TRAINING_MODE_LAUNCHER.py`

## 🔔 NOTIFICATIONS
Test alerts: `python CLIENT_NOTIFICATION_DEMO.py`

## 📞 SUPPORT
All documentation and guides included in package.

**Happy Trading!** 🚀
"""
        
        readme_file = package_dir / "CLIENT_README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ Created client README")
        
    def create_streamlit_info(self, package_dir):
        """Create Streamlit deployment info"""
        streamlit_info = """# 🌐 STREAMLIT CLOUD DEPLOYMENT

## Main Application File
```
system/apex_compliance_guardian_streamlit.py
```

## Deployment Settings
- **Main file path**: `system/apex_compliance_guardian_streamlit.py`
- **Python version**: 3.11
- **Port**: 8501
- **Dependencies**: All listed in requirements.txt

## Repository Settings
- **Repository**: `https://github.com/Flopchamp/ENIGMA_APEX_PROFESSIONAL_ALGO_TRADER`
- **Branch**: `deploy`
- **Requirements**: `requirements.txt`

## Web Access
Your application will be available at:
- `https://your-app-name.streamlit.app`
- `https://enigma-apex-professional.streamlit.app`

## Configuration Files
- `.streamlit/config.toml` - Streamlit configuration
- `.env` - Environment variables (configure before deployment)
- `requirements.txt` - Python dependencies

## Features Available in Web Version
- ✅ Real-time trading dashboard
- ✅ Risk management controls  
- ✅ Browser notifications
- ✅ Mobile responsive design
- ✅ Professional charts and analytics
- ✅ Apex compliance monitoring

**Your Streamlit app is ready for professional trading!** 🚀
"""
        
        streamlit_file = package_dir / "STREAMLIT_DEPLOYMENT_INFO.md"
        with open(streamlit_file, 'w', encoding='utf-8') as f:
            f.write(streamlit_info)
            
        print("✅ Created Streamlit deployment info")
        
    def create_zip_package(self, package_dir):
        """Create ZIP file for distribution"""
        print("📦 Creating ZIP package...")
        
        zip_file = self.output_dir / f"{self.package_name}.zip"
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        # Get file size
        file_size_mb = zip_file.stat().st_size / (1024 * 1024)
        
        print(f"✅ Created ZIP package: {zip_file.name}")
        print(f"📊 Package size: {file_size_mb:.1f} MB")
        
        return zip_file
        
    def create_download_instructions(self, zip_file):
        """Create download instructions file"""
        instructions = f"""# 📥 ENIGMA APEX DOWNLOAD INSTRUCTIONS

## Package Information
- **Package Name**: {zip_file.name}
- **Creation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Package Size**: {zip_file.stat().st_size / (1024 * 1024):.1f} MB
- **Contents**: Complete Enigma Apex trading system

## Download Steps
1. **Download the ZIP file**: {zip_file.name}
2. **Extract to**: C:\\EnigmaApex\\
3. **Read**: CLIENT_README.md for setup instructions
4. **Choose access method**:
   - Web access (recommended): No installation needed
   - Local installation: Follow setup guide

## What's Included
- ✅ Complete trading system
- ✅ NinjaTrader integration files
- ✅ Training mode launcher
- ✅ Notification system
- ✅ Risk management tools
- ✅ Complete documentation
- ✅ Streamlit cloud configuration

## Support
All documentation and troubleshooting guides included in package.

**Ready for professional trading!** 🎯
"""
        
        instructions_file = self.output_dir / "DOWNLOAD_INSTRUCTIONS.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
            
        print(f"✅ Created download instructions")
        
    def create_client_package(self):
        """Create complete client download package"""
        print("🚀 CREATING ENIGMA APEX CLIENT PACKAGE")
        print("=" * 60)
        
        # Create package structure
        package_dir = self.create_package_structure()
        
        # Add client-specific files
        self.create_client_readme(package_dir)
        self.create_streamlit_info(package_dir)
        
        # Create ZIP distribution
        zip_file = self.create_zip_package(package_dir)
        
        # Create download instructions
        self.create_download_instructions(zip_file)
        
        print("\n" + "=" * 60)
        print("🎉 CLIENT PACKAGE CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📦 Package Location: {zip_file}")
        print(f"📁 Package Directory: {package_dir}")
        print(f"📄 Instructions: {self.output_dir}/DOWNLOAD_INSTRUCTIONS.md")
        print()
        print("📋 DISTRIBUTION OPTIONS:")
        print("1. 🌐 Streamlit Cloud: Deploy directly from repository")
        print("2. 📦 ZIP Download: Provide ZIP file to client")
        print("3. 📧 Email: Send download link and instructions")
        print("4. 💾 USB/Cloud: Physical or cloud storage distribution")
        print()
        print("🎯 Your client now has everything needed for professional trading!")

def main():
    """Main package creation function"""
    try:
        creator = ClientPackageCreator()
        creator.create_client_package()
        
    except Exception as e:
        print(f"❌ Package creation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
