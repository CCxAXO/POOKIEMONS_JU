from typing import Dict, Optional
import hashlib
import secrets

class User:
    def __init__(self, username: str, password: str, role: str, company_symbol: str = None):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.role = role  # 'admin', 'company_owner', 'trader'
        self.company_symbol = company_symbol
        self.session_token = None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return self._hash_password(password) == self.password_hash
    
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
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, User] = {}
        
        # Create default admin account
        self.create_user('admin', 'admin123', 'admin')
        print("✓ Default admin created (username: admin, password: admin123)")
    
    def create_user(self, username: str, password: str, role: str, 
                    company_symbol: str = None) -> User:
        """Create a new user"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        user = User(username, password, role, company_symbol)
        self.users[username] = user
        return user
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Login user and create session"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if not user.verify_password(password):
            return None
        
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
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username) 