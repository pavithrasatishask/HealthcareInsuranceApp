# Healthcare Insurance API - Quick Reference

Base URL: `http://localhost:5000`

---

## 🔐 Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ❌ | Register new user |
| POST | `/api/auth/login` | ❌ | Login and get JWT token |
| GET | `/api/auth/me` | ✅ | Get current user details |

---

## 👥 User Management Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/api/users` | ✅ | Admin/Provider | Get all users |
| GET | `/api/users/<id>` | ✅ | All* | Get user by ID |
| PUT | `/api/users/<id>` | ✅ | All* | Update user |
| POST | `/api/users/<id>/activate` | ✅ | Admin | Activate user |
| POST | `/api/users/<id>/deactivate` | ✅ | Admin | Deactivate user |

*Patients can only access their own profile

---

## 📋 Policy Management Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/api/policies` | ✅ | Admin/Provider | Create policy |
| GET | `/api/policies` | ✅ | All* | Get policies |
| GET | `/api/policies/<id>` | ✅ | All* | Get policy by ID |
| PUT | `/api/policies/<id>` | ✅ | Admin/Provider | Update policy |
| PATCH | `/api/policies/<id>/status` | ✅ | Admin | Update policy status |

*Patients see only their own policies

---

## 🏥 Claims Processing Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/api/claims` | ✅ | All | Submit claim |
| GET | `/api/claims` | ✅ | All* | Get claims |
| GET | `/api/claims/<id>` | ✅ | All* | Get claim by ID |
| POST | `/api/claims/<id>/review` | ✅ | Admin/Provider | Review claim |
| PATCH | `/api/claims/<id>/status` | ✅ | Admin | Update claim status |

*Patients see only their own claims

---

## 📝 Sample Request Examples

### Register User
```bash
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "email": "patient@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "patient"
}
```

### Login
```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "patient@example.com",
  "password": "password123"
}
```

### Create Policy (Admin/Provider)
```bash
POST http://localhost:5000/api/policies
Authorization: Bearer <token>
Content-Type: application/json

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

### Submit Claim
```bash
POST http://localhost:5000/api/claims
Authorization: Bearer <token>
Content-Type: application/json

{
  "policy_id": 1,
  "claim_amount": 5000.00,
  "diagnosis": "Fractured arm",
  "treatment_details": "X-ray and cast",
  "provider_name": "City Hospital",
  "service_date": "2024-01-15"
}
```

### Review Claim (Admin/Provider)
```bash
POST http://localhost:5000/api/claims/1/review
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "approved",
  "approved_amount": 4500.00,
  "review_notes": "Claim approved"
}
```

---

## 🔑 Authentication Header

For all authenticated endpoints, include:
```
Authorization: Bearer <your_jwt_token>
```

---

## ✅ Validation URLs

Test these endpoints in order:

1. **Health Check**: `GET http://localhost:5000/`
2. **Register**: `POST http://localhost:5000/api/auth/register`
3. **Login**: `POST http://localhost:5000/api/auth/login`
4. **Get Current User**: `GET http://localhost:5000/api/auth/me` (with token)
5. **Create Policy**: `POST http://localhost:5000/api/policies` (with admin/provider token)
6. **Get Policies**: `GET http://localhost:5000/api/policies` (with token)
7. **Submit Claim**: `POST http://localhost:5000/api/claims` (with patient token)
8. **Get Claims**: `GET http://localhost:5000/api/claims` (with token)
9. **Review Claim**: `POST http://localhost:5000/api/claims/1/review` (with admin/provider token)

---

## 📊 Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Server Error

---

## 🎯 Quick Test Flow

1. Register 3 users: patient, provider, admin
2. Login as each and save tokens
3. As admin/provider: Create a policy for the patient
4. As patient: Submit a claim for that policy
5. As admin/provider: Review and approve the claim
6. As admin: Update claim status to "paid"

---

For detailed documentation, see `API_DOCUMENTATION.md`

