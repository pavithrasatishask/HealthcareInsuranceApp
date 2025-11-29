"""
Claim service for business logic related to insurance claims.
"""
import random
from datetime import datetime
from services.supabase_client import SupabaseClient
from services.policy_service import PolicyService


class ClaimService:
    """Service for claim-related business logic."""
    
    @staticmethod
    def generate_claim_number() -> str:
        """
        Generate a unique claim number (CLM + 10 digits).
        
        Returns:
            str: Claim number
        """
        digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        return f"CLM{digits}"
    
    @staticmethod
    def validate_claim_data(claim_data: dict) -> tuple[bool, str]:
        """
        Validate claim data.
        
        Args:
            claim_data: Dictionary containing claim data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['policy_id', 'claim_amount', 'diagnosis', 'treatment_details', 'provider_name', 'service_date']
        for field in required_fields:
            if field not in claim_data:
                return False, f"{field} is required"
        
        # Validate claim amount is positive
        if float(claim_data['claim_amount']) <= 0:
            return False, "Claim amount must be positive"
        
        # Validate service date
        try:
            service_date = datetime.strptime(claim_data['service_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            if service_date > today:
                return False, "Service date cannot be in the future"
        except ValueError:
            return False, "Invalid service date format. Use YYYY-MM-DD"
        
        return True, ""
    
    @staticmethod
    def create_claim(claim_data: dict, user_id: int) -> dict:
        """
        Create a new claim.
        
        Args:
            claim_data: Dictionary containing claim data
            user_id: ID of user submitting the claim
            
        Returns:
            dict: Created claim data
        """
        supabase = SupabaseClient.get_client()
        
        # Validate claim data
        is_valid, error_msg = ClaimService.validate_claim_data(claim_data)
        if not is_valid:
            raise ValueError(error_msg)
        
        policy_id = claim_data['policy_id']
        
        # Check if policy exists and belongs to user
        policy = PolicyService.get_policy_by_id(policy_id)
        if not policy:
            raise ValueError("Policy not found")
        
        if policy['user_id'] != user_id:
            raise PermissionError("You can only submit claims for your own policies")
        
        # Check if policy is active
        if not PolicyService.is_policy_active(policy_id):
            raise ValueError("Cannot submit claim for inactive policy")
        
        # Generate unique claim number
        claim_number = ClaimService.generate_claim_number()
        
        # Check for uniqueness (retry if needed)
        max_retries = 10
        for _ in range(max_retries):
            existing = supabase.table('claims').select('id').eq('claim_number', claim_number).execute()
            if not existing.data or len(existing.data) == 0:
                break
            claim_number = ClaimService.generate_claim_number()
        else:
            raise Exception("Failed to generate unique claim number")
        
        # Prepare claim data for insertion
        insert_data = {
            'claim_number': claim_number,
            'policy_id': policy_id,
            'user_id': user_id,
            'claim_amount': float(claim_data['claim_amount']),
            'approved_amount': 0.00,
            'status': 'submitted',
            'diagnosis': claim_data['diagnosis'],
            'treatment_details': claim_data['treatment_details'],
            'provider_name': claim_data['provider_name'],
            'service_date': claim_data['service_date']
        }
        
        # Insert claim
        response = supabase.table('claims').insert(insert_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("Failed to create claim")
        
        return response.data[0]
    
    @staticmethod
    def get_claim_by_id(claim_id: int) -> dict:
        """
        Get claim by ID.
        
        Args:
            claim_id: Claim ID
            
        Returns:
            dict: Claim data or None
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('claims').select('*').eq('id', claim_id).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]
    
    @staticmethod
    def get_claims_by_user(user_id: int) -> list:
        """
        Get all claims for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of claims
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('claims').select('*').eq('user_id', user_id).execute()
        
        return response.data
    
    @staticmethod
    def get_all_claims() -> list:
        """
        Get all claims.
        
        Returns:
            list: List of all claims
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('claims').select('*').execute()
        
        return response.data
    
    @staticmethod
    def review_claim(claim_id: int, review_data: dict, reviewer_id: int) -> dict:
        """
        Review a claim (approve/deny with notes).
        
        Args:
            claim_id: Claim ID
            review_data: Dictionary containing review decision and notes
            reviewer_id: ID of user reviewing the claim
            
        Returns:
            dict: Updated claim data
        """
        supabase = SupabaseClient.get_client()
        
        # Get current claim
        claim = ClaimService.get_claim_by_id(claim_id)
        if not claim:
            raise ValueError("Claim not found")
        
        # Validate review data
        if 'status' not in review_data:
            raise ValueError("Status is required for review")
        
        valid_statuses = ['under_review', 'approved', 'denied']
        if review_data['status'] not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # If approved, validate approved_amount
        if review_data['status'] == 'approved':
            if 'approved_amount' not in review_data:
                raise ValueError("Approved amount is required when approving a claim")
            
            approved_amount = float(review_data['approved_amount'])
            claim_amount = float(claim['claim_amount'])
            
            if approved_amount < 0:
                raise ValueError("Approved amount cannot be negative")
            
            if approved_amount > claim_amount:
                raise ValueError("Approved amount cannot exceed claim amount")
        else:
            # For denied or under_review, set approved_amount to 0
            review_data['approved_amount'] = 0.00
        
        # Prepare update data
        update_data = {
            'status': review_data['status'],
            'approved_amount': float(review_data.get('approved_amount', 0)),
            'reviewed_by': reviewer_id,
            'reviewed_at': datetime.utcnow().isoformat(),
            'review_notes': review_data.get('review_notes', '')
        }
        
        # Update claim
        response = supabase.table('claims').update(update_data).eq('id', claim_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("Failed to update claim")
        
        return response.data[0]
    
    @staticmethod
    def update_claim_status(claim_id: int, status: str) -> dict:
        """
        Update claim status (admin only).
        
        Args:
            claim_id: Claim ID
            status: New status
            
        Returns:
            dict: Updated claim data
        """
        valid_statuses = ['submitted', 'under_review', 'approved', 'denied', 'paid']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        supabase = SupabaseClient.get_client()
        response = supabase.table('claims').update({'status': status}).eq('id', claim_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("Claim not found")
        
        return response.data[0]

