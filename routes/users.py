"""
User management routes.
"""
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.helpers import require_auth, require_role

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
@require_auth
@require_role(['administrator', 'provider'])
def get_all_users(current_user):
    """
    Get all users (admin/provider only).
    
    Requires: Authorization header with Bearer token
    """
    try:
        users = UserService.get_all_users()
        return jsonify({
            'users': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id, current_user):
    """
    Get user by ID.
    
    Patients can only view their own profile.
    Providers/Admins can view any profile.
    
    Requires: Authorization header with Bearer token
    """
    try:
        # Check permissions
        if current_user['role'] == 'patient' and current_user['id'] != user_id:
            return jsonify({'error': 'You can only view your own profile'}), 403
        
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch user: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id, current_user):
    """
    Update user details.
    
    Users can only update their own profile (except admins).
    
    Requires: Authorization header with Bearer token
    
    Request body (all fields optional):
        {
            "full_name": "Updated Name",
            "phone": "1234567890",
            "address": "New Address",
            "date_of_birth": "1990-01-01",
            "password": "newpassword123"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user = UserService.update_user(user_id, data, current_user)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user
        }), 200
    
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@require_auth
@require_role(['administrator'])
def deactivate_user(user_id, current_user):
    """
    Deactivate a user (admin only).
    
    Requires: Authorization header with Bearer token (admin role)
    """
    try:
        user = UserService.toggle_user_active(user_id, False)
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user': user
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to deactivate user: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@require_auth
@require_role(['administrator'])
def activate_user(user_id, current_user):
    """
    Activate a user (admin only).
    
    Requires: Authorization header with Bearer token (admin role)
    """
    try:
        user = UserService.toggle_user_active(user_id, True)
        
        return jsonify({
            'message': 'User activated successfully',
            'user': user
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to activate user: {str(e)}'}), 500

