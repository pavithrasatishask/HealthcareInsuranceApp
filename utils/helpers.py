"""
Utility decorators for authentication and authorization.
"""
from functools import wraps
from flask import request, jsonify
import jwt
from config import Config
from services.supabase_client import SupabaseClient


def require_auth(f):
    """
    Decorator to require JWT authentication.
    
    Extracts and validates JWT token from Authorization header.
    Adds 'current_user' to the decorated function's kwargs.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        try:
            # Decode and verify token
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            user_id = payload.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'Invalid token payload'}), 401
            
            # Fetch user from database
            supabase = SupabaseClient.get_client()
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            
            if not response.data or len(response.data) == 0:
                return jsonify({'error': 'User not found'}), 401
            
            user = response.data[0]
            
            # Check if user is active
            if not user.get('is_active', True):
                return jsonify({'error': 'User account is deactivated'}), 403
            
            # Add current_user to kwargs
            kwargs['current_user'] = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication error: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(allowed_roles):
    """
    Decorator to require specific user roles.
    
    Args:
        allowed_roles: List of allowed roles (e.g., ['administrator', 'provider'])
    
    Must be used after @require_auth decorator.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current_user from kwargs (set by @require_auth)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': allowed_roles,
                    'user_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

