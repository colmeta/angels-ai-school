# 🚀 RENDER PRODUCTION DEPLOYMENT GUIDE

**Complete step-by-step guide to deploy Angels AI School Management Platform to Render**

**Date**: 2025-11-09  
**Status**: ✅ READY FOR DEPLOYMENT  
**Free Tier**: ✅ Supported (with limitations)

---

## 📋 PRE-DEPLOYMENT CHECKLIST

- [x] ✅ All 39 features built and integrated
- [x] ✅ Clarity chatbot API integrated
- [x] ✅ Database backups configured
- [x] ✅ Encryption service implemented
- [x] ✅ Audit logging enabled
- [x] ✅ Production monitoring added
- [x] ✅ Critical SELECT * queries optimized
- [x] ✅ All migrations ready (012 migration files)
- [x] ✅ Requirements.txt updated
- [x] ✅ Procfile configured
- [x] ✅ Runtime specified (Python 3.11.8)

---

## 🎯 STEP 1: CREATE RENDER SERVICES

You need **2 services** on Render:

### A. PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `angels-ai-db`
   - **Database**: `angels_ai_school`
   - **User**: `angels_ai_user` (auto-generated)
   - **Region**: Choose closest to Uganda (Europe/Frankfurt or Singapore)
   - **Plan**: 
     - Free: $0/month (1 GB storage, expires after 90 days)
     - Starter: $7/month (10 GB, automated backups, PITR)
     - **RECOMMENDATION**: Start with Starter for A/B testing

4. Click "Create Database"
5. **SAVE** the Internal Database URL (starts with `postgres://`)

### B. Web Service (FastAPI Backend)

1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `colmeta/angels-ai-school`
3. Configure:
   - **Name**: `angels-ai-backend`
   - **Region**: Same as database
   - **Branch**: `cursor/integrate-ai-agent-api-key-and-automate-services-ad91`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: 
     - Free: $0/month (sleeps after 15 min inactivity, 750 hrs/month)
     - Starter: $7/month (always on, better performance)
     - **RECOMMENDATION**: Starter for production

4. Click "Create Web Service" (Don't deploy yet - set env vars first!)

---

## 🔐 STEP 2: CONFIGURE ENVIRONMENT VARIABLES

In your Render web service dashboard, go to **Environment** tab and add these variables:

### ✅ REQUIRED (Core System)

```bash
# Database
DATABASE_URL=<Your Render PostgreSQL Internal URL>

# Authentication (Generate secrets)
JWT_SECRET_KEY=<Generate with: openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Clarity AI Chatbot (Your API)
CLARITY_API_KEY=cp_live_demo_2024_clarity_pearl_ai_test_key_001
CLARITY_API_URL=https://veritas-engine-zae0.onrender.com

# App Settings
DEFAULT_BRAND_NAME=Angels AI School
API_BASE_URL=https://angels-ai-backend.onrender.com
FRONTEND_URL=https://your-frontend-app.onrender.com
```

### ⚠️ REQUIRED FOR A/B TESTING (Free Options Available)

```bash
# Email Notifications (SendGrid - Free 100 emails/day)
SENDGRID_API_KEY=<Get from https://sendgrid.com/free>
SENDGRID_FROM_EMAIL=noreply@your-school-domain.com

# SMS Notifications - Africa's Talking (Free sandbox)
AFRICAS_TALKING_API_KEY=<Get from https://africastalking.com>
AFRICAS_TALKING_USERNAME=<Your username>

# OR Twilio SMS (Free trial $15 credit)
# TWILIO_ACCOUNT_SID=<Your Twilio SID>
# TWILIO_AUTH_TOKEN=<Your Twilio token>
# TWILIO_PHONE_NUMBER=<Your Twilio number>

# Web Push Notifications (Free - generate keys)
VAPID_PUBLIC_KEY=<Generate with web-push library>
VAPID_PRIVATE_KEY=<Generate with web-push library>
VAPID_SUBJECT=mailto:admin@your-school-domain.com
```

### 🔒 SECURITY (Generate Before Real Data)

```bash
# Data Encryption (CRITICAL for health records)
ENCRYPTION_KEY=<Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

### 💰 PAYMENT GATEWAYS (For Fee Collection)

```bash
# MTN Mobile Money Uganda
MTN_MOMO_API_KEY=<Get from MTN MoMo API>
MTN_MOMO_USER_ID=<Your MTN user ID>
MTN_MOMO_SUBSCRIPTION_KEY=<Your subscription key>

# Airtel Money Uganda
AIRTEL_MONEY_API_KEY=<Get from Airtel Money API>
AIRTEL_MONEY_CLIENT_ID=<Your client ID>
AIRTEL_MONEY_CLIENT_SECRET=<Your client secret>
```

### 📸 OCR (Photo-based Data Entry)

```bash
# Google Cloud Vision API (Free 1000 requests/month)
GOOGLE_APPLICATION_CREDENTIALS_JSON=<Your service account JSON as string>
# OR
GOOGLE_CLOUD_PROJECT_ID=<Your project ID>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 📊 MONITORING (Optional - Free Tiers)

```bash
# Sentry Error Tracking (Free 5000 errors/month)
# SENTRY_DSN=<Get from https://sentry.io/signup/>

# Logging
LOG_LEVEL=INFO
```

### 🌐 MULTI-LLM FALLBACKS (Optional - You mentioned having these)

```bash
# LLM API Keys (Optional fallbacks to Clarity)
# ANTHROPIC_API_KEY=<Your Claude API key>
# GEMINI_API_KEY=<Your Gemini API key>
# GROQ_API_KEY=<Your Groq API key>
# OPENAI_API_KEY=<Your OpenAI key>
```

---

## 🗄️ STEP 3: RUN DATABASE MIGRATIONS

**Option A: Via Render Shell (Recommended)**

1. In Render dashboard, go to your web service
2. Click "Shell" tab
3. Run migrations:

```bash
# Install psycopg2 if needed
pip install psycopg2-binary

# Run all migrations
python -c "
import os
import psycopg2
from pathlib import Path

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Run each migration file
migrations = sorted(Path('migrations').glob('*.sql'))
for migration in migrations:
    print(f'Running {migration.name}...')
    cursor.execute(migration.read_text())
    conn.commit()
    print(f'✅ {migration.name} complete')

cursor.close()
conn.close()
print('🎉 All migrations complete!')
"
```

**Option B: Via Local psql Command**

```bash
# From your local machine
export DATABASE_URL="<Your Render PostgreSQL External URL>"

# Run migrations
for file in migrations/*.sql; do
    echo "Running $file..."
    psql $DATABASE_URL -f $file
done
```

**Option C: Use run_migrations.py Script**

```bash
# In Render shell
python run_migrations.py
```

---

## 🧪 STEP 4: VERIFY DEPLOYMENT

### A. Check Health Endpoint

```bash
curl https://angels-ai-backend.onrender.com/api/health
```

**Expected Response:**
```json
{
  "timestamp": "2025-11-09T...",
  "uptime_seconds": 45,
  "status": "healthy",
  "checks": {
    "database": {
      "healthy": true,
      "response_time_ms": 12.5,
      "status": "connected"
    },
    "clarity_api": {
      "healthy": true,
      "response_time_ms": 350.2,
      "status": "available"
    }
  }
}
```

### B. Test Clarity Chatbot

```bash
curl -X POST https://angels-ai-backend.onrender.com/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I check my child'\''s fee balance?",
    "school_id": "test-school-001",
    "user_role": "parent",
    "domain": "financial"
  }'
```

### C. Check API Documentation

Visit: `https://angels-ai-backend.onrender.com/docs`

Should show all 39 feature endpoints!

---

## 📦 STEP 5: SETUP DATABASE BACKUPS

### A. Run Backup Setup SQL

```bash
# In Render shell
psql $DATABASE_URL -f scripts/setup_database_backups.sql
```

### B. Configure Daily Backups (On Paid Plan)

**Render Starter Plan ($7/month) includes:**
- Automated daily backups
- 7-day retention
- Point-in-time recovery

**On Free Plan:**
- Run manual backups: `./scripts/backup_database.sh`
- Store locally or upload to S3

### C. Setup Cron Job (Optional - Requires Render Cron or external)

```yaml
# render-cron.yaml (if using Render Cron service)
jobs:
  - type: cronjob
    name: daily-backup
    schedule: "0 2 * * *"  # 2 AM daily
    command: "./scripts/backup_database.sh"
```

---

## 🎨 STEP 6: DEPLOY FRONTEND (React PWAs)

### A. Create Web Service for Frontend

1. Click "New +" → "Static Site"
2. Connect GitHub repo
3. Configure:
   - **Name**: `angels-ai-frontend`
   - **Build Command**: `cd webapp && npm install && npm run build`
   - **Publish Directory**: `webapp/dist`
   - **Plan**: Free (100 GB bandwidth/month)

### B. Add Environment Variables

```bash
VITE_API_BASE_URL=https://angels-ai-backend.onrender.com
VITE_VAPID_PUBLIC_KEY=<Your VAPID public key>
```

### C. Enable PWA Features

Already configured in `vite.config.ts`! PWA will work automatically.

---

## 🔥 STEP 7: A/B TESTING SETUP

### School 1: Control Group (Traditional Setup)
- Manual attendance
- Paper-based fees
- WhatsApp for communication

### School 2: Test Group (Full AI Platform)
- Photo-based attendance
- Mobile Money payments
- In-app chatbot
- AI-generated reports
- All 39 features enabled

### Metrics to Track

1. **Time Savings**
   - Attendance entry time
   - Report generation time
   - Parent communication time

2. **Accuracy**
   - Data entry errors
   - Fee collection accuracy
   - Attendance accuracy

3. **User Satisfaction**
   - Parent satisfaction scores
   - Teacher satisfaction scores
   - Admin satisfaction scores

4. **Cost Savings**
   - WhatsApp/SMS costs
   - Paper costs
   - Manual labor hours

### Monitoring Dashboard

Access at: `https://angels-ai-backend.onrender.com/api/metrics`

---

## 💰 COST BREAKDOWN

### Render Free Tier (MVP Testing)

| Service | Cost | Limitations |
|---------|------|-------------|
| PostgreSQL Free | $0 | 1 GB, 90 days expiry |
| Web Service Free | $0 | Sleeps after 15 min, 750 hrs/month |
| Static Site Free | $0 | 100 GB bandwidth |
| **TOTAL** | **$0/month** | ⚠️ **Not recommended for production** |

### Render Starter (Recommended for A/B Testing)

| Service | Cost | Features |
|---------|------|----------|
| PostgreSQL Starter | $7 | 10 GB, backups, PITR |
| Web Service Starter | $7 | Always on, better performance |
| Static Site Free | $0 | 100 GB bandwidth |
| **TOTAL** | **$14/month** | ✅ **Production-ready** |

### External Services (Free Tiers)

| Service | Free Tier | Use Case |
|---------|-----------|----------|
| SendGrid | 100 emails/day | Parent notifications |
| Africa's Talking | Sandbox | SMS testing |
| Google Cloud Vision | 1000 requests/month | OCR/Photo processing |
| Sentry | 5000 errors/month | Error monitoring |
| **TOTAL** | **$0/month** | Sufficient for A/B testing (2 schools) |

### **Grand Total for A/B Testing: $14/month** 🎯

---

## 🚨 TROUBLESHOOTING

### Issue 1: Database Connection Fails

**Solution**:
```bash
# Check DATABASE_URL is set correctly
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue 2: Clarity API Timeout

**Solution**:
```bash
# Clarity API can be slow on cold start
# Increase timeout in api/services/chatbot.py
self.timeout = 60.0  # Increase from 30 to 60
```

### Issue 3: Migration Fails

**Solution**:
```bash
# Check which migration failed
psql $DATABASE_URL -c "SELECT * FROM schema_migrations"

# Run failed migration manually
psql $DATABASE_URL -f migrations/XXX_failed_migration.sql
```

### Issue 4: Health Check Returns 503

**Solution**:
```bash
# Check Render logs
render logs -s angels-ai-backend

# Common cause: Missing env vars
# Verify all REQUIRED env vars are set
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

After deployment, verify:

- [ ] ✅ `/api/health` returns "healthy"
- [ ] ✅ `/api/chatbot/message` works
- [ ] ✅ `/docs` shows all 39 features
- [ ] ✅ Database migrations completed
- [ ] ✅ Can create a school
- [ ] ✅ Can create a user
- [ ] ✅ Can login
- [ ] ✅ Can upload a photo (OCR test)
- [ ] ✅ Can make a payment (Mobile Money test)
- [ ] ✅ Can send a notification

---

## 🎯 READY FOR A/B TESTING

Once all checklist items pass:

1. ✅ Deploy to Render ($14/month)
2. ✅ Onboard School 1 (Control)
3. ✅ Onboard School 2 (Test with AI)
4. ✅ Track metrics for 4-8 weeks
5. ✅ Analyze results
6. ✅ Iterate based on feedback
7. ✅ Scale to more schools

---

## 📞 SUPPORT

**Render Issues**: https://render.com/docs/troubleshooting  
**Clarity API**: nsubugacollin@gmail.com  
**Platform Issues**: Check logs via `render logs -s angels-ai-backend`

---

## 🚀 WHAT'S NEXT

After successful A/B testing:

1. **Scale Infrastructure**: Upgrade to Pro plan ($25/month per service)
2. **Add CDN**: For faster global access
3. **Enable Auto-scaling**: Handle 10+ schools
4. **Setup CI/CD**: Automated deployments
5. **Add Monitoring**: Full observability stack
6. **Implement Caching**: Redis for performance
7. **Multi-region Deployment**: Serve from multiple locations

---

**🎉 YOU'RE READY TO DEPLOY!**

Run `git push` and your Render services will auto-deploy. Check logs for any issues.

**Good luck with your A/B testing! 🚀**
