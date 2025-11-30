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
            "payer_program": "medicare",
            "payer_name": "Centers for Medicare & Medicaid Services",
            "payer_id": "CMS001",
            "policy_type": "Medicare Advantage",
            "plan_name": "Medicare Part C - Silver Plan",
            "coverage_amount": 50000.00,
            "premium_amount": 500.00,
            "deductible_amount": 1500.00,
            "out_of_pocket_max": 7500.00,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "medicare_part": "Part C",
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
    Providers/Admins see all policies or can filter by payer_program.
    
    Query parameters:
        - payer_program: Filter by payer program (medicare, medicaid, commercial, other_government)
        - user_id: Filter by user ID (admin/provider only)
    
    Requires: Authorization header with Bearer token
    """
    try:
        if current_user['role'] == 'patient':
            policies = PolicyService.get_policies_by_user(current_user['id'])
        else:
            # Admin/Provider can filter by payer_program or user_id
            payer_program = request.args.get('payer_program')
            user_id = request.args.get('user_id', type=int)
            
            if user_id:
                policies = PolicyService.get_policies_by_user(user_id)
            elif payer_program:
                # Validate payer_program
                valid_programs = ['medicare', 'medicaid', 'commercial', 'other_government']
                if payer_program not in valid_programs:
                    return jsonify({
                        'error': f'Invalid payer_program. Must be one of: {", ".join(valid_programs)}'
                    }), 400
                policies = PolicyService.get_policies_by_payer_program(payer_program)
            else:
                policies = PolicyService.get_all_policies()
        
        return jsonify({
            'policies': policies,
            'count': len(policies)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch policies: {str(e)}'}), 500


@policies_bp.route('/programs', methods=['GET'])
@require_auth
@require_role(['administrator', 'provider'])
def get_payer_program_stats(current_user):
    """
    Get statistics by payer program (admin/provider only).
    
    Returns aggregated statistics for Medicare, Medicaid, Commercial, and Other programs.
    
    Requires: Authorization header with Bearer token (admin/provider role)
    """
    try:
        stats = PolicyService.get_payer_program_stats()
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch statistics: {str(e)}'}), 500


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
            "payer_program": "medicare",
            "payer_name": "Updated Payer Name",
            "policy_type": "Family Plan",
            "plan_name": "Updated Plan Name",
            "coverage_amount": 75000.00,
            "premium_amount": 750.00,
            "deductible_amount": 2000.00,
            "out_of_pocket_max": 8000.00,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "medicare_part": "Part B",
            "medicaid_state": "CA"
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
    
    Valid statuses: active, inactive, suspended, cancelled
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