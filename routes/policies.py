"""
Policy management routes.
"""
from flask import Blueprint, request, jsonify
from services.policy_service import PolicyService
from utils.helpers import require_auth, require_role

policies_bp = Blueprint('policies', __name__, url_prefix='/api/policies')


@policies_bp.route('', methods=['POST'])
@require_auth
@require_role(['administrator', 'provider'])
def create_policy(current_user):
    """
    Create a new insurance policy (admin/provider only).
    
    Requires: Authorization header with Bearer token
    
    Request body:
        {
            "user_id": 1,
            "policy_type": "Individual Health",
            "coverage_amount": 50000.00,
            "premium_amount": 500.00,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "status": "active"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        policy = PolicyService.create_policy(data, current_user['id'])
        
        return jsonify({
            'message': 'Policy created successfully',
            'policy': policy
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create policy: {str(e)}'}), 500


@policies_bp.route('', methods=['GET'])
@require_auth
def get_policies(current_user):
    """
    Get policies (filtered by role).
    
    Patients see only their own policies.
    Providers/Admins see all policies.
    
    Requires: Authorization header with Bearer token
    """
    try:
        if current_user['role'] == 'patient':
            policies = PolicyService.get_policies_by_user(current_user['id'])
        else:
            policies = PolicyService.get_all_policies()
        
        return jsonify({
            'policies': policies,
            'count': len(policies)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch policies: {str(e)}'}), 500


@policies_bp.route('/<int:policy_id>', methods=['GET'])
@require_auth
def get_policy(policy_id, current_user):
    """
    Get policy by ID.
    
    Patients can only view their own policies.
    Providers/Admins can view any policy.
    
    Requires: Authorization header with Bearer token
    """
    try:
        policy = PolicyService.get_policy_by_id(policy_id)
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
        
        # Check permissions
        if current_user['role'] == 'patient' and policy['user_id'] != current_user['id']:
            return jsonify({'error': 'You can only view your own policies'}), 403
        
        return jsonify({
            'policy': policy
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch policy: {str(e)}'}), 500


@policies_bp.route('/<int:policy_id>', methods=['PUT'])
@require_auth
@require_role(['administrator', 'provider'])
def update_policy(policy_id, current_user):
    """
    Update policy details (admin/provider only).
    
    Requires: Authorization header with Bearer token
    
    Request body (all fields optional):
        {
            "policy_type": "Family Plan",
            "coverage_amount": 75000.00,
            "premium_amount": 750.00,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        policy = PolicyService.update_policy(policy_id, data)
        
        return jsonify({
            'message': 'Policy updated successfully',
            'policy': policy
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update policy: {str(e)}'}), 500


@policies_bp.route('/<int:policy_id>/status', methods=['PATCH'])
@require_auth
@require_role(['administrator'])
def update_policy_status(policy_id, current_user):
    """
    Update policy status (admin only).
    
    Requires: Authorization header with Bearer token (admin role)
    
    Request body:
        {
            "status": "inactive"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        policy = PolicyService.update_policy_status(policy_id, data['status'])
        
        return jsonify({
            'message': 'Policy status updated successfully',
            'policy': policy
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update policy status: {str(e)}'}), 500

