# Supabase Database Setup Instructions

## Step-by-Step Guide

### 1. Open Supabase SQL Editor
- Go to your Supabase project dashboard
- Click on "SQL Editor" in the left sidebar
- Click "New query"

### 2. Copy and Paste the SQL

**IMPORTANT**: Copy the SQL statements below (not the filename), and paste them into the SQL Editor:

```sql
-- Healthcare Insurance Management API - Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Users table with role-based access
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('patient', 'provider', 'administrator')),
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Policies table with foreign key to users
CREATE TABLE IF NOT EXISTS policies (
    id BIGSERIAL PRIMARY KEY,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    policy_type VARCHAR(100) NOT NULL,
    coverage_amount DECIMAL(12, 2) NOT NULL,
    premium_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'cancelled')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Claims table with foreign keys to policies and users
CREATE TABLE IF NOT EXISTS claims (
    id BIGSERIAL PRIMARY KEY,
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    policy_id BIGINT NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    claim_amount DECIMAL(12, 2) NOT NULL,
    approved_amount DECIMAL(12, 2) DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'under_review', 'approved', 'denied', 'paid')),
    diagnosis TEXT,
    treatment_details TEXT,
    provider_name VARCHAR(255),
    service_date DATE NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_by BIGINT REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_policies_user_id ON policies(user_id);
CREATE INDEX IF NOT EXISTS idx_policies_status ON policies(status);
CREATE INDEX IF NOT EXISTS idx_claims_user_id ON claims(user_id);
CREATE INDEX IF NOT EXISTS idx_claims_policy_id ON claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3. Run the Query
- Click the "Run" button (or press Ctrl+Enter / Cmd+Enter)
- You should see "Success. No rows returned" or similar success message

### 4. Verify Tables Were Created
- Go to "Table Editor" in the left sidebar
- You should see three tables: `users`, `policies`, and `claims`

### 5. Check Your .env File

Make sure your `.env` file has the correct values:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_key_here
JWT_SECRET_KEY=your_jwt_secret_key
FLASK_ENV=development
```

**To get your Supabase credentials:**
1. Go to Project Settings > API
2. Copy the "Project URL" → use for `SUPABASE_URL`
3. Copy the "anon public" key → use for `SUPABASE_KEY` (or service_role key if you prefer)

### 6. Restart Flask App
After setting up the database and verifying your `.env` file:
1. Stop your Flask app (Ctrl+C)
2. Restart it: `python app.py`

### 7. Run Tests
Once everything is set up, run the test script:
```bash
python test_api.py
```

## Common Issues

### Issue: "Invalid API key" error
- Make sure you copied the **actual key value**, not just the variable name
- Check there are no extra spaces or quotes in your `.env` file
- Verify the key starts with `eyJ` (JWT token format)
- Restart Flask app after updating `.env`

### Issue: "relation does not exist" error
- Make sure you ran the SQL schema in Supabase SQL Editor
- Verify tables exist in Supabase Table Editor
- Check table names match exactly: `users`, `policies`, `claims`

### Issue: SQL syntax error
- Make sure you're copying the **SQL content**, not the filename
- Copy all the SQL statements from the file
- Don't include the filename `database_schema.sql` in the query

