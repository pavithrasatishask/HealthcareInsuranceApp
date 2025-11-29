# Healthcare Insurance API - Complete API Reference

Base URL: `http://localhost:5000`

All endpoints return JSON responses. Most endpoints require JWT authentication via the `Authorization` header: `Bearer <token>`

---

## Table of Contents

1. [Health Check](#health-check)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management Endpoints](#user-management-endpoints)
4. [Policy Management Endpoints](#policy-management-endpoints)
5. [Claims Processing Endpoints](#claims-processing-endpoints)

---

## Health Check

### GET `/`
**Functionality**: Health check endpoint to verify API is running

**Authentication**: None required

**URL**: `http://localhost:5000/`

**Example Request**:
```bash
curl -X GET http://localhost:5000/
```

**Example Response**:
```json
{
  "message": "Healthcare Insurance API is running",
  "version": "1.0.0",
  "status": "healthy"
}
```

---

## Authentication Endpoints

### 1. Register User

**POST** `/api/auth/register`

**Functionality**: Register a new user account with email and password

**Authentication**: None required

**URL**: `http://localhost:5000/api/auth/register`

**Request Body**:
```json
{
  "email": "patient@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "patient",
  "phone": "1234567890",
  "address": "123 Main St",
  "date_of_birth": "1990-01-01"
}
```

**Required Fields**: `email`, `password`, `full_name`, `role`

**Valid Roles**: `patient`, `provider`, `administrator`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "role": "patient",
    "phone": "1234567890",
    "address": "123 Main St",
    "date_of_birth": "1990-01-01"
  }'
```

**Success Response** (201):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "phone": "1234567890",
    "address": "123 Main St",
    "date_of_birth": "1990-01-01",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `400`: Missing required fields, invalid role, password too short, or email already exists
- `500`: Server error

---

### 2. Login

**POST** `/api/auth/login`

**Functionality**: Authenticate user and receive JWT token

**Authentication**: None required

**URL**: `http://localhost:5000/api/auth/login`

**Request Body**:
```json
{
  "email": "patient@example.com",
  "password": "password123"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123"
  }'
```

**Success Response** (200):
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "full_name": "John Doe",
    "role": "patient"
  }
}
```

**Error Responses**:
- `400`: Missing email or password
- `401`: Invalid email or password
- `403`: User account is deactivated
- `500`: Server error

**Note**: Save the `token` from this response to use in subsequent authenticated requests.

---

### 3. Get Current User

**GET** `/api/auth/me`

**Functionality**: Get details of the currently authenticated user

**Authentication**: Required (Bearer token)

**URL**: `http://localhost:5000/api/auth/me`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "phone": "1234567890",
    "address": "123 Main St",
    "date_of_birth": "1990-01-01",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: User account is deactivated

---

## User Management Endpoints

### 4. Get All Users

**GET** `/api/users`

**Functionality**: Retrieve all users in the system

**Authentication**: Required (Bearer token)

**Access**: Administrator or Provider only

**URL**: `http://localhost:5000/api/users`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "users": [
    {
      "id": 1,
      "email": "patient@example.com",
      "full_name": "John Doe",
      "role": "patient",
      "is_active": true
    },
    {
      "id": 2,
      "email": "provider@example.com",
      "full_name": "Dr. Smith",
      "role": "provider",
      "is_active": true
    }
  ],
  "count": 2
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient role cannot access)
- `500`: Server error

---

### 5. Get User by ID

**GET** `/api/users/<user_id>`

**Functionality**: Retrieve a specific user by their ID

**Authentication**: Required (Bearer token)

**Access**: 
- Patients can only view their own profile
- Providers/Admins can view any profile

**URL**: `http://localhost:5000/api/users/1`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "phone": "1234567890",
    "address": "123 Main St",
    "date_of_birth": "1990-01-01",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient trying to view another user's profile)
- `404`: User not found
- `500`: Server error

---

### 6. Update User

**PUT** `/api/users/<user_id>`

**Functionality**: Update user profile information

**Authentication**: Required (Bearer token)

**Access**: 
- Users can only update their own profile
- Administrators can update any profile

**URL**: `http://localhost:5000/api/users/1`

**Request Body** (all fields optional):
```json
{
  "full_name": "John Updated",
  "phone": "9876543210",
  "address": "456 New St",
  "date_of_birth": "1990-01-01",
  "password": "newpassword123"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated",
    "phone": "9876543210"
  }'
```

**Success Response** (200):
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "full_name": "John Updated",
    "phone": "9876543210",
    "role": "patient",
    "is_active": true,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Error Responses**:
- `400`: Invalid data or password too short
- `401`: Missing or invalid token
- `403`: Insufficient permissions (trying to update another user's profile)
- `500`: Server error

**Note**: Only administrators can change user roles.

---

### 7. Deactivate User

**POST** `/api/users/<user_id>/deactivate`

**Functionality**: Deactivate a user account (prevents login)

**Authentication**: Required (Bearer token)

**Access**: Administrator only

**URL**: `http://localhost:5000/api/users/1/deactivate`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/users/1/deactivate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "message": "User deactivated successfully",
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "is_active": false
  }
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: Insufficient permissions (not administrator)
- `500`: Server error

---

### 8. Activate User

**POST** `/api/users/<user_id>/activate`

**Functionality**: Activate a previously deactivated user account

**Authentication**: Required (Bearer token)

**Access**: Administrator only

**URL**: `http://localhost:5000/api/users/1/activate`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/users/1/activate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "message": "User activated successfully",
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "is_active": true
  }
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: Insufficient permissions (not administrator)
- `500`: Server error

---

## Policy Management Endpoints

### 9. Create Policy

**POST** `/api/policies`

**Functionality**: Create a new insurance policy

**Authentication**: Required (Bearer token)

**Access**: Administrator or Provider only

**URL**: `http://localhost:5000/api/policies`

**Request Body**:
```json
{
  "user_id": 1,
  "policy_type": "Individual Health",
  "coverage_amount": 50000.00,
  "premium_amount": 500.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "status": "active"
}
```

**Required Fields**: `user_id`, `policy_type`, `coverage_amount`, `premium_amount`, `start_date`, `end_date`

**Valid Statuses**: `active`, `inactive`, `suspended`, `cancelled`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/policies \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "policy_type": "Individual Health",
    "coverage_amount": 50000.00,
    "premium_amount": 500.00,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "status": "active"
  }'
```

**Success Response** (201):
```json
{
  "message": "Policy created successfully",
  "policy": {
    "id": 1,
    "policy_number": "POL1234567890",
    "user_id": 1,
    "policy_type": "Individual Health",
    "coverage_amount": 50000.00,
    "premium_amount": 500.00,
    "status": "active",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "created_by": 2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `400`: Missing required fields, invalid amounts, or invalid date range
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient role cannot create policies)
- `500`: Server error

**Note**: Policy number is auto-generated (POL + 10 digits).

---

### 10. Get All Policies

**GET** `/api/policies`

**Functionality**: Retrieve policies (filtered by user role)

**Authentication**: Required (Bearer token)

**Access**: 
- Patients see only their own policies
- Providers/Admins see all policies

**URL**: `http://localhost:5000/api/policies`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/policies \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "policies": [
    {
      "id": 1,
      "policy_number": "POL1234567890",
      "user_id": 1,
      "policy_type": "Individual Health",
      "coverage_amount": 50000.00,
      "premium_amount": 500.00,
      "status": "active",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    }
  ],
  "count": 1
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `500`: Server error

---

### 11. Get Policy by ID

**GET** `/api/policies/<policy_id>`

**Functionality**: Retrieve a specific policy by ID

**Authentication**: Required (Bearer token)

**Access**: 
- Patients can only view their own policies
- Providers/Admins can view any policy

**URL**: `http://localhost:5000/api/policies/1`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/policies/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "policy": {
    "id": 1,
    "policy_number": "POL1234567890",
    "user_id": 1,
    "policy_type": "Individual Health",
    "coverage_amount": 50000.00,
    "premium_amount": 500.00,
    "status": "active",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "created_by": 2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient trying to view another user's policy)
- `404`: Policy not found
- `500`: Server error

---

### 12. Update Policy

**PUT** `/api/policies/<policy_id>`

**Functionality**: Update policy details

**Authentication**: Required (Bearer token)

**Access**: Administrator or Provider only

**URL**: `http://localhost:5000/api/policies/1`

**Request Body** (all fields optional):
```json
{
  "policy_type": "Family Plan",
  "coverage_amount": 75000.00,
  "premium_amount": 750.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:5000/api/policies/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coverage_amount": 75000.00,
    "premium_amount": 750.00
  }'
```

**Success Response** (200):
```json
{
  "message": "Policy updated successfully",
  "policy": {
    "id": 1,
    "policy_number": "POL1234567890",
    "coverage_amount": 75000.00,
    "premium_amount": 750.00,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Error Responses**:
- `400`: Invalid data, amounts, or date range
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient role cannot update policies)
- `500`: Server error

---

### 13. Update Policy Status

**PATCH** `/api/policies/<policy_id>/status`

**Functionality**: Update policy status (active/inactive/suspended/cancelled)

**Authentication**: Required (Bearer token)

**Access**: Administrator only

**URL**: `http://localhost:5000/api/policies/1/status`

**Request Body**:
```json
{
  "status": "inactive"
}
```

**Valid Statuses**: `active`, `inactive`, `suspended`, `cancelled`

**Example Request**:
```bash
curl -X PATCH http://localhost:5000/api/policies/1/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive"
  }'
```

**Success Response** (200):
```json
{
  "message": "Policy status updated successfully",
  "policy": {
    "id": 1,
    "status": "inactive",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Error Responses**:
- `400`: Invalid status value
- `401`: Missing or invalid token
- `403`: Insufficient permissions (not administrator)
- `500`: Server error

---

## Claims Processing Endpoints

### 14. Submit Claim

**POST** `/api/claims`

**Functionality**: Submit a new insurance claim

**Authentication**: Required (Bearer token)

**Access**: All authenticated users (patients can only submit for their own policies)

**URL**: `http://localhost:5000/api/claims`

**Request Body**:
```json
{
  "policy_id": 1,
  "claim_amount": 5000.00,
  "diagnosis": "Fractured arm",
  "treatment_details": "X-ray and cast application",
  "provider_name": "City Hospital",
  "service_date": "2024-01-15"
}
```

**Required Fields**: `policy_id`, `claim_amount`, `diagnosis`, `treatment_details`, `provider_name`, `service_date`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/claims \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": 1,
    "claim_amount": 5000.00,
    "diagnosis": "Fractured arm",
    "treatment_details": "X-ray and cast application",
    "provider_name": "City Hospital",
    "service_date": "2024-01-15"
  }'
```

**Success Response** (201):
```json
{
  "message": "Claim submitted successfully",
  "claim": {
    "id": 1,
    "claim_number": "CLM9876543210",
    "policy_id": 1,
    "user_id": 1,
    "claim_amount": 5000.00,
    "approved_amount": 0.00,
    "status": "submitted",
    "diagnosis": "Fractured arm",
    "treatment_details": "X-ray and cast application",
    "provider_name": "City Hospital",
    "service_date": "2024-01-15",
    "submitted_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `400`: Missing required fields, invalid amounts, or service date in future
- `401`: Missing or invalid token
- `403`: Insufficient permissions (trying to submit claim for another user's policy)
- `500`: Server error

**Note**: 
- Claim number is auto-generated (CLM + 10 digits)
- Claims can only be submitted for active policies
- Service date cannot be in the future

---

### 15. Get All Claims

**GET** `/api/claims`

**Functionality**: Retrieve claims (filtered by user role)

**Authentication**: Required (Bearer token)

**Access**: 
- Patients see only their own claims
- Providers/Admins see all claims

**URL**: `http://localhost:5000/api/claims`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/claims \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "claims": [
    {
      "id": 1,
      "claim_number": "CLM9876543210",
      "policy_id": 1,
      "user_id": 1,
      "claim_amount": 5000.00,
      "approved_amount": 0.00,
      "status": "submitted",
      "diagnosis": "Fractured arm",
      "treatment_details": "X-ray and cast application",
      "provider_name": "City Hospital",
      "service_date": "2024-01-15",
      "submitted_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `500`: Server error

---

### 16. Get Claim by ID

**GET** `/api/claims/<claim_id>`

**Functionality**: Retrieve a specific claim by ID

**Authentication**: Required (Bearer token)

**Access**: 
- Patients can only view their own claims
- Providers/Admins can view any claim

**URL**: `http://localhost:5000/api/claims/1`

**Example Request**:
```bash
curl -X GET http://localhost:5000/api/claims/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response** (200):
```json
{
  "claim": {
    "id": 1,
    "claim_number": "CLM9876543210",
    "policy_id": 1,
    "user_id": 1,
    "claim_amount": 5000.00,
    "approved_amount": 4500.00,
    "status": "approved",
    "diagnosis": "Fractured arm",
    "treatment_details": "X-ray and cast application",
    "provider_name": "City Hospital",
    "service_date": "2024-01-15",
    "submitted_at": "2024-01-15T10:30:00Z",
    "reviewed_by": 2,
    "reviewed_at": "2024-01-16T09:00:00Z",
    "review_notes": "Claim approved with minor adjustment"
  }
}
```

**Error Responses**:
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient trying to view another user's claim)
- `404`: Claim not found
- `500`: Server error

---

### 17. Review Claim

**POST** `/api/claims/<claim_id>/review`

**Functionality**: Review a claim (approve or deny with notes)

**Authentication**: Required (Bearer token)

**Access**: Administrator or Provider only

**URL**: `http://localhost:5000/api/claims/1/review`

**Request Body** (for approval):
```json
{
  "status": "approved",
  "approved_amount": 4500.00,
  "review_notes": "Claim approved with minor adjustment"
}
```

**Request Body** (for denial):
```json
{
  "status": "denied",
  "review_notes": "Treatment not covered under policy"
}
```

**Valid Statuses**: `under_review`, `approved`, `denied`

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/claims/1/review \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_amount": 4500.00,
    "review_notes": "Claim approved with minor adjustment"
  }'
```

**Success Response** (200):
```json
{
  "message": "Claim reviewed successfully",
  "claim": {
    "id": 1,
    "status": "approved",
    "approved_amount": 4500.00,
    "reviewed_by": 2,
    "reviewed_at": "2024-01-16T09:00:00Z",
    "review_notes": "Claim approved with minor adjustment"
  }
}
```

**Error Responses**:
- `400`: Missing status, invalid status, or approved_amount exceeds claim_amount
- `401`: Missing or invalid token
- `403`: Insufficient permissions (patient role cannot review claims)
- `500`: Server error

**Note**: 
- When approving, `approved_amount` is required and cannot exceed `claim_amount`
- When denying, `approved_amount` is automatically set to 0

---

### 18. Update Claim Status

**PATCH** `/api/claims/<claim_id>/status`

**Functionality**: Update claim status (admin-only operation)

**Authentication**: Required (Bearer token)

**Access**: Administrator only

**URL**: `http://localhost:5000/api/claims/1/status`

**Request Body**:
```json
{
  "status": "paid"
}
```

**Valid Statuses**: `submitted`, `under_review`, `approved`, `denied`, `paid`

**Example Request**:
```bash
curl -X PATCH http://localhost:5000/api/claims/1/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "paid"
  }'
```

**Success Response** (200):
```json
{
  "message": "Claim status updated successfully",
  "claim": {
    "id": 1,
    "status": "paid",
    "updated_at": "2024-01-17T10:00:00Z"
  }
}
```

**Error Responses**:
- `400`: Invalid status value
- `401`: Missing or invalid token
- `403`: Insufficient permissions (not administrator)
- `500`: Server error

---

## Testing Workflow

### Step 1: Register Users
1. Register a patient: `POST /api/auth/register` with role `patient`
2. Register a provider: `POST /api/auth/register` with role `provider`
3. Register an admin: `POST /api/auth/register` with role `administrator`

### Step 2: Login
1. Login as any user: `POST /api/auth/login`
2. Save the JWT token from the response

### Step 3: Create Policy (as Admin/Provider)
1. Use the admin/provider token
2. Create a policy: `POST /api/policies` with a valid `user_id`

### Step 4: Submit Claim (as Patient)
1. Use the patient token
2. Submit a claim: `POST /api/claims` with the `policy_id` from Step 3

### Step 5: Review Claim (as Admin/Provider)
1. Use the admin/provider token
2. Review the claim: `POST /api/claims/<claim_id>/review`

### Step 6: Update Claim Status (as Admin)
1. Use the admin token
2. Update claim status: `PATCH /api/claims/<claim_id>/status`

---

## Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid input data or validation error
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions for this operation
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Authentication Token Usage

All authenticated endpoints require the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

The token expires after 24 hours. To get a new token, login again using `POST /api/auth/login`.

---

## Role-Based Access Summary

| Endpoint | Patient | Provider | Administrator |
|----------|---------|----------|---------------|
| Register | ✅ | ✅ | ✅ |
| Login | ✅ | ✅ | ✅ |
| Get Current User | ✅ | ✅ | ✅ |
| Get All Users | ❌ | ✅ | ✅ |
| Get User by ID | Own only | ✅ | ✅ |
| Update User | Own only | Own only | ✅ |
| Activate/Deactivate User | ❌ | ❌ | ✅ |
| Create Policy | ❌ | ✅ | ✅ |
| Get Policies | Own only | All | All |
| Update Policy | ❌ | ✅ | ✅ |
| Update Policy Status | ❌ | ❌ | ✅ |
| Submit Claim | Own policies | Own policies | Own policies |
| Get Claims | Own only | All | All |
| Review Claim | ❌ | ✅ | ✅ |
| Update Claim Status | ❌ | ❌ | ✅ |

---

## Postman/Thunder Client Collection

You can import these endpoints into Postman or Thunder Client:

1. Create a new collection: "Healthcare Insurance API"
2. Set base URL variable: `{{base_url}}` = `http://localhost:5000`
3. Set token variable: `{{token}}` = (from login response)
4. Add Authorization header to all authenticated requests: `Bearer {{token}}`

---

## Notes

- All dates should be in `YYYY-MM-DD` format
- All amounts are decimal numbers (e.g., `5000.00`)
- Policy numbers are auto-generated: `POL` + 10 random digits
- Claim numbers are auto-generated: `CLM` + 10 random digits
- Password minimum length: 8 characters
- JWT token expiration: 24 hours

