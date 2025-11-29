# .env File Format Check

## Correct Format

Your `.env` file should look like this:

```env
SUPABASE_URL=https://fveuyqyfzsthqvmqxbxg.supabase.co
SUPABASE_KEY=your_actual_supabase_key_here
JWT_SECRET_KEY=your_jwt_secret_key
FLASK_ENV=development
```

## Important Notes

1. **SUPABASE_URL should NOT include `/rest/v1/`**
   - ❌ Wrong: `https://fveuyqyfzsthqvmqxbxg.supabase.co/rest/v1/`
   - ✅ Correct: `https://fveuyqyfzsthqvmqxbxg.supabase.co`

2. **No quotes around values**
   - ❌ Wrong: `SUPABASE_URL="https://fveuyqyfzsthqvmqxbxg.supabase.co"`
   - ✅ Correct: `SUPABASE_URL=https://fveuyqyfzsthqvmqxbxg.supabase.co`

3. **No extra spaces**
   - ❌ Wrong: `SUPABASE_URL = https://fveuyqyfzsthqvmqxbxg.supabase.co`
   - ✅ Correct: `SUPABASE_URL=https://fveuyqyfzsthqvmqxbxg.supabase.co`

4. **SUPABASE_KEY should be the full key**
   - Should start with `eyJ` (JWT format)
   - Get it from: Supabase Dashboard > Settings > API > anon public key

## After Updating

1. Save the `.env` file
2. **Restart your Flask app** (stop with Ctrl+C, then run `python app.py` again)
3. Run the test: `python test_api.py`

