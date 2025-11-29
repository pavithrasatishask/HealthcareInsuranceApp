"""
Policy service for business logic related to insurance policies.
"""
import random
from datetime import datetime
from services.supabase_client import SupabaseClient


class PolicyService:
    """Service for policy-related business logic."""
    
    @staticmethod
    def generate_policy_number() -> str:
        """
        Generate a unique policy number (POL + 10 digits).
        
        Returns:
            str: Policy number
        """
        digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        return f"POL{digits}"
    
    @staticmethod
    def validate_policy_data(policy_data: dict) -> tuple[bool, str]:
        """
        Validate policy data.
        
        Args:
            policy_data: Dictionary containing policy data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['user_id', 'policy_type', 'coverage_amount', 'premium_amount', 'start_date', 'end_date']
        for field in required_fields:
            if field not in policy_data:
                return False, f"{field} is required"
        
        # Validate amounts are positive
        if float(policy_data['coverage_amount']) <= 0:
            return False, "Coverage amount must be positive"
        
        if float(policy_data['premium_amount']) <= 0:
            return False, "Premium amount must be positive"
        
        # Validate date range
        start_date = datetime.strptime(policy_data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(policy_data['end_date'], '%Y-%m-%d').date()
        
        if end_date <= start_date:
            return False, "End date must be after start date"
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'suspended', 'cancelled']
        if 'status' in policy_data and policy_data['status'] not in valid_statuses:
            return False, f"Status must be one of: {', '.join(valid_statuses)}"
        
        return True, ""
    
    @staticmethod
    def create_policy(policy_data: dict, created_by: int) -> dict:
        """
        Create a new insurance policy.
        
        Args:
            policy_data: Dictionary containing policy data
            created_by: ID of user creating the policy
            
        Returns:
            dict: Created policy data
        """
        supabase = SupabaseClient.get_client()
        
        # Validate policy data
        is_valid, error_msg = PolicyService.validate_policy_data(policy_data)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check if user exists
        user_response = supabase.table('users').select('id').eq('id', policy_data['user_id']).execute()
        if not user_response.data or len(user_response.data) == 0:
            raise ValueError("User not found")
        
        # Generate unique policy number
        policy_number = PolicyService.generate_policy_number()
        
        # Check for uniqueness (retry if needed)
        max_retries = 10
        for _ in range(max_retries):
            existing = supabase.table('policies').select('id').eq('policy_number', policy_number).execute()
            if not existing.data or len(existing.data) == 0:
                break
            policy_number = PolicyService.generate_policy_number()
        else:
            raise Exception("Failed to generate unique policy number")
        
        # Prepare policy data for insertion
        insert_data = {
            'policy_number': policy_number,
            'user_id': policy_data['user_id'],
            'policy_type': policy_data['policy_type'],
            'coverage_amount': float(policy_data['coverage_amount']),
            'premium_amount': float(policy_data['premium_amount']),
            'status': policy_data.get('status', 'active'),
            'start_date': policy_data['start_date'],
            'end_date': policy_data['end_date'],
            'created_by': created_by
        }
        
        # Insert policy
        response = supabase.table('policies').insert(insert_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("Failed to create policy")
        
        return response.data[0]
    
    @staticmethod
    def get_policy_by_id(policy_id: int) -> dict:
        """
        Get policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            dict: Policy data or None
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('policies').select('*').eq('id', policy_id).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]
    
    @staticmethod
    def get_policies_by_user(user_id: int) -> list:
        """
        Get all policies for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of policies
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('policies').select('*').eq('user_id', user_id).execute()
        
        return response.data
    
    @staticmethod
    def get_all_policies() -> list:
        """
        Get all policies.
        
        Returns:
            list: List of all policies
        """
        supabase = SupabaseClient.get_client()
        response = supabase.table('policies').select('*').execute()
        
        return response.data
    
    @staticmethod
    def update_policy(policy_id: int, update_data: dict) -> dict:
        """
        Update policy details.
        
        Args:
            policy_id: Policy ID
            update_data: Dictionary containing fields to update
            
        Returns:
            dict: Updated policy data
        """
        supabase = SupabaseClient.get_client()
        
        # Remove fields that shouldn't be updated
        update_data.pop('id', None)
        update_data.pop('policy_number', None)
        update_data.pop('created_at', None)
        update_data.pop('created_by', None)
        
        # Validate amounts if provided
        if 'coverage_amount' in update_data:
            if float(update_data['coverage_amount']) <= 0:
                raise ValueError("Coverage amount must be positive")
        
        if 'premium_amount' in update_data:
            if float(update_data['premium_amount']) <= 0:
                raise ValueError("Premium amount must be positive")
        
        # Validate date range if dates are being updated
        if 'start_date' in update_data or 'end_date' in update_data:
            # Get current policy to compare dates
            current_policy = PolicyService.get_policy_by_id(policy_id)
            if not current_policy:
                raise ValueError("Policy not found")
            
            start_date_str = update_data.get('start_date', current_policy['start_date'])
            end_date_str = update_data.get('end_date', current_policy['end_date'])
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if end_date <= start_date:
                raise ValueError("End date must be after start date")
        
        # Validate status if provided
        if 'status' in update_data:
            valid_statuses = ['active', 'inactive', 'suspended', 'cancelled']
            if update_data['status'] not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Update policy
        response = supabase.table('policies').update(update_data).eq('id', policy_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise Exception("Policy not found or update failed")
        
        return response.data[0]
    
    @staticmethod
    def update_policy_status(policy_id: int, status: str) -> dict:
        """
        Update policy status.
        
        Args:
            policy_id: Policy ID
            status: New status
            
        Returns:
            dict: Updated policy data
        """
        valid_statuses = ['active', 'inactive', 'suspended', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return PolicyService.update_policy(policy_id, {'status': status})
    
    @staticmethod
    def is_policy_active(policy_id: int) -> bool:
        """
        Check if a policy is active.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            bool: True if policy is active, False otherwise
        """
        policy = PolicyService.get_policy_by_id(policy_id)
        if not policy:
            return False
        
        # Check status
        if policy['status'] != 'active':
            return False
        
        # Check date range
        today = datetime.now().date()
        start_date = datetime.strptime(policy['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(policy['end_date'], '%Y-%m-%d').date()
        
        return start_date <= today <= end_date

