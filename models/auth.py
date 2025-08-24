import json
import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class User:
    """User model for authentication."""
    
    def __init__(self, user_id: str, username: str, email: str, user_type: str, 
                 created_at: str, last_login: str, is_active: bool = True):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.user_type = user_type
        self.created_at = created_at
        self.last_login = last_login
        self.is_active = is_active
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "user_type": self.user_type,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            username=data.get("username", ""),
            email=data.get("email", ""),
            user_type=data.get("user_type", "user"),
            created_at=data.get("created_at", ""),
            last_login=data.get("last_login", ""),
            is_active=data.get("is_active", True)
        )


class AuthManager:
    """Manages user authentication using JSON files."""
    
    def __init__(self, users_file: Path):
        self.users_file = users_file
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize users file if it doesn't exist
        if not self.users_file.exists():
            self._create_default_users()
    
    def _create_default_users(self):
        """Create default users if file doesn't exist."""
        default_users = [
            {
                "user_id": "user_20250823_000000_0001",
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": "admin123",
                "user_type": "admin",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "is_active": True
            },
            {
                "user_id": "user_20250823_000000_0002",
                "username": "sairam",
                "email": "sairampanchak@gmail.com",
                "password_hash": "sairam123",
                "user_type": "user",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "is_active": True
            }
        ]
        
        with open(self.users_file, 'w') as f:
            json.dump(default_users, f, indent=2)
    
    def _load_users(self) -> list:
        """Load users from JSON file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_users(self, users: list):
        """Save users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        users = self._load_users()
        
        for user_data in users:
            if (user_data["email"] == email and 
                user_data["password_hash"] == password and 
                user_data["is_active"]):
                
                # Update last login
                user_data["last_login"] = datetime.now().isoformat()
                self._save_users(users)
                
                return User.from_dict(user_data)
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        users = self._load_users()
        
        for user_data in users:
            if user_data["email"] == email and user_data["is_active"]:
                return User.from_dict(user_data)
        
        return None
    
    def create_user(self, username: str, email: str, password: str, user_type: str = "user") -> Optional[User]:
        """Create a new user."""
        users = self._load_users()
        
        # Check if email already exists
        for user_data in users:
            if user_data["email"] == email:
                return None
        
        # Create new user
        new_user = {
            "user_id": f"user_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "username": username,
            "email": email,
            "password_hash": password,  # In production, hash this properly
            "user_type": user_type,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "is_active": True
        }
        
        users.append(new_user)
        self._save_users(users)
        
        return User.from_dict(new_user)
    
    def update_user_last_login(self, email: str):
        """Update user's last login time."""
        users = self._load_users()
        
        for user_data in users:
            if user_data["email"] == email:
                user_data["last_login"] = datetime.now().isoformat()
                break
        
        self._save_users(users)
