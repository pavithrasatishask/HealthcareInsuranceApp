# Healthcare Insurance Management API

A Flask-based REST API for managing healthcare insurance policies and claims. This is Phase 1 of a MicroSaaS project that will eventually include an AI-powered codebase assistant.

## Features

- **User Management**: Registration, authentication, and role-based access control
- **Policy Management**: Create, view, and manage insurance policies
- **Claims Processing**: Submit, review, and track insurance claims

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **CORS**: flask-cors

## Project Structure

```
healthcare-insurance-api/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── database_schema.sql      # Database schema for Supabase
├── README.md                # This file
├── routes/
│   ├── __init__.py
│   ├── auth.py              # Authentication endpoints
│   ├── users.py             # User management endpoints
│   ├── policies.py          # Policy management endpoints
│   └── claims.py            # Claims processing endpoints
├── services/
│   ├── __init__.py
│   ├── supabase_client.py   # Supabase client singleton
│   ├── auth_service.py      # Authentication logic
│   ├── user_service.py      # User business logic
│   ├── policy_service.py    # Policy business logic
│   └── claim_service.py     # Claim business logic
└── utils/
    ├── __init__.py
    └── helpers.py           # Authentication decorators
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Supabase account and project
- pip (Python package manager)

### 2. Clone and Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Supabase Setup

1. Create a new project in [Supabase](https://supabase.com)
2. Go to SQL Editor in your Supabase dashboard
3. Copy and run the SQL from `database_schema.sql`
4. Get your project URL and anon key from Settings > API

### 4. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   JWT_SECRET_KEY=generate_a_secure_random_key_here
   FLASK_ENV=development
   ```

3. Generate a secure JWT secret key:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

### 5. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "patient",
  "phone": "1234567890",
  "address": "123 Main St",
  "date_of_birth": "1990-01-01"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "patient"
  }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### User Management

#### Get All Users (Admin/Provider only)
```http
GET /api/users
Authorization: Bearer <token>
```

#### Get User by ID
```http
GET /api/users/<id>
Authorization: Bearer <token>
```

#### Update User
```http
PUT /api/users/<id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Updated Name",
  "phone": "9876543210"
}
```

#### Activate/Deactivate User (Admin only)
```http
POST /api/users/<id>/activate
POST /api/users/<id>/deactivate
Authorization: Bearer <token>
```

### Policy Management

#### Create Policy (Admin/Provider only)
```http
POST /api/policies
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

#### Get Policies
```http
GET /api/policies
Authorization: Bearer <token>
```

#### Get Policy by ID
```http
GET /api/policies/<id>
Authorization: Bearer <token>
```

#### Update Policy (Admin/Provider only)
```http
PUT /api/policies/<id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "coverage_amount": 75000.00,
  "premium_amount": 750.00
}
```

#### Update Policy Status (Admin only)
```http
PATCH /api/policies/<id>/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "inactive"
}
```

### Claims Processing

#### Submit Claim
```http
POST /api/claims
Authorization: Bearer <token>
Content-Type: application/json

{
  "policy_id": 1,
  "claim_amount": 5000.00,
  "diagnosis": "Fractured arm",
  "treatment_details": "X-ray and cast application",
  "provider_name": "City Hospital",
  "service_date": "2024-01-15"
}
```

#### Get Claims
```http
GET /api/claims
Authorization: Bearer <token>
```

#### Get Claim by ID
```http
GET /api/claims/<id>
Authorization: Bearer <token>
```

#### Review Claim (Admin/Provider only)
```http
POST /api/claims/<id>/review
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "approved",
  "approved_amount": 4500.00,
  "review_notes": "Claim approved with minor adjustment"
}
```

#### Update Claim Status (Admin only)
```http
PATCH /api/claims/<id>/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "paid"
}
```

## User Roles

- **Patient**: Can view and manage their own policies and claims
- **Provider**: Can view all policies and claims, create policies, review claims
- **Administrator**: Full access to all features, can manage users and update statuses

## Business Rules

### User Management
- Email must be unique
- Password minimum 8 characters
- Users can only update their own profiles (except admins)
- Only admins can change user roles

### Policy Management
- Policy numbers are auto-generated (POL + 10 digits)
- Only active policies can have claims submitted
- Coverage and premium amounts must be positive
- End date must be after start date

### Claims Processing
- Claim numbers are auto-generated (CLM + 10 digits)
- Patients can only submit claims for their own policies
- Claims can only be submitted for active policies
- Approved amount cannot exceed claim amount
- Service date cannot be in the future

## Testing

### Generate Password Hash for Testing

To create test users with known passwords, generate password hashes:

```python
import bcrypt

password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
```

### Sample Test Data

You can insert test users directly in Supabase SQL Editor:

```sql
-- Note: Replace [bcrypt_hash] with actual bcrypt hash from above

-- Administrator
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@healthcare.com', '[bcrypt_hash]', 'Admin User', 'administrator');

-- Provider
INSERT INTO users (email, password_hash, full_name, role) VALUES
('provider@healthcare.com', '[bcrypt_hash]', 'Dr. Provider', 'provider');

-- Patient
INSERT INTO users (email, password_hash, full_name, role, date_of_birth) VALUES
('patient@healthcare.com', '[bcrypt_hash]', 'Patient User', 'patient', '1990-01-01');
```

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

## Security Features

- JWT-based authentication with 24-hour expiration
- Password hashing with bcrypt (12 salt rounds)
- Role-based access control
- Input validation
- Parameterized queries (handled by Supabase)
- CORS enabled for frontend integration

## Development

### Running in Development Mode

The app runs in development mode by default when `FLASK_ENV=development` in `.env`.

### Code Organization

- **Routes**: Handle HTTP requests/responses
- **Services**: Contain business logic
- **Utils**: Reusable utilities and decorators
- **Config**: Centralized configuration

## Future Enhancements

This is Phase 1 of the project. Future phases may include:
- AI-powered codebase assistant
- Advanced analytics and reporting
- Document management
- Email notifications
- Payment processing integration

## License

This project is part of a MicroSaaS development initiative.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

