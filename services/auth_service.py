"""
Authentication service for password hashing and JWT token generation.
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from config import Config


class AuthService:
    """Service for authentication-related operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_token(user_id: int, email: str, role: str) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_id: User ID
            email: User email
            role: User role
            
        Returns:
            str: JWT token
        """
        expiration = datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
        return token

