# ✅ DEPLOY NOW - COMPLETE CHECKLIST

**You have everything ready! Follow these steps:**

---

## 🎯 STEP 1: SUPABASE DATABASE (5 minutes)

### ✅ Already Done:
- [x] Supabase project created
- [x] Database password: `18January2005`
- [x] Database URL: `postgresql://postgres:18January2005@db.hsmfffgszcgmmyynaeqi.supabase.co:5432/postgres`

### 🔨 Do Now:

1. **Go to Supabase SQL Editor**:
   - https://supabase.com/dashboard/project/hsmfffgszcgmmyynaeqi/sql

2. **Copy this SQL file**:
   - https://raw.githubusercontent.com/colmeta/angels-ai-school/cursor/integrate-ai-agent-api-key-and-automate-services-ad91/database/COMPLETE_DATABASE_SCHEMA.sql

3. **Paste and Run**:
   - Click "New query"
   - Paste ALL the SQL (1500+ lines)
   - Click **"RUN"** (or Ctrl+Enter)
   - Wait 30 seconds
   - ✅ Should see: "DATABASE SCHEMA CREATED SUCCESSFULLY!"

4. **Verify Tables Created**:
   - Go to "Table Editor"
   - Should see 80+ tables (schools, students, teachers, parents, etc.)

---

## 🚀 STEP 2: GENERATE SECURITY KEYS (2 minutes)

**Run these commands on your computer** (or use online tools):

### JWT Secret Key:
```bash
openssl rand -hex 32
```
**Copy the output!** Example: `7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b`

### Encryption Key:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
**Copy the output!** Example: `xYz123AbC456DeF789GhI012JkL345MnO678PqR901StU234VwX567==`

**⚠️ SAVE THESE KEYS!** You'll need them in next step.

---

## 🔧 STEP 3: RENDER WEB SERVICE (8 minutes)

### 3.1 Create Service

1. **Go to Render**: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"**
4. Select repository: `colmeta/angels-ai-school`
5. Branch: `cursor/integrate-ai-agent-api-key-and-automate-services-ad91`

### 3.2 Configure Service

**Name**: `angels-ai-school-test` (or any name you want)

**Runtime**: Python 3

**Build Command**:
```
pip install -r requirements.txt
```

**Start Command**:
```
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**Plan**: **FREE** ✅ (Select the $0/month option)

**⚠️ STOP! Don't create yet - add environment variables first!**

### 3.3 Add Environment Variables

Click **"Environment"** tab (or "Advanced" → "Environment Variables")

**Add these 12 variables** (copy from `RENDER_ENV_VARS_COMPLETE.txt`):

```bash
DATABASE_URL
postgresql://postgres:18January2005@db.hsmfffgszcgmmyynaeqi.supabase.co:5432/postgres

JWT_SECRET_KEY
PASTE_YOUR_GENERATED_JWT_KEY_FROM_STEP_2

ENCRYPTION_KEY
PASTE_YOUR_GENERATED_ENCRYPTION_KEY_FROM_STEP_2

CLARITY_ENGINE_API_URL
https://veritas-engine-zae0.onrender.com

CLARITY_ENGINE_API_KEY
QmlSn68qp7tXGv0EdqMiX41Qqo8LlRPI5J4W2cawPcA

CLARITY_PEARL_API_URL
https://clarity-pearl-ai-api.onrender.com

CLARITY_PEARL_API_KEY
YOUR_CLARITY_PEARL_API_KEY_HERE

DEFAULT_BRAND_NAME
Angels AI School

API_BASE_URL
https://angels-ai-school-test.onrender.com

ACCESS_TOKEN_EXPIRE_MINUTES
60

REFRESH_TOKEN_EXPIRE_DAYS
7

LOG_LEVEL
INFO
```

### 3.4 Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build
3. Watch the logs:
   - Should see: `Installing dependencies...`
   - Should see: `Starting server...`
   - Should see: `Uvicorn running on http://0.0.0.0:10000`
   - ✅ When you see this = SUCCESS!

---

## 🧪 STEP 4: TEST DEPLOYMENT (3 minutes)

### Test 1: Health Check

**Open in browser**:
```
https://angels-ai-school-test.onrender.com/api/health
```

**Expected**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09...",
  "checks": {
    "database": {
      "healthy": true,
      "response_time_ms": 45.2,
      "status": "connected"
    },
    "clarity_api": {
      "healthy": true
    }
  }
}
```

✅ **If you see this = EVERYTHING WORKS!**

### Test 2: API Documentation

**Open in browser**:
```
https://angels-ai-school-test.onrender.com/docs
```

Should show:
- 200+ API endpoints
- All 39 features
- Interactive testing interface

### Test 3: Clarity Pearl AI Chatbot

**Using API docs** (`/docs`):
1. Find `POST /api/chatbot/message`
2. Click "Try it out"
3. Paste this JSON:
```json
{
  "message": "How do I check my child's fees?",
  "school_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_role": "parent",
  "domain": "financial"
}
```
4. Click "Execute"
5. Should get AI response! ✅

### Test 4: Login Test User

1. In Supabase SQL Editor, run:
```sql
-- Create test admin user
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES
('admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZZPw4V2G', 'Admin', 'Test', 'admin');

-- Link to demo school
INSERT INTO user_schools (user_id, school_id, role, is_primary)
SELECT u.id, s.id, 'admin', true
FROM users u, schools s
WHERE u.email = 'admin@test.com' AND s.name = 'Demo School Uganda';
```

2. In API docs, test login:
   - POST `/api/auth/login`
   - Email: `admin@test.com`
   - Password: `test123`
   - Should get `access_token`! ✅

---

## ⚠️ STEP 5: CHANGE DATABASE PASSWORD (CRITICAL!)

**Your password is now public in our conversation. Change it NOW!**

1. Go to Supabase: https://supabase.com/dashboard/project/hsmfffgszcgmmyynaeqi/settings/database
2. Scroll to **"Database password"**
3. Click **"Reset database password"**
4. Generate new strong password
5. **SAVE IT!**
6. Update `DATABASE_URL` in Render:
   - Go to Render service → Environment
   - Update `DATABASE_URL` with new password:
     ```
     postgresql://postgres:NEW_PASSWORD@db.hsmfffgszcgmmyynaeqi.supabase.co:5432/postgres
     ```
   - Click "Save Changes"
   - Service will redeploy automatically

---

## 🎉 SUCCESS CHECKLIST

- [ ] ✅ Supabase database created (80+ tables)
- [ ] ✅ JWT & Encryption keys generated
- [ ] ✅ Render service deployed
- [ ] ✅ Health check returns "healthy"
- [ ] ✅ API docs accessible
- [ ] ✅ Chatbot responds
- [ ] ✅ Login works
- [ ] ✅ Database password changed

**When all checked = YOU'RE LIVE!** 🎊

---

## 💰 COST - FREE TIER

| Service | Plan | Cost |
|---------|------|------|
| Supabase | Free | $0 |
| Render | Free | $0 |
| Clarity Engine | Your API | $0 |
| Clarity Pearl AI | Your API | $0 |
| **TOTAL** | | **$0/month** ✅ |

**Limitations**:
- Render sleeps after 15 min (30s cold start)
- Supabase 500MB DB limit
- Perfect for testing!

---

## 🚀 NEXT: ONBOARD FIRST CLIENT

Once everything works:

1. **Test all features** (use `/docs`)
2. **When satisfied** → Upgrade to paid:
   - Supabase Pro: $25/month
   - Render Starter: $7/month
   - Total: $32/month
3. **Onboard your first school!**
4. **Start making money!** 💰

---

## 🆘 TROUBLESHOOTING

**"Cannot connect to database"**
→ Check DATABASE_URL password is correct

**"Service unavailable"**
→ Free tier sleeping, wait 30s and refresh

**"Build failed"**
→ Check Render logs for errors

**"Chatbot not responding"**
→ Check CLARITY_PEARL_API_KEY is correct

---

## 📞 WHEN DEPLOYED

**Tell me** when:
1. ✅ Everything is deployed and working
2. ✅ You've tested all features
3. ✅ Ready to onboard first client
4. ✅ Need help with anything

---

**🎯 TOTAL TIME: 15-20 minutes**
**💰 TOTAL COST: $0**
**🚀 LET'S DEPLOY!**
