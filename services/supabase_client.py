"""
Singleton Supabase client for database operations.
"""
from supabase import create_client, Client
from config import Config


class SupabaseClient:
    """Singleton class for Supabase client."""
    
    _instance: Client = None
    _initialized = False
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create the Supabase client instance.
        
        Returns:
            Client: Supabase client instance
        """
        if cls._instance is None:
            Config.validate()
            cls._instance = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            cls._initialized = True
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        cls._initialized = False

