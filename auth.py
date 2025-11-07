from typing import Dict, Optional
import secrets
from user_storage import UserStorage

class User:
    def __init__(self, username: str, role: str, company_symbol: str = None):
        self.username = username
        self.role = role
        self.company_symbol = company_symbol
        self.session_token = None
    
    def create_session(self) -> str:
        """Create session token"""
        self.session_token = secrets.token_hex(32)
        return self.session_token
    
    def to_dict(self) -> Dict:
        return {
            'username': self.username,
            'role': self.role,
            'company_symbol': self.company_symbol
        }


class AuthManager:
    def __init__(self):
        self.user_storage = UserStorage()
        self.sessions: Dict[str, User] = {}
    
    def create_user(self, username: str, password: str, role: str, 
                    company_symbol: str = None) -> bool:
        """Create a new user"""
        return self.user_storage.create_user(username, password, role, company_symbol)
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Login user and create session"""
        user_data = self.user_storage.verify_user(username, password)
        
        if not user_data:
            return None
        
        # Create user object
        user = User(
            user_data['username'],
            user_data['role'],
            user_data.get('company_symbol')
        )
        
        # Create session
        token = user.create_session()
        self.sessions[token] = user
        
        return {
            'success': True,
            'token': token,
            'user': user.to_dict()
        }
    
    def logout(self, token: str):
        """Logout user"""
        if token in self.sessions:
            del self.sessions[token]
    
    def verify_session(self, token: str) -> Optional[User]:
        """Verify session token"""
        return self.sessions.get(token)
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.user_storage.get_user(username)
    
    @property
    def users(self):
        """Get all users"""
        return self.user_storage.get_all_users()