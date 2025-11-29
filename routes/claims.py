"""
Claims processing routes.
"""
from flask import Blueprint, request, jsonify
from services.claim_service import ClaimService
from utils.helpers import require_auth, require_role

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')


@claims_bp.route('', methods=['POST'])
@require_auth
def submit_claim(current_user):
    """
    Submit a new claim.
    
    Patients can only submit claims for their own policies.
    
    Requires: Authorization header with Bearer token
    
    Request body:
        {
            "policy_id": 1,
            "claim_amount": 5000.00,
            "diagnosis": "Fractured arm",
            "treatment_details": "X-ray and cast application",
            "provider_name": "City Hospital",
            "service_date": "2024-01-15"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        claim = ClaimService.create_claim(data, current_user['id'])
        
        return jsonify({
            'message': 'Claim submitted successfully',
            'claim': claim
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': f'Failed to submit claim: {str(e)}'}), 500


@claims_bp.route('', methods=['GET'])
@require_auth
def get_claims(current_user):
    """
    Get claims (filtered by role).
    
    Patients see only their own claims.
    Providers/Admins see all claims.
    
    Requires: Authorization header with Bearer token
    """
    try:
        if current_user['role'] == 'patient':
            claims = ClaimService.get_claims_by_user(current_user['id'])
        else:
            claims = ClaimService.get_all_claims()
        
        return jsonify({
            'claims': claims,
            'count': len(claims)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch claims: {str(e)}'}), 500


@claims_bp.route('/<int:claim_id>', methods=['GET'])
@require_auth
def get_claim(claim_id, current_user):
    """
    Get claim by ID.
    
    Patients can only view their own claims.
    Providers/Admins can view any claim.
    
    Requires: Authorization header with Bearer token
    """
    try:
        claim = ClaimService.get_claim_by_id(claim_id)
        
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404
        
        # Check permissions
        if current_user['role'] == 'patient' and claim['user_id'] != current_user['id']:
            return jsonify({'error': 'You can only view your own claims'}), 403
        
        return jsonify({
            'claim': claim
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch claim: {str(e)}'}), 500


@claims_bp.route('/<int:claim_id>/review', methods=['POST'])
@require_auth
@require_role(['administrator', 'provider'])
def review_claim(claim_id, current_user):
    """
    Review a claim (approve/deny with notes) - admin/provider only.
    
    Requires: Authorization header with Bearer token
    
    Request body:
        {
            "status": "approved",
            "approved_amount": 4500.00,
            "review_notes": "Claim approved with minor adjustment"
        }
        
    Or for denial:
        {
            "status": "denied",
            "review_notes": "Treatment not covered under policy"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        claim = ClaimService.review_claim(claim_id, data, current_user['id'])
        
        return jsonify({
            'message': 'Claim reviewed successfully',
            'claim': claim
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to review claim: {str(e)}'}), 500


@claims_bp.route('/<int:claim_id>/status', methods=['PATCH'])
@require_auth
@require_role(['administrator'])
def update_claim_status(claim_id, current_user):
    """
    Update claim status (admin only).
    
    Requires: Authorization header with Bearer token (admin role)
    
    Request body:
        {
            "status": "paid"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        claim = ClaimService.update_claim_status(claim_id, data['status'])
        
        return jsonify({
            'message': 'Claim status updated successfully',
            'claim': claim
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update claim status: {str(e)}'}), 500

