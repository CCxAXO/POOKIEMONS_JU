import json
import base64
import os
from typing import Dict, Optional

class UserStorage:
    def __init__(self, storage_file='users.json'):
        self.storage_file = storage_file
        self.users = self._load_users()
        
        # Create default admin if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _encode_password(self, password: str) -> str:
        """Encode password to base64"""
        return base64.b64encode(password.encode()).decode()
    
    def _decode_password(self, encoded: str) -> str:
        """Decode password from base64"""
        return base64.b64decode(encoded.encode()).decode()
    
    def _create_default_admin(self):
        """Create default admin account"""
        self.users['admin'] = {
            'username': 'admin',
            'password': self._encode_password('admin123'),
            'role': 'admin',
            'company_symbol': None
        }
        self._save_users()
        print("✓ Default admin created (username: admin, password: admin123)")
    
    def create_user(self, username: str, password: str, role: str, 
                    company_symbol: str = None) -> bool:
        """Create a new user"""
        if username in self.users:
            return False
        
        self.users[username] = {
            'username': username,
            'password': self._encode_password(password),
            'role': role,
            'company_symbol': company_symbol
        }
        self._save_users()
        print(f"✓ User {username} created with role {role}")
        return True
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        stored_password = self._decode_password(user['password'])
        
        if password == stored_password:
            return {
                'username': user['username'],
                'role': user['role'],
                'company_symbol': user.get('company_symbol')
            }
        return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user info"""
        if username in self.users:
            user = self.users[username]
            return {
                'username': user['username'],
                'role': user['role'],
                'company_symbol': user.get('company_symbol')
            }
        return None
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return username in self.users
    
    def get_all_users(self) -> Dict:
        """Get all users (without passwords)"""
        return {
            username: {
                'username': data['username'],
                'role': data['role'],
                'company_symbol': data.get('company_symbol')
            }
            for username, data in self.users.items()
        }