# ⚡ QUICK START - DEPLOY IN 30 MINUTES

**Follow these 5 steps to deploy Angels AI School Management Platform**

---

## STEP 1: CREATE RENDER DATABASE (5 minutes)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Settings:
   - Name: `angels-ai-db`
   - Database: `angels_ai_school`
   - Region: Frankfurt or Singapore
   - Plan: **Starter ($7/month)**
4. Click **"Create Database"**
5. **COPY** the **Internal Database URL** (starts with `postgres://`)

---

## STEP 2: CREATE RENDER WEB SERVICE (5 minutes)

1. Click **"New +"** → **"Web Service"**
2. Connect GitHub: `colmeta/angels-ai-school`
3. Settings:
   - Name: `angels-ai-backend`
   - Branch: `cursor/integrate-ai-agent-api-key-and-automate-services-ad91`
   - Runtime: **Python 3**
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Starter ($7/month)**
4. **DON'T DEPLOY YET!** Go to **Environment** tab first

---

## STEP 3: SET ENVIRONMENT VARIABLES (10 minutes)

In **Environment** tab, add these (minimum required):

```bash
# Database (from Step 1)
DATABASE_URL=postgres://...your-render-db-url...

# Generate these 2:
JWT_SECRET_KEY=PASTE_HERE_openssl_rand_hex_32
ENCRYPTION_KEY=PASTE_HERE_python_cryptography_fernet

# Clarity AI (already configured)
CLARITY_API_KEY=cp_live_demo_2024_clarity_pearl_ai_test_key_001
CLARITY_API_URL=https://veritas-engine-zae0.onrender.com

# App settings
DEFAULT_BRAND_NAME=Angels AI School
API_BASE_URL=https://angels-ai-backend.onrender.com
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate keys**:
```bash
# JWT Secret
openssl rand -hex 32

# Encryption Key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Optional (for notifications)**:
```bash
SENDGRID_API_KEY=your_key_here
AFRICAS_TALKING_API_KEY=your_key_here
MTN_MOMO_API_KEY=your_key_here
AIRTEL_MONEY_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
```

See `.env.production.render` for full list (40+ variables)

---

## STEP 4: DEPLOY & RUN MIGRATIONS (5 minutes)

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait for build to complete (~3-5 minutes)
3. Once live, click **"Shell"** tab
4. Run migrations:

```bash
python run_migrations.py
```

If that fails, run manually:
```bash
python -c "
import os
import psycopg2
from pathlib import Path

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

for migration in sorted(Path('migrations').glob('*.sql')):
    print(f'Running {migration.name}...')
    cursor.execute(migration.read_text())
    conn.commit()
    print(f'✅ {migration.name} complete')

cursor.close()
conn.close()
print('🎉 All migrations complete!')
"
```

---

## STEP 5: VERIFY DEPLOYMENT (5 minutes)

### A. Test Health Endpoint
```bash
curl https://angels-ai-backend.onrender.com/api/health
```

**Expected**:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"healthy": true},
    "clarity_api": {"healthy": true}
  }
}
```

### B. Test Chatbot
```bash
curl -X POST https://angels-ai-backend.onrender.com/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I pay fees?", "school_id": "test", "domain": "financial"}'
```

### C. View API Docs
Open: `https://angels-ai-backend.onrender.com/docs`

**Should see 200+ endpoints!** ✅

---

## 🎉 YOU'RE LIVE!

**Backend URL**: `https://angels-ai-backend.onrender.com`

**Cost**: $14/month (Database + Web Service)

**Next Steps**:
1. Deploy frontend (React PWA) to Render Static Site
2. Create test school account
3. Add test students
4. Start A/B testing!

---

## 🚨 TROUBLESHOOTING

### Health check returns 503
```bash
# Check logs
render logs -s angels-ai-backend

# Common fix: Missing DATABASE_URL or JWT_SECRET_KEY
```

### Migrations fail
```bash
# Check what ran
psql $DATABASE_URL -c "SELECT * FROM pg_tables WHERE schemaname = 'public'"

# Run specific migration
psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

### Clarity API timeout
```bash
# Normal on cold start - wait 30 seconds and retry
```

---

## 📞 SUPPORT

- **Render Docs**: https://render.com/docs
- **Full Guide**: `RENDER_PRODUCTION_DEPLOYMENT.md`
- **Env Vars**: `.env.production.render`
- **Complete Summary**: `MISSION_ACCOMPLISHED.md`

---

**🚀 DEPLOY NOW: 30 minutes to production!**
