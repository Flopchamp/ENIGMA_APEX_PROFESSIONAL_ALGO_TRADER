"""
🔧 ENIGMA APEX PROFESSIONAL - PC TROUBLESHOOTING ASSISTANT
Interactive diagnostic tool to help users fix common PC setup issues
"""

import sys
import os
import subprocess
import platform
import socket
from datetime import datetime

class PCTroubleshooter:
    """Interactive troubleshooting assistant for PC-specific issues"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.python_version = sys.version_info
        self.issues_found = []
        self.fixes_applied = []
        
    def print_header(self):
        """Print troubleshooting header"""
        print("=" * 60)
        print("🔧 ENIGMA APEX PROFESSIONAL - PC TROUBLESHOOTING")
        print("=" * 60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Operating System: {platform.system()} {platform.release()}")
        print(f"Python Version: {sys.version}")
        print("-" * 60)
    
    def diagnose_python_issues(self):
        """Diagnose Python-related problems"""
        print("🐍 Diagnosing Python Issues...")
        
        # Check Python version
        if self.python_version.major < 3 or self.python_version.minor < 8:
            self.issues_found.append("Python version too old")
            print("   ❌ Python version is too old (need 3.8+)")
            self.suggest_python_fix()
        else:
            print("   ✅ Python version is compatible")
        
        # Check pip availability
        try:
            import pip
            print("   ✅ pip is available")
        except ImportError:
            self.issues_found.append("pip not available")
            print("   ❌ pip is not available")
            self.suggest_pip_fix()
        
        # Check if Python is in PATH
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Python is in PATH")
            else:
                self.issues_found.append("Python not in PATH")
                print("   ❌ Python is not in PATH")
                self.suggest_path_fix()
        except FileNotFoundError:
            self.issues_found.append("Python command not found")
            print("   ❌ Python command not found")
            self.suggest_path_fix()
    
    def diagnose_package_issues(self):
        """Diagnose package installation problems"""
        print("\n📦 Diagnosing Package Issues...")
        
        required_packages = [
            'streamlit', 'pandas', 'numpy', 'plotly', 
            'requests', 'websockets', 'cryptography', 'psutil'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package} - Available")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} - Missing")
        
        if missing_packages:
            self.issues_found.append(f"Missing packages: {missing_packages}")
            self.suggest_package_fix(missing_packages)
    
    def diagnose_network_issues(self):
        """Diagnose network connectivity problems"""
        print("\n🌍 Diagnosing Network Issues...")
        
        test_hosts = [
            ("Google DNS", "8.8.8.8", 53),
            ("PyPI", "pypi.org", 80),
            ("Streamlit", "streamlit.io", 80)
        ]
        
        network_issues = []
        
        for name, host, port in test_hosts:
            try:
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
                print(f"   ✅ {name} - Reachable")
            except (socket.error, socket.timeout):
                network_issues.append(name)
                print(f"   ❌ {name} - Unreachable")
        
        if network_issues:
            self.issues_found.append(f"Network connectivity issues: {network_issues}")
            self.suggest_network_fix()
    
    def diagnose_streamlit_issues(self):
        """Diagnose Streamlit-specific problems"""
        print("\n🌐 Diagnosing Streamlit Issues...")
        
        # Check Streamlit import
        try:
            import streamlit
            print("   ✅ Streamlit imports successfully")
            
            # Check Streamlit CLI
            try:
                result = subprocess.run(['streamlit', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ Streamlit CLI works: {result.stdout.strip()}")
                else:
                    self.issues_found.append("Streamlit CLI not working")
                    print("   ❌ Streamlit CLI not working")
                    self.suggest_streamlit_fix()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.issues_found.append("Streamlit CLI timeout/not found")
                print("   ❌ Streamlit CLI timeout or not found")
                self.suggest_streamlit_fix()
                
        except ImportError:
            self.issues_found.append("Streamlit not installed")
            print("   ❌ Streamlit not installed")
            self.suggest_streamlit_install()
    
    def diagnose_permissions_issues(self):
        """Diagnose file/directory permission problems"""
        print("\n🔐 Diagnosing Permission Issues...")
        
        # Check write permissions in current directory
        test_file = "test_permissions.tmp"
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("   ✅ Write permissions - OK")
        except (PermissionError, OSError):
            self.issues_found.append("No write permissions")
            print("   ❌ No write permissions in current directory")
            self.suggest_permission_fix()
        
        # Check if running as admin (Windows)
        if self.os_type == "Windows":
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if is_admin:
                    print("   ✅ Running as Administrator")
                else:
                    print("   ⚠️  Not running as Administrator")
                    print("      (May be needed for some operations)")
            except:
                print("   ⚠️  Cannot determine admin status")
    
    def suggest_python_fix(self):
        """Suggest fixes for Python issues"""
        print("\n💡 PYTHON FIX SUGGESTIONS:")
        print("1. Download Python 3.8+ from https://python.org")
        print("2. During installation, check 'Add to PATH'")
        print("3. Restart your computer after installation")
        print("4. Test with: python --version")
    
    def suggest_pip_fix(self):
        """Suggest fixes for pip issues"""
        print("\n💡 PIP FIX SUGGESTIONS:")
        if self.os_type == "Windows":
            print("1. Try: python -m ensurepip --upgrade")
            print("2. Or: python -m pip install --upgrade pip")
        else:
            print("1. Try: python3 -m ensurepip --upgrade")
            print("2. Or: curl https://bootstrap.pypa.io/get-pip.py | python3")
    
    def suggest_path_fix(self):
        """Suggest PATH fixes"""
        print("\n💡 PATH FIX SUGGESTIONS:")
        if self.os_type == "Windows":
            print("1. Search 'Environment Variables' in Start menu")
            print("2. Add Python installation directory to PATH")
            print("3. Typical location: C:\\Python39 or C:\\Users\\YourName\\AppData\\Local\\Programs\\Python")
        else:
            print("1. Add to ~/.bashrc or ~/.zshrc:")
            print("   export PATH=\"/usr/local/bin/python3:$PATH\"")
            print("2. Reload with: source ~/.bashrc")
    
    def suggest_package_fix(self, packages):
        """Suggest package installation fixes"""
        print("\n💡 PACKAGE INSTALLATION FIXES:")
        package_list = " ".join(packages)
        
        print("Try these commands:")
        if self.os_type == "Windows":
            print(f"1. pip install {package_list}")
            print(f"2. python -m pip install {package_list}")
            print("3. pip install --user {package_list}")
        else:
            print(f"1. pip3 install {package_list}")
            print(f"2. python3 -m pip install {package_list}")
            print("3. sudo pip3 install {package_list}")
        
        print("\nIf still failing:")
        print("- Update pip: pip install --upgrade pip")
        print("- Clear cache: pip cache purge")
        print("- Try with --no-cache-dir flag")
    
    def suggest_network_fix(self):
        """Suggest network fixes"""
        print("\n💡 NETWORK FIX SUGGESTIONS:")
        print("1. Check your internet connection")
        print("2. Disable VPN temporarily")
        print("3. Check firewall settings")
        print("4. Try from different network (mobile hotspot)")
        print("5. Corporate networks: Contact IT about proxy settings")
        
        if self.os_type == "Windows":
            print("6. Windows: Check Windows Defender Firewall")
            print("7. Try: netsh winsock reset (as Administrator)")
    
    def suggest_streamlit_fix(self):
        """Suggest Streamlit fixes"""
        print("\n💡 STREAMLIT FIX SUGGESTIONS:")
        print("1. Reinstall Streamlit:")
        print("   pip uninstall streamlit")
        print("   pip install streamlit")
        print("2. Clear Streamlit cache:")
        print("   streamlit cache clear")
        print("3. Try different port:")
        print("   streamlit run app.py --server.port 8502")
        print("4. Check for conflicting applications on port 8501")
    
    def suggest_streamlit_install(self):
        """Suggest Streamlit installation"""
        print("\n💡 STREAMLIT INSTALLATION:")
        print("pip install streamlit")
        print("Test with: streamlit hello")
    
    def suggest_permission_fix(self):
        """Suggest permission fixes"""
        print("\n💡 PERMISSION FIX SUGGESTIONS:")
        if self.os_type == "Windows":
            print("1. Run Command Prompt as Administrator")
            print("2. Right-click folder → Properties → Security → Edit")
            print("3. Give your user account Full Control")
        else:
            print("1. Check folder permissions: ls -la")
            print("2. Change ownership: sudo chown -R $USER:$USER .")
            print("3. Set permissions: chmod 755 .")
    
    def run_interactive_diagnosis(self):
        """Run interactive diagnosis with user prompts"""
        self.print_header()
        
        print("Starting interactive PC diagnosis...\n")
        
        # Run all diagnostic tests
        self.diagnose_python_issues()
        self.diagnose_package_issues()
        self.diagnose_network_issues()
        self.diagnose_streamlit_issues()
        self.diagnose_permissions_issues()
        
        # Summary
        print("\n" + "=" * 60)
        print("🔍 DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        if not self.issues_found:
            print("🎉 No issues found! Your PC should be ready.")
            print("Try running: python enigma_system_test.py")
        else:
            print(f"Found {len(self.issues_found)} issues:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"{i}. {issue}")
            
            print("\nRecommended next steps:")
            print("1. Apply the suggested fixes above")
            print("2. Restart your computer if needed")
            print("3. Re-run this troubleshooter")
            print("4. Then run: python enigma_system_test.py")
        
        print("=" * 60)
    
    def quick_fix_menu(self):
        """Interactive menu for quick fixes"""
        print("\n🛠️ QUICK FIX MENU")
        print("1. Install all required packages")
        print("2. Update pip")
        print("3. Test network connectivity")
        print("4. Reinstall Streamlit")
        print("5. Run full system test")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            self.auto_install_packages()
        elif choice == "2":
            self.auto_update_pip()
        elif choice == "3":
            self.diagnose_network_issues()
        elif choice == "4":
            self.auto_reinstall_streamlit()
        elif choice == "5":
            os.system("python enigma_system_test.py")
        elif choice == "0":
            print("Goodbye!")
        else:
            print("Invalid choice. Please try again.")
            self.quick_fix_menu()
    
    def auto_install_packages(self):
        """Automatically install required packages"""
        print("Installing required packages...")
        packages = "streamlit pandas numpy plotly requests websockets cryptography psutil"
        
        try:
            result = subprocess.run(f"pip install {packages}", shell=True, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Packages installed successfully!")
                self.fixes_applied.append("Installed packages")
            else:
                print(f"❌ Installation failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Installation error: {e}")
    
    def auto_update_pip(self):
        """Automatically update pip"""
        print("Updating pip...")
        try:
            result = subprocess.run("python -m pip install --upgrade pip", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ pip updated successfully!")
                self.fixes_applied.append("Updated pip")
            else:
                print(f"❌ pip update failed: {result.stderr}")
        except Exception as e:
            print(f"❌ pip update error: {e}")
    
    def auto_reinstall_streamlit(self):
        """Automatically reinstall Streamlit"""
        print("Reinstalling Streamlit...")
        try:
            # Uninstall
            subprocess.run("pip uninstall streamlit -y", shell=True, 
                         capture_output=True, text=True)
            # Reinstall
            result = subprocess.run("pip install streamlit", shell=True, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Streamlit reinstalled successfully!")
                self.fixes_applied.append("Reinstalled Streamlit")
            else:
                print(f"❌ Streamlit reinstall failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Streamlit reinstall error: {e}")

def main():
    """Main troubleshooting function"""
    troubleshooter = PCTroubleshooter()
    
    print("Choose troubleshooting mode:")
    print("1. Full automatic diagnosis")
    print("2. Quick fix menu")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        troubleshooter.run_interactive_diagnosis()
        
        # Offer quick fixes if issues found
        if troubleshooter.issues_found:
            fix_choice = input("\nWould you like to try automatic fixes? (y/n): ").lower()
            if fix_choice == 'y':
                troubleshooter.quick_fix_menu()
    
    elif choice == "2":
        troubleshooter.quick_fix_menu()
    
    elif choice == "3":
        print("Goodbye!")
    
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
