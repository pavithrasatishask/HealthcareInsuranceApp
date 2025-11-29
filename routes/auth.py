"""
Authentication routes for user registration and login.
"""
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from services.auth_service import AuthService
from utils.helpers import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
        {
            "email": "user@example.com",
            "password": "password123",
            "full_name": "John Doe",
            "role": "patient",
            "phone": "1234567890",
            "address": "123 Main St",
            "date_of_birth": "1990-01-01"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create user
        user = UserService.create_user(data)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        error_str = str(e)
        # Check if it's a unique constraint violation
        if 'duplicate' in error_str.lower() or 'unique' in error_str.lower():
            return jsonify({'error': 'Email already exists'}), 400
        # Check for Supabase API key errors
        if 'api key' in error_str.lower() or 'invalid' in error_str.lower():
            return jsonify({
                'error': f'Registration failed: {error_str}',
                'hint': 'Please verify your SUPABASE_URL and SUPABASE_KEY in .env file are correct and restart the Flask app.'
            }), 500
        return jsonify({'error': f'Registration failed: {error_str}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login and get JWT token.
    
    Request body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Get user by email
        user = UserService.get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'User account is deactivated'}), 403
        
        # Verify password
        if not AuthService.verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = AuthService.generate_token(
            user_id=user['id'],
            email=user['email'],
            role=user['role']
        )
        
        # Remove password_hash from response
        user.pop('password_hash', None)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user(current_user):
    """
    Get current authenticated user details.
    
    Requires: Authorization header with Bearer token
    """
    return jsonify({
        'user': current_user
    }), 200

