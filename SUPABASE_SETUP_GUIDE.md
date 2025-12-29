# 🎯 SUPABASE + RENDER FREE TIER SETUP

**Test everything for FREE before paying!**

---

## STEP 1: SETUP SUPABASE DATABASE (5 minutes) - FREE

### A. Create Supabase Account
1. Go to https://supabase.com
2. Click **"Start your project"**
3. Sign up with GitHub (recommended) or email
4. **FREE TIER**: Unlimited API requests, 500MB database, 1GB file storage

### B. Create New Project
1. Click **"New Project"**
2. Settings:
   - **Name**: `angels-ai-school`
   - **Database Password**: Create strong password (SAVE THIS!)
   - **Region**: Choose closest to you (Singapore for Africa/Asia, Frankfurt for Europe)
   - **Plan**: **Free** ✅
3. Click **"Create new project"**
4. Wait 2-3 minutes for setup

### C. Get Database URL
1. Go to **Project Settings** → **Database**
2. Scroll to **Connection String**
3. Select **URI** tab
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
5. **Replace `[YOUR-PASSWORD]` with your actual password!**

### D. Run Database Schema
1. Go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy ALL contents from `/workspace/database/COMPLETE_DATABASE_SCHEMA.sql`
4. Paste into SQL Editor
5. Click **"Run"** (or press Ctrl+Enter)
6. Wait ~30 seconds
7. You should see: ✅ Success message with "DATABASE SCHEMA CREATED SUCCESSFULLY!"

### E. Verify Tables Created
1. Go to **Table Editor** (left sidebar)
2. You should see 80+ tables:
   - schools
   - students
   - teachers
   - parents
   - attendance
   - grades
   - fees
   - payments
   - and 70+ more...

✅ **Supabase Setup Complete!**

---

## STEP 2: DEPLOY TO RENDER FREE TIER (10 minutes) - FREE

### A. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. **FREE TIER**: 750 hours/month, sleeps after 15 min inactivity

### B. Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect to GitHub repo: `colmeta/angels-ai-school`
3. Settings:
   - **Name**: `angels-ai-backend-test`
   - **Branch**: `cursor/integrate-ai-agent-api-key-and-automate-services-ad91`
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free** ✅ (Select the $0/month option)
4. **STOP! Don't deploy yet - add environment variables first**

### C. Set Environment Variables (MINIMUM for testing)

Click **"Environment"** tab, add these 10 variables:

```bash
# 1. Database (from Supabase)
DATABASE_URL
postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres

# 2. Generate JWT Secret (run this command locally)
JWT_SECRET_KEY
PASTE_HERE_openssl_rand_hex_32

# 3. Generate Encryption Key (run this command locally)
ENCRYPTION_KEY
PASTE_HERE_python_fernet_key

# 4. Clarity AI (already configured)
CLARITY_API_KEY
cp_live_demo_2024_clarity_pearl_ai_test_key_001

CLARITY_API_URL
https://veritas-engine-zae0.onrender.com

# 5. App Settings
DEFAULT_BRAND_NAME
Angels AI School Test

API_BASE_URL
https://angels-ai-backend-test.onrender.com

ACCESS_TOKEN_EXPIRE_MINUTES
60

REFRESH_TOKEN_EXPIRE_DAYS
7

# 6. Optional but recommended
LOG_LEVEL
INFO
```

**Generate Keys Locally**:
```bash
# JWT Secret
openssl rand -hex 32

# Encryption Key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### D. Deploy!
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build
3. Watch the logs for any errors
4. When you see: `Uvicorn running on http://0.0.0.0:10000` ✅ SUCCESS!

---

## STEP 3: TEST YOUR DEPLOYMENT (5 minutes)

### A. Test Health Endpoint

Open in browser or curl:
```bash
https://angels-ai-backend-test.onrender.com/api/health
```

**Expected Response**:
```json
{
  "timestamp": "2025-11-09...",
  "uptime_seconds": 123,
  "status": "healthy",
  "checks": {
    "database": {
      "healthy": true,
      "response_time_ms": 45.2,
      "status": "connected"
    },
    "clarity_api": {
      "healthy": true,
      "response_time_ms": 320.5,
      "status": "available"
    }
  }
}
```

✅ If you see this = **EVERYTHING WORKS!**

### B. Test API Documentation

Open: `https://angels-ai-backend-test.onrender.com/docs`

You should see:
- 200+ API endpoints
- All 39 features documented
- Interactive API testing interface

### C. Test Clarity Chatbot

```bash
curl -X POST https://angels-ai-backend-test.onrender.com/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I check fees?",
    "school_id": "550e8400-e29b-41d4-a716-446655440000",
    "domain": "financial"
  }'
```

Should return AI response from Clarity! ✅

---

## STEP 4: CREATE TEST SCHOOL & USER (5 minutes)

### A. Using Supabase SQL Editor

1. Go to **SQL Editor** in Supabase
2. Run this to create test school (already created by schema):

```sql
-- Test school already exists!
SELECT * FROM schools WHERE name = 'Demo School Uganda';
```

3. Create a test admin user:

```sql
-- Insert test admin user
INSERT INTO users (email, password_hash, first_name, last_name, role, status) VALUES
(
    'admin@demoschool.ug',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZZPw4V2G', -- Password: "test123"
    'Admin',
    'User',
    'admin',
    'active'
);

-- Link user to school
INSERT INTO user_schools (user_id, school_id, role, is_primary)
SELECT 
    u.id,
    s.id,
    'admin',
    true
FROM users u, schools s
WHERE u.email = 'admin@demoschool.ug'
AND s.name = 'Demo School Uganda';
```

4. Test login (use API docs `/docs` → `/api/auth/login`):
   - Email: `admin@demoschool.ug`
   - Password: `test123`

### B. Create Test Student

```sql
-- Insert test student
INSERT INTO students (
    school_id, 
    admission_number, 
    first_name, 
    last_name, 
    date_of_birth,
    gender,
    class_name,
    stream,
    status
) 
SELECT 
    s.id,
    'S001',
    'John',
    'Doe',
    '2010-05-15',
    'Male',
    'Primary 5',
    'A',
    'active'
FROM schools s 
WHERE s.name = 'Demo School Uganda';
```

---

## STEP 5: TEST KEY FEATURES (10 minutes)

Use the API docs at `/docs` to test:

### ✅ 1. Authentication
- POST `/api/auth/login` with test credentials
- Save the `access_token`

### ✅ 2. Students
- GET `/api/students/school/{school_id}`
- Should see "John Doe"

### ✅ 3. Chatbot
- POST `/api/chatbot/message`
- Ask: "How many students are enrolled?"

### ✅ 4. Health Check
- GET `/api/health`
- Should show "healthy"

### ✅ 5. API Documentation
- Browse all 200+ endpoints
- Test different features

---

## 💰 COST BREAKDOWN - TESTING PHASE

| Service | Plan | Cost | Limitations |
|---------|------|------|-------------|
| **Supabase** | Free | **$0** | 500MB DB, 1GB storage, 50k monthly active users |
| **Render Web Service** | Free | **$0** | 750 hrs/month, sleeps after 15 min |
| **Clarity AI** | Your API | **$0** | Already your own |
| **TOTAL** | | **$0/month** ✅ | Perfect for testing! |

**Limitations on Free Tier**:
- ⚠️ Render sleeps after 15 min inactivity (30s cold start)
- ⚠️ Supabase 500MB limit (enough for 100+ students)
- ⚠️ No automated backups on free tiers

---

## 🚀 WHEN TO UPGRADE TO PAID

**Upgrade when you see**:
1. ✅ Everything works perfectly
2. ✅ First client ready to onboard
3. ✅ Need 24/7 availability (no sleep)
4. ✅ Need automated backups
5. ✅ Need more than 500MB database

**Paid Tier Costs**:
- **Supabase Pro**: $25/month (8GB DB, automated backups, no sleep)
- **Render Starter**: $7/month (always on, better performance)
- **Total**: $32/month for production-ready system

---

## 🚨 TROUBLESHOOTING FREE TIER

### Issue 1: "Cannot connect to database"
**Solution**:
- Check DATABASE_URL has correct password
- Ensure Supabase project is not paused (free tier pauses after 7 days inactivity)
- Go to Supabase dashboard and click "Resume project"

### Issue 2: Render service times out
**Solution**:
- Free tier sleeps after 15 min
- First request takes 30-60 seconds (cold start)
- Just wait and refresh

### Issue 3: "JWT_SECRET_KEY not set"
**Solution**:
- Go to Render Environment variables
- Add JWT_SECRET_KEY
- Restart service

### Issue 4: Build fails on Render
**Solution**:
- Check build logs in Render dashboard
- Common issue: Python version mismatch
- Ensure `runtime.txt` has `python-3.11.8`

---

## ✅ SUCCESS CHECKLIST

Before onboarding first client, verify:

- [ ] ✅ Supabase database created (80+ tables)
- [ ] ✅ Render service deployed successfully
- [ ] ✅ Health check returns "healthy"
- [ ] ✅ API docs accessible at `/docs`
- [ ] ✅ Clarity chatbot responds
- [ ] ✅ Test school created
- [ ] ✅ Test admin login works
- [ ] ✅ Test student created
- [ ] ✅ Can create attendance record
- [ ] ✅ Can record payment
- [ ] ✅ Can send message/notification

---

## 🎯 NEXT: ONBOARD FIRST CLIENT

Once everything works on free tier:

1. **Upgrade to Paid** ($32/month)
   - Supabase Pro: $25/month
   - Render Starter: $7/month

2. **Setup Production Features**
   - Mobile Money API keys (MTN, Airtel)
   - SMS provider (Africa's Talking)
   - Email provider (SendGrid)
   - OCR (Google Cloud Vision)

3. **Onboard Client**
   - Create their school in database
   - Import students/teachers
   - Train staff on system
   - Start using!

4. **Monitor & Iterate**
   - Watch metrics
   - Collect feedback
   - Fix issues
   - Add features as needed

---

## 📞 SUPPORT

**Free Tier Help**:
- Supabase Docs: https://supabase.com/docs
- Render Docs: https://render.com/docs/free
- Render Community: https://community.render.com

**Platform Issues**:
- Check Render logs: `render logs -s angels-ai-backend-test`
- Check Supabase logs: Project → Logs
- API errors: Check `/api/health` for status

---

## 🎉 YOU'RE READY!

**Total Setup Time**: 25 minutes  
**Total Cost**: $0  
**Features**: All 39 features working  
**Database**: 80+ tables ready  
**API**: 200+ endpoints live  

**Test everything, then upgrade when you're ready to onboard your first client!** 🚀
