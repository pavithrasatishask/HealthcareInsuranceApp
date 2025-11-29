"""
User service for business logic related to user management.
"""
from services.supabase_client import SupabaseClient
from services.auth_service import AuthService


class UserService:
    """Service for user-related business logic."""
    
    @staticmethod
    def validate_role(role: str) -> bool:
        """
        Validate that a role is one of the allowed roles.
        
        Args:
            role: Role to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        allowed_roles = ['patient', 'provider', 'administrator']
        return role in allowed_roles
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password meets requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        return True, ""
    
    @staticmethod
    def create_user(user_data: dict) -> dict:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            dict: Created user data (without password_hash)
        """
        supabase = SupabaseClient.get_client()
        
        # Validate role
        role = user_data.get('role', 'patient')
        if not UserService.validate_role(role):
            raise ValueError("Invalid role. Must be one of: patient, provider, administrator")
        
        # Validate password
        password = user_data.get('password')
        if not password:
            raise ValueError("Password is required")
        
        is_valid, error_msg = UserService.validate_password(password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Prepare user data for insertion
        insert_data = {
            'email': user_data['email'],
            'password_hash': password_hash,
            'full_name': user_data['full_name'],
            'role': role,
            'phone': user_data.get('phone'),
            'address': user_data.get('address'),
            'date_of_birth': user_data.get('date_of_birth'),
            'is_active': user_data.get('is_active', True)
        }
        
        # Insert user
        try:
            response = supabase.table('users').insert(insert_data).execute()
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            # Get more details from the exception if available
            error_details = ""
            if hasattr(e, 'message'):
                error_details = f" Message: {e.message}"
            if hasattr(e, 'code'):
                error_details += f" Code: {e.code}"
            if hasattr(e, 'hint'):
                error_details += f" Hint: {e.hint}"
            
            # Check for common Supabase errors - be more specific
            error_lower = error_msg.lower()
            if any(term in error_lower for term in ['invalid api key', 'api key', 'apikey', '401', 'unauthorized', 'forbidden']):
                # Try to get the actual Supabase error response
                actual_error = error_msg
                if hasattr(e, 'args') and len(e.args) > 0:
                    actual_error = str(e.args[0])
                raise ValueError(f"Supabase API key error: {actual_error}. Please verify:\n1. SUPABASE_URL format: https://xxx.supabase.co\n2. SUPABASE_KEY is the full key (starts with 'eyJ')\n3. No quotes or extra spaces in .env\n4. Restart Flask after .env changes")
            elif 'JWT' in error_msg or 'token' in error_lower:
                raise ValueError("Supabase authentication error. Please check your SUPABASE_KEY in .env file.")
            elif 'relation' in error_lower or 'does not exist' in error_lower or 'table' in error_lower:
                raise ValueError("Database table 'users' does not exist. Please run database_schema.sql in Supabase SQL Editor.")
            else:
                # Include full error details for debugging - this will help us see the actual error
                full_error = f"Supabase error ({error_type}): {error_msg}"
                if error_details:
                    full_error += error_details
                raise Exception(full_error)
        
        if not response.data or len(response.data) == 0:
            raise Exception("Failed to create user")
        
        user = response.data[0]
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        return user
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User data (without password_hash)
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        user = response.data[0]
        user.pop('password_hash', None)
        return user
    
    @staticmethod
    def get_user_by_email(email: str) -> dict:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            dict: User data (including password_hash for auth)
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]
    
    @staticmethod
    def get_all_users() -> list:
        """
        Get all users.
        
        Returns:
            list: List of user data (without password_hash)
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('users').select('*').execute()
        
        users = response.data
        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)
        
        return users
    
    @staticmethod
    def update_user(user_id: int, update_data: dict, current_user: dict) -> dict:
        """
        Update user details.
        
        Args:
            user_id: User ID to update
            update_data: Dictionary containing fields to update
            current_user: Current authenticated user
            
        Returns:
            dict: Updated user data (without password_hash)
        """
        supabase = SupabaseClient.get_client()
        
        # Check permissions: users can only update their own profile unless they're admin
        if current_user['role'] != 'administrator' and current_user['id'] != user_id:
            raise PermissionError("You can only update your own profile")
        
        # Remove fields that shouldn't be updated directly
        update_data.pop('id', None)
        update_data.pop('created_at', None)
        
        # If password is being updated, hash it
        if 'password' in update_data:
            password = update_data.pop('password')
            is_valid, error_msg = UserService.validate_password(password)
            if not is_valid:
                raise ValueError(error_msg)
            update_data['password_hash'] = AuthService.hash_password(password)
        
        # If role is being updated, only admins can do this
        if 'role' in update_data:
            if current_user['role'] != 'administrator':
                raise PermissionError("Only administrators can change user roles")
            if not UserService.validate_role(update_data['role']):
                raise ValueError("Invalid role")
        
        # Update user
        response = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("User not found or update failed")
        
        user = response.data[0]
        user.pop('password_hash', None)
        
        return user
    
    @staticmethod
    def toggle_user_active(user_id: int, is_active: bool) -> dict:
        """
        Activate or deactivate a user.
        
        Args:
            user_id: User ID
            is_active: True to activate, False to deactivate
            
        Returns:
            dict: Updated user data
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('users').update({'is_active': is_active}).eq('id', user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("User not found")
        
        user = response.data[0]
        user.pop('password_hash', None)
        
        return user

