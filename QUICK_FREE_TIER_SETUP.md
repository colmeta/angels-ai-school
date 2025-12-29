# ⚡ QUICK FREE TIER SETUP - 15 MINUTES

**Test everything FREE before paying!**

---

## 📋 WHAT YOU NEED

1. GitHub account
2. Supabase account (create free at supabase.com)
3. Render account (create free at render.com)
4. 15 minutes of time

**Total Cost**: $0 ✅

---

## 🎯 STEP 1: SUPABASE (5 min)

### 1.1 Create Project
- Go to https://supabase.com
- Click "New Project"
- Name: `angels-ai-school`
- Set password (SAVE IT!)
- Region: Frankfurt or Singapore
- Plan: **FREE**

### 1.2 Get Database URL
- Project Settings → Database
- Copy "URI" connection string
- Replace `[YOUR-PASSWORD]` with your actual password

### 1.3 Run Database Schema
- Go to **SQL Editor**
- Click "New query"
- Open file: `/workspace/database/COMPLETE_DATABASE_SCHEMA.sql`
- Copy ALL (1500+ lines)
- Paste into editor
- Click **"Run"**
- Wait ~30 seconds
- ✅ Should see success message!

### 1.4 Verify
- Go to **Table Editor**
- Should see 80+ tables ✅

---

## 🚀 STEP 2: RENDER (8 min)

### 2.1 Create Web Service
- Go to https://render.com
- New + → Web Service
- Connect GitHub: `colmeta/angels-ai-school`
- Branch: `cursor/integrate-ai-agent-api-key-and-automate-services-ad91`
- Name: `angels-ai-test`
- Plan: **FREE**

### 2.2 Build Settings
```
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### 2.3 Environment Variables (MINIMUM 10)

**STOP! Don't deploy yet. Add these first:**

```bash
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres

JWT_SECRET_KEY=GENERATE_THIS_LOCALLY

ENCRYPTION_KEY=GENERATE_THIS_LOCALLY

CLARITY_API_KEY=cp_live_demo_2024_clarity_pearl_ai_test_key_001

CLARITY_API_URL=https://veritas-engine-zae0.onrender.com

DEFAULT_BRAND_NAME=Angels AI School

API_BASE_URL=https://angels-ai-test.onrender.com

ACCESS_TOKEN_EXPIRE_MINUTES=60

REFRESH_TOKEN_EXPIRE_DAYS=7

LOG_LEVEL=INFO
```

**Generate Keys** (run locally in terminal):
```bash
# JWT Secret
openssl rand -hex 32

# Encryption Key  
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2.4 Deploy
- Click "Create Web Service"
- Wait 5-10 minutes
- Watch logs for: `Uvicorn running` ✅

---

## ✅ STEP 3: TEST (2 min)

### Test Health
Open in browser:
```
https://angels-ai-test.onrender.com/api/health
```

Should show:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"healthy": true},
    "clarity_api": {"healthy": true}
  }
}
```

### Test API Docs
```
https://angels-ai-test.onrender.com/docs
```

Should show 200+ endpoints ✅

### Test Chatbot
```bash
curl -X POST https://angels-ai-test.onrender.com/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","school_id":"550e8400-e29b-41d4-a716-446655440000","domain":"education"}'
```

Should return AI response ✅

---

## 🎉 SUCCESS!

**If all 3 tests pass, you have**:
- ✅ 39 features live
- ✅ 80+ database tables
- ✅ 200+ API endpoints
- ✅ Clarity AI chatbot
- ✅ All systems working
- ✅ $0 cost

---

## 📱 QUICK TEST LOGIN

### Create Test User (in Supabase SQL Editor)

```sql
-- Insert admin user
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES
('admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZZPw4V2G', 'Admin', 'Test', 'admin');

-- Link to demo school
INSERT INTO user_schools (user_id, school_id, role, is_primary)
SELECT u.id, s.id, 'admin', true
FROM users u, schools s
WHERE u.email = 'admin@test.com' AND s.name = 'Demo School Uganda';
```

**Login Credentials**:
- Email: `admin@test.com`
- Password: `test123`

Test at: `https://angels-ai-test.onrender.com/docs` → POST `/api/auth/login`

---

## ⚠️ FREE TIER LIMITATIONS

1. **Render**: Sleeps after 15 min (30s cold start on first request)
2. **Supabase**: 500MB database limit (enough for 100+ students)
3. **Supabase**: Pauses after 7 days inactivity (just click "Resume")

**These are perfect for testing!**

---

## 💰 WHEN TO UPGRADE

**Upgrade to paid when**:
1. Everything works ✅
2. First client ready ✅
3. Need 24/7 uptime ✅
4. Need automated backups ✅

**Paid costs**:
- Supabase Pro: $25/month
- Render Starter: $7/month
- **Total: $32/month**

---

## 🚨 TROUBLESHOOTING

**"Cannot connect to database"**
→ Check DATABASE_URL password is correct

**"Service unavailable"**
→ Free tier is sleeping, wait 30s and refresh

**"Build failed"**
→ Check Render logs, usually missing env vars

**"Supabase project paused"**
→ Go to Supabase dashboard, click "Resume project"

---

## 📞 NEXT STEPS

1. ✅ Test all features using `/docs`
2. ✅ Create test students, teachers
3. ✅ Try bulk operations
4. ✅ Test chatbot queries
5. ✅ Upload a photo (OCR test)
6. ✅ When satisfied → Upgrade to paid
7. ✅ Onboard first client!

---

## 📁 FILES YOU NEED

1. **Database SQL**: `/workspace/database/COMPLETE_DATABASE_SCHEMA.sql`
2. **Full Guide**: `/workspace/SUPABASE_SETUP_GUIDE.md`
3. **Deployment**: `/workspace/RENDER_PRODUCTION_DEPLOYMENT.md`

---

**🎯 TOTAL TIME: 15 minutes**  
**💰 TOTAL COST: $0**  
**🚀 READY TO TEST!**

Copy the database SQL, paste in Supabase, deploy to Render, and you're LIVE! 🎉
