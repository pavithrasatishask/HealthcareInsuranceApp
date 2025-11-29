# Troubleshooting Guide

## Issue: "Invalid API key" Error

If you're getting "Invalid API key" errors after updating your `.env` file:

### Solution: Restart the Flask Application

The Supabase client is initialized as a singleton when the Flask app starts. If you update the `.env` file, you **must restart the Flask app** for the changes to take effect.

**Steps:**
1. Stop the Flask app (Ctrl+C in the terminal where it's running)
2. Verify your `.env` file has the correct values:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_service_role_key_or_anon_key
   JWT_SECRET_KEY=your_jwt_secret
   FLASK_ENV=development
   ```
3. Start the Flask app again:
   ```bash
   python app.py
   ```

### Which Supabase Key to Use?

- **Anon/Public Key**: Use this for client-side operations (recommended for most cases)
- **Service Role Key**: Use this for server-side operations that bypass Row Level Security (RLS)

For this API, you can use either:
- **Anon key** (recommended) - if RLS is properly configured
- **Service role key** - if you want to bypass RLS (useful for admin operations)

### Verify Your Configuration

1. Check your Supabase project:
   - Go to: Project Settings > API
   - Copy the **Project URL** → use for `SUPABASE_URL`
   - Copy the **anon public** key → use for `SUPABASE_KEY` (or service_role key if needed)

2. Verify the `.env` file is in the project root (same directory as `app.py`)

3. Make sure there are no extra spaces or quotes in the `.env` file:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Test Your Configuration

After restarting, test with:
```bash
python test_api.py
```

If you still get errors, check:
- The Supabase URL format is correct (should start with `https://`)
- The API key is the full key (starts with `eyJ...`)
- The database schema has been set up (run `database_schema.sql` in Supabase SQL Editor)

