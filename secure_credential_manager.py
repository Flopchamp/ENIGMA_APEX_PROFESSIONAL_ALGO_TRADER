"""
🔒 SECURE CREDENTIAL MANAGER
Enterprise-grade credential storage and management for production trading
Encrypts and securely stores API keys, passwords, and trading credentials
"""

import os
import json
import base64
import hashlib
import keyring
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
from dataclasses import dataclass, asdict
import getpass

@dataclass
class TradingCredentials:
    """Secure trading credentials structure"""
    platform: str
    username: str
    password: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    account_id: Optional[str] = None
    environment: str = "demo"  # demo, test, live
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class SecureCredentialManager:
    """Manages encrypted storage of trading platform credentials"""
    
    def __init__(self, master_password: Optional[str] = None, testing_mode: bool = False):
        self.logger = logging.getLogger(__name__)
        self.app_name = "ENIGMA_APEX_TRADER"
        self.testing_mode = testing_mode
        
        # Initialize encryption
        if master_password:
            self.master_password = master_password
        elif testing_mode:
            # Use default password for testing
            self.master_password = "testing_password_123"
        else:
            self.master_password = self._get_or_create_master_password()
        
        self.encryption_key = self._derive_encryption_key(self.master_password)
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Credential storage directory
        self.credentials_dir = os.path.join(os.path.expanduser("~"), ".enigma_apex", "credentials")
        os.makedirs(self.credentials_dir, exist_ok=True)
        
        self.logger.info("Secure credential manager initialized")
    
    def _get_or_create_master_password(self) -> str:
        """Get or create master password using system keyring"""
        try:
            # Try to get existing master password
            master_password = keyring.get_password(self.app_name, "master_password")
            
            if not master_password:
                # Create new master password
                print("🔒 First time setup - Creating secure master password")
                master_password = getpass.getpass("Enter master password for credential encryption: ")
                
                if len(master_password) < 8:
                    raise ValueError("Master password must be at least 8 characters")
                
                # Store in system keyring
                keyring.set_password(self.app_name, "master_password", master_password)
                self.logger.info("Master password created and stored securely")
            
            return master_password
            
        except Exception as e:
            self.logger.error(f"Error managing master password: {e}")
            # Fallback to environment variable
            master_password = os.getenv("ENIGMA_MASTER_PASSWORD")
            if not master_password:
                raise Exception("No master password available. Set ENIGMA_MASTER_PASSWORD environment variable.")
            return master_password
    
    def _derive_encryption_key(self, password: str) -> bytes:
        """Derive encryption key from master password using PBKDF2"""
        # Use a fixed salt for consistency (in production, consider unique per-user salts)
        salt = b"enigma_apex_trading_2024"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def store_credentials(self, platform: str, credentials: TradingCredentials) -> bool:
        """Store encrypted trading credentials"""
        try:
            # Validate credentials
            if not credentials.username or not credentials.password:
                raise ValueError("Username and password are required")
            
            # Create credential file path
            filename = f"{platform}_{credentials.environment}.json"
            filepath = os.path.join(self.credentials_dir, filename)
            
            # Prepare data for encryption
            credential_data = {
                "platform": credentials.platform,
                "username": credentials.username,
                "password": credentials.password,
                "api_key": credentials.api_key,
                "api_secret": credentials.api_secret,
                "account_id": credentials.account_id,
                "environment": credentials.environment,
                "created_at": credentials.created_at.isoformat(),
                "expires_at": credentials.expires_at.isoformat() if credentials.expires_at else None
            }
            
            # Encrypt the data
            json_data = json.dumps(credential_data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Store encrypted data
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info(f"Credentials stored securely for {platform} ({credentials.environment})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing credentials for {platform}: {e}")
            return False
    
    def get_credentials(self, platform: str, environment: str = "demo") -> Optional[TradingCredentials]:
        """Retrieve and decrypt trading credentials"""
        try:
            # Create credential file path
            filename = f"{platform}_{environment}.json"
            filepath = os.path.join(self.credentials_dir, filename)
            
            if not os.path.exists(filepath):
                self.logger.warning(f"No credentials found for {platform} ({environment})")
                return None
            
            # Read encrypted data
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            credential_data = json.loads(decrypted_data.decode())
            
            # Create credentials object
            credentials = TradingCredentials(
                platform=credential_data["platform"],
                username=credential_data["username"],
                password=credential_data["password"],
                api_key=credential_data.get("api_key"),
                api_secret=credential_data.get("api_secret"),
                account_id=credential_data.get("account_id"),
                environment=credential_data["environment"],
                created_at=datetime.fromisoformat(credential_data["created_at"]),
                expires_at=datetime.fromisoformat(credential_data["expires_at"]) if credential_data.get("expires_at") else None
            )
            
            # Check if credentials are expired
            if credentials.expires_at and datetime.now() > credentials.expires_at:
                self.logger.warning(f"Credentials for {platform} ({environment}) have expired")
                return None
            
            self.logger.info(f"Credentials retrieved for {platform} ({environment})")
            return credentials
            
        except Exception as e:
            self.logger.error(f"Error retrieving credentials for {platform}: {e}")
            return None
    
    def delete_credentials(self, platform: str, environment: str = "demo") -> bool:
        """Delete stored credentials"""
        try:
            filename = f"{platform}_{environment}.json"
            filepath = os.path.join(self.credentials_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"Credentials deleted for {platform} ({environment})")
                return True
            else:
                self.logger.warning(f"No credentials found to delete for {platform} ({environment})")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting credentials for {platform}: {e}")
            return False
    
    def list_stored_credentials(self) -> Dict[str, Dict[str, datetime]]:
        """List all stored credentials (metadata only)"""
        try:
            credentials_info = {}
            
            for filename in os.listdir(self.credentials_dir):
                if filename.endswith('.json'):
                    # Parse filename to get platform and environment
                    name_parts = filename[:-5].split('_')  # Remove .json extension
                    if len(name_parts) >= 2:
                        platform = '_'.join(name_parts[:-1])
                        environment = name_parts[-1]
                        
                        # Get file modification time
                        filepath = os.path.join(self.credentials_dir, filename)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if platform not in credentials_info:
                            credentials_info[platform] = {}
                        
                        credentials_info[platform][environment] = mod_time
            
            return credentials_info
            
        except Exception as e:
            self.logger.error(f"Error listing credentials: {e}")
            return {}
    
    def rotate_credentials(self, platform: str, environment: str, new_credentials: TradingCredentials) -> bool:
        """Rotate/update existing credentials"""
        try:
            # Store new credentials
            success = self.store_credentials(platform, new_credentials)
            
            if success:
                self.logger.info(f"Credentials rotated for {platform} ({environment})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error rotating credentials for {platform}: {e}")
            return False
    
    def export_credentials_backup(self, backup_password: str) -> str:
        """Export encrypted backup of all credentials"""
        try:
            # Create backup encryption key
            backup_key = self._derive_encryption_key(backup_password)
            backup_cipher = Fernet(backup_key)
            
            # Collect all credentials
            all_credentials = {}
            
            for filename in os.listdir(self.credentials_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.credentials_dir, filename)
                    with open(filepath, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Decrypt with current key, re-encrypt with backup key
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    re_encrypted_data = backup_cipher.encrypt(decrypted_data)
                    
                    all_credentials[filename] = base64.b64encode(re_encrypted_data).decode()
            
            # Create backup file
            backup_data = {
                "created_at": datetime.now().isoformat(),
                "app_version": "1.0",
                "credentials": all_credentials
            }
            
            backup_json = json.dumps(backup_data, indent=2)
            backup_filename = f"enigma_apex_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_filename, 'w') as f:
                f.write(backup_json)
            
            self.logger.info(f"Credentials backup exported to {backup_filename}")
            return backup_filename
            
        except Exception as e:
            self.logger.error(f"Error exporting credentials backup: {e}")
            return ""
    
    def test_credential_security(self) -> Dict[str, bool]:
        """Test the security of credential storage"""
        tests = {}
        
        try:
            # Test 1: Master password strength
            tests["master_password_secure"] = len(self.master_password) >= 8
            
            # Test 2: Encryption key derivation
            test_key = self._derive_encryption_key("test_password")
            tests["encryption_working"] = len(test_key) == 44  # Base64 encoded 32-byte key
            
            # Test 3: Directory permissions (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                dir_permissions = oct(os.stat(self.credentials_dir).st_mode)[-3:]
                tests["directory_secure"] = dir_permissions in ['700', '750']
            else:
                tests["directory_secure"] = True  # Windows handles this differently
            
            # Test 4: Encryption/decryption cycle
            test_data = "test_credential_data"
            try:
                encrypted = self.cipher_suite.encrypt(test_data.encode())
                decrypted = self.cipher_suite.decrypt(encrypted).decode()
                tests["encryption_cycle"] = (test_data == decrypted)
            except:
                tests["encryption_cycle"] = False
            
            self.logger.info(f"Security test results: {tests}")
            return tests
            
        except Exception as e:
            self.logger.error(f"Error during security tests: {e}")
            return {"error": True}

# Streamlit Integration
def integrate_with_streamlit():
    """Integration helper for Streamlit dashboard"""
    import streamlit as st
    
    # Initialize credential manager in session state
    if 'credential_manager' not in st.session_state:
        try:
            st.session_state.credential_manager = SecureCredentialManager()
        except Exception as e:
            st.error(f"Failed to initialize credential manager: {e}")
            return None
    
    return st.session_state.credential_manager

def render_credential_setup_ui():
    """Streamlit UI for credential setup"""
    import streamlit as st
    
    st.subheader("🔒 Secure Credential Management")
    
    credential_manager = integrate_with_streamlit()
    if not credential_manager:
        return
    
    # Show stored credentials
    stored_creds = credential_manager.list_stored_credentials()
    
    if stored_creds:
        st.markdown("### 📋 Stored Credentials")
        for platform, environments in stored_creds.items():
            with st.expander(f"🔑 {platform.title()}"):
                for env, mod_time in environments.items():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**Environment:** {env}")
                    with col2:
                        st.write(f"**Last Updated:** {mod_time.strftime('%Y-%m-%d %H:%M')}")
                    with col3:
                        if st.button("🗑️", key=f"delete_{platform}_{env}", help="Delete credentials"):
                            credential_manager.delete_credentials(platform, env)
                            st.rerun()
    
    # Add new credentials
    st.markdown("### ➕ Add New Credentials")
    
    with st.form("add_credentials"):
        platform = st.selectbox("Platform", ["tradovate", "ninjatrader", "interactive_brokers", "binance"])
        environment = st.selectbox("Environment", ["demo", "test", "live"])
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
            api_key = st.text_input("API Key (Optional)")
        with col2:
            password = st.text_input("Password", type="password")
            api_secret = st.text_input("API Secret (Optional)", type="password")
        
        account_id = st.text_input("Account ID (Optional)")
        
        submitted = st.form_submit_button("🔒 Store Credentials Securely")
        
        if submitted:
            if username and password:
                credentials = TradingCredentials(
                    platform=platform,
                    username=username,
                    password=password,
                    api_key=api_key if api_key else None,
                    api_secret=api_secret if api_secret else None,
                    account_id=account_id if account_id else None,
                    environment=environment
                )
                
                success = credential_manager.store_credentials(platform, credentials)
                if success:
                    st.success("✅ Credentials stored securely!")
                    st.rerun()
                else:
                    st.error("❌ Failed to store credentials")
            else:
                st.error("Username and password are required")
    
    # Security status
    with st.expander("🛡️ Security Status"):
        security_tests = credential_manager.test_credential_security()
        
        for test, passed in security_tests.items():
            if test == "error":
                st.error("Security test failed")
            else:
                icon = "✅" if passed else "❌"
                st.write(f"{icon} {test.replace('_', ' ').title()}: {'Passed' if passed else 'Failed'}")

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test the credential manager
    try:
        # Initialize with a test master password
        credential_manager = SecureCredentialManager("test_master_password_123")
        
        # Run security tests
        security_results = credential_manager.test_credential_security()
        print("Security Test Results:", security_results)
        
        # Store test credentials
        test_credentials = TradingCredentials(
            platform="tradovate",
            username="test_user",
            password="test_password",
            api_key="test_api_key",
            environment="demo"
        )
        
        success = credential_manager.store_credentials("tradovate", test_credentials)
        print(f"Store credentials: {success}")
        
        # Retrieve credentials
        retrieved = credential_manager.get_credentials("tradovate", "demo")
        print(f"Retrieved credentials: {retrieved.username if retrieved else 'None'}")
        
        # List stored credentials
        stored = credential_manager.list_stored_credentials()
        print(f"Stored credentials: {stored}")
        
    except Exception as e:
        print(f"Error: {e}")
