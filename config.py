"""
Configuration settings for the Healthcare Insurance API.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Supabase settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Password hashing
    BCRYPT_ROUNDS = 12
    
    @staticmethod
    def validate():
        """Validate that required environment variables are set."""
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'JWT_SECRET_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

