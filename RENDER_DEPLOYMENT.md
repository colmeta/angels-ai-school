# 🚀 Complete Render Deployment Guide

**Platform**: Angels AI School Management System  
**Last Updated**: 2025-11-07  
**Deployment Target**: Render.com  
**Time to Deploy**: 15-20 minutes

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deploy (One-Click)](#quick-deploy-one-click)
3. [Manual Deploy (Step-by-Step)](#manual-deploy-step-by-step)
4. [Environment Variables Setup](#environment-variables-setup)
5. [Database Setup](#database-setup)
6. [Frontend Deployment](#frontend-deployment)
7. [Post-Deployment Testing](#post-deployment-testing)
8. [Custom Domain Setup](#custom-domain-setup)
9. [Monitoring & Logs](#monitoring--logs)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- ✅ GitHub account
- ✅ Render account (free - sign up at [render.com](https://render.com))
- ✅ This repository pushed to GitHub
- ✅ Clarity Engine API key

### Recommended
- ✅ Custom domain (optional)
- ✅ Mobile Money API keys (MTN, Airtel)
- ✅ Africa's Talking API key
- ✅ SendGrid API key
- ✅ Google Cloud service account JSON

---

## Quick Deploy (One-Click)

### Method 1: Deploy to Render Button

1. **Click the deploy button** in README.md:
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

2. **Connect GitHub**:
   - Authorize Render to access your repository
   - Select the `angels-ai-school` repository

3. **Configure Services**:
   Render will automatically create:
   - PostgreSQL database (1GB free tier)
   - Backend API service
   - Auto-scaling enabled

4. **Set Environment Variables**:
   - Click on the created service
   - Go to "Environment" tab
   - Add variables from [Environment Variables Guide](ENVIRONMENT_VARIABLES.md)
   - **CRITICAL REQUIRED**:
     ```
     DATABASE_URL=auto-populated
     JWT_SECRET_KEY=generate-strong-key
     CLARITY_API_KEY=your-clarity-key
     CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com
     ```

5. **Deploy**:
   - Click "Deploy"
   - Wait 5-10 minutes for build
   - Backend will be live at `https://your-app.onrender.com`

6. **Run Migrations**:
   - Go to "Shell" tab in Render dashboard
   - Run: `python run_migrations.py`

---

## Manual Deploy (Step-by-Step)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Verify email

### Step 2: Create PostgreSQL Database

1. **Dashboard** → **New** → **PostgreSQL**
2. **Configure**:
   - Name: `angels-ai-db`
   - Database: `angels_ai`
   - User: `angels_ai_user`
   - Region: Oregon (US West) or Frankfurt (EU)
   - Plan: **Free** (1GB storage)
3. Click **Create Database**
4. Wait 2-3 minutes for provisioning
5. **Save the Internal Database URL** (starts with `postgresql://...`)

### Step 3: Create Backend API Service

1. **Dashboard** → **New** → **Web Service**
2. **Connect Repository**:
   - Click "Connect account" (GitHub)
   - Select `angels-ai-school` repository
3. **Configure Service**:
   ```
   Name: angels-ai-backend
   Region: Oregon (same as database)
   Branch: main (or your working branch)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   Plan: Free (or Starter $7/month for better performance)
   ```
4. **Advanced Settings**:
   - Health Check Path: `/api/health`
   - Auto-Deploy: Yes

### Step 4: Set Environment Variables

In the backend service, go to **Environment** tab:

#### CRITICAL (Required)
```bash
DATABASE_URL=<paste-internal-database-url-from-step-2>
JWT_SECRET_KEY=<generate-random-key>
CLARITY_API_KEY=<your-clarity-key>
CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com
```

Generate JWT key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### RECOMMENDED (For Full Features)
```bash
# Mobile Money
MTN_MOBILE_MONEY_API_KEY=<your-mtn-key>
MTN_MOBILE_MONEY_BASE_URL=https://api.mtn.com/mobilemoney
AIRTEL_MOBILE_MONEY_API_KEY=<your-airtel-key>
AIRTEL_MOBILE_MONEY_BASE_URL=https://openapi.airtel.africa/mobile-money

# Notifications
AFRICAS_TALKING_API_KEY=<your-at-key>
AFRICAS_TALKING_USERNAME=sandbox
AFRICAS_TALKING_SENDER_ID=AngelsAI
SENDGRID_API_KEY=<your-sendgrid-key>
SENDGRID_FROM_EMAIL=noreply@your-domain.com

# OCR
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/google-credentials.json
```

#### OPTIONAL
```bash
# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Branding
DEFAULT_BRAND_NAME=Angels AI School
DEFAULT_BRAND_PRIMARY_COLOR=#0B69FF
DEFAULT_BRAND_ACCENT_COLOR=#FFB400

# Feature Flags
ENABLE_BACKGROUND_SYNC=true
ENABLE_PARENT_CHATBOT=true
ENABLE_MOBILE_MONEY=true
```

### Step 5: Add Google Cloud Credentials (If Using OCR)

1. In backend service, go to **Environment** tab
2. Click "Add from .env"
3. Create **Secret File**:
   - Key: `google-credentials.json`
   - Value: Paste entire JSON content from Google service account
4. Set environment variable:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/google-credentials.json
   ```

### Step 6: Deploy Backend

1. Click **"Create Web Service"** or **"Manual Deploy"**
2. Render will:
   - Clone repository
   - Install dependencies (`pip install -r requirements.txt`)
   - Start server (`uvicorn api.main:app ...`)
3. Wait 5-10 minutes for first deploy
4. Check logs for errors
5. Backend URL: `https://angels-ai-backend.onrender.com`

### Step 7: Run Database Migrations

**Option A: Using Render Shell**
1. Go to backend service → **Shell** tab
2. Run:
   ```bash
   python run_migrations.py
   ```
3. Verify: You should see "✅ Migration 001_initial_schema.sql executed successfully" etc.

**Option B: Using Local Connection**
1. Copy external database URL from Render dashboard
2. Run locally:
   ```bash
   export DATABASE_URL="<external-database-url>"
   python run_migrations.py
   ```

### Step 8: Verify Backend

1. Open `https://angels-ai-backend.onrender.com/`
2. You should see:
   ```json
   {
     "message": "Angels AI School API",
     "version": "1.0.0",
     "status": "operational"
   }
   ```
3. Check API docs: `https://angels-ai-backend.onrender.com/docs`

---

## Frontend Deployment

### Option 1: Deploy with Backend (Recommended)

Frontend is served by FastAPI backend automatically.

1. Build frontend locally:
   ```bash
   cd webapp
   npm install
   npm run build
   ```
2. Commit `webapp/dist` to repository
3. Backend serves static files from `/`
4. Frontend URL: `https://angels-ai-backend.onrender.com/`

### Option 2: Separate Frontend Service

1. **Dashboard** → **New** → **Static Site**
2. **Configure**:
   ```
   Name: angels-ai-frontend
   Branch: main
   Build Command: cd webapp && npm install && npm run build
   Publish Directory: webapp/dist
   ```
3. **Environment Variables**:
   ```
   VITE_API_URL=https://angels-ai-backend.onrender.com
   ```
4. Deploy
5. Frontend URL: `https://angels-ai-frontend.onrender.com`

---

## Environment Variables Setup

### Complete List for Render

Go to backend service → **Environment** tab → **Add Environment Variable**:

```bash
# === REQUIRED ===
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-strong-random-key-here
CLARITY_API_KEY=your-clarity-key
CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com

# === RECOMMENDED (Mobile Money) ===
MTN_MOBILE_MONEY_API_KEY=your-mtn-key
MTN_MOBILE_MONEY_BASE_URL=https://api.mtn.com/mobilemoney
MTN_SUBSCRIPTION_KEY=your-mtn-subscription-key
AIRTEL_MOBILE_MONEY_API_KEY=your-airtel-key
AIRTEL_MOBILE_MONEY_BASE_URL=https://openapi.airtel.africa/mobile-money
AIRTEL_CLIENT_ID=your-airtel-client-id
AIRTEL_CLIENT_SECRET=your-airtel-client-secret

# === RECOMMENDED (Notifications) ===
AFRICAS_TALKING_API_KEY=your-at-key
AFRICAS_TALKING_USERNAME=your-username
AFRICAS_TALKING_SENDER_ID=AngelsAI
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=noreply@your-domain.com
SENDGRID_FROM_NAME=Angels AI School
VAPID_PUBLIC_KEY=your-vapid-public
VAPID_PRIVATE_KEY=your-vapid-private
VAPID_EMAIL=admin@your-domain.com

# === RECOMMENDED (OCR) ===
GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/google-credentials.json

# === OPTIONAL (Token Config) ===
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# === OPTIONAL (Fallback AI) ===
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key

# === OPTIONAL (External Chatbot) ===
CHATBOT_API_KEY=your-chatbot-key
CHATBOT_API_BASE_URL=https://your-chatbot.com/api

# === OPTIONAL (Cloud Storage) ===
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
AWS_BUCKET_NAME=angels-ai-uploads

# === OPTIONAL (Branding Defaults) ===
DEFAULT_BRAND_NAME=Angels AI School
DEFAULT_BRAND_PRIMARY_COLOR=#0B69FF
DEFAULT_BRAND_ACCENT_COLOR=#FFB400
DEFAULT_BRAND_LOGO_URL=https://your-domain.com/logo.png

# === OPTIONAL (Feature Flags) ===
ENABLE_BACKGROUND_SYNC=true
ENABLE_PARENT_CHATBOT=true
ENABLE_MOBILE_MONEY=true
ENABLE_SMS_NOTIFICATIONS=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_PHOTO_UPLOAD=true
ENABLE_OFFLINE_MODE=true
```

---

## Database Setup

### Initial Schema Creation

After deploying backend, run migrations:

```bash
# In Render Shell
python run_migrations.py
```

This creates:
- 25 database tables
- All indexes
- All constraints
- Triggers for updated_at

### Seed Data (Optional)

Create initial school and admin user:

```bash
# In Render Shell or local
python seed_data.py
```

This creates:
- Demo school
- Admin user (admin@school.com / admin123)
- Sample students, teachers, parents

### Database Backups

Render automatically backs up:
- **Free tier**: Daily backups, 7-day retention
- **Paid tier**: Daily backups, 30-day retention

Manual backup:
```bash
# From Render dashboard
pg_dump $DATABASE_URL > backup.sql
```

---

## Post-Deployment Testing

### 1. Health Check

```bash
curl https://your-app.onrender.com/api/health
```

Expected:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T12:00:00Z"
}
```

### 2. API Documentation

Visit: `https://your-app.onrender.com/docs`

Should see Swagger UI with all endpoints.

### 3. Authentication Test

```bash
# Register user
curl -X POST https://your-app.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "school_id": "demo-school-id",
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "role": "admin"
  }'

# Login
curl -X POST https://your-app.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 4. Clarity Engine Test

```bash
curl -X POST https://your-app.onrender.com/api/clarity/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Test the Clarity Engine integration",
    "domain": "education"
  }'
```

### 5. Frontend Test

1. Visit `https://your-app.onrender.com/`
2. Check if homepage loads
3. Test navigation to different pages
4. Try "Add to Home Screen" on mobile

---

## Custom Domain Setup

### Step 1: Add Domain to Render

1. Go to backend service → **Settings** → **Custom Domains**
2. Click **Add Custom Domain**
3. Enter your domain (e.g., `school.yourdomain.com`)
4. Render provides DNS records:
   ```
   Type: CNAME
   Name: school
   Value: your-app.onrender.com
   ```

### Step 2: Update DNS

At your domain registrar (Cloudflare, Namecheap, GoDaddy):
1. Add CNAME record from Render
2. Wait 5-60 minutes for DNS propagation

### Step 3: Enable HTTPS

Render automatically provisions SSL certificate (Let's Encrypt).

### Step 4: Update Frontend Environment

If frontend is separate:
```bash
# In frontend service environment
VITE_API_URL=https://school.yourdomain.com
```

---

## Monitoring & Logs

### View Logs

1. **Real-time logs**:
   - Render dashboard → Service → **Logs** tab
   - Auto-refreshes

2. **Download logs**:
   ```bash
   # Using Render CLI
   render logs <service-id>
   ```

### Metrics

Free tier includes:
- CPU usage
- Memory usage
- Request count
- Response time
- Error rate

### Alerts

Set up in **Settings** → **Alerts**:
- Deploy failures
- High error rate
- Service crashes

### Health Monitoring

Endpoint: `/api/health`

Render pings every 60 seconds.
If unhealthy:
- Service restarts automatically
- Alert sent to email

---

## Troubleshooting

### Build Failed

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
1. Check `requirements.txt` includes all dependencies
2. Rebuild: `pip freeze > requirements.txt`
3. Commit and push

**Error**: `Error installing crewai`

**Solution**:
```bash
# In requirements.txt
crewai[tools]>=0.203.0  # Ensure this exact format
```

### Database Connection Failed

**Error**: `could not connect to server`

**Solution**:
1. Check `DATABASE_URL` is set correctly
2. Use **Internal Database URL** (not External)
3. Verify database is in same region as service

### Migrations Failed

**Error**: `relation "schools" already exists`

**Solution**:
1. Drop and recreate database (dev only):
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```
2. Run migrations again

### JWT Token Invalid

**Error**: `Invalid token`

**Solution**:
1. Check `JWT_SECRET_KEY` is set
2. Ensure key hasn't changed (invalidates all tokens)
3. Generate new strong key

### Clarity API Not Responding

**Error**: `Connection timeout to Clarity Engine`

**Solution**:
1. Check `CLARITY_BASE_URL` is correct
2. Verify Clarity Engine is running:
   ```bash
   curl https://veritas-engine-zae0.onrender.com/instant/health
   ```
3. Check API key is valid

### Mobile Money Not Working

**Error**: `MTN API authentication failed`

**Solution**:
1. Verify API keys are correct
2. Check subscription is active
3. Ensure environment variables are set:
   - `MTN_MOBILE_MONEY_API_KEY`
   - `MTN_SUBSCRIPTION_KEY`

### Out of Memory

**Error**: `Worker killed (out of memory)`

**Solution**:
1. Upgrade to Starter plan ($7/month) - 512MB RAM
2. Or optimize queries:
   ```python
   # Add indexes, limit query results
   ```

### Slow Performance

**Issues**:
- Requests taking >5 seconds
- Database queries slow

**Solutions**:
1. Upgrade database to paid tier (better performance)
2. Add database indexes (check `migrations/*.sql`)
3. Enable query caching
4. Upgrade service to Starter plan

### Frontend Not Loading

**Error**: `Failed to load resource: net::ERR_CONNECTION_REFUSED`

**Solution**:
1. Check `VITE_API_URL` in frontend environment
2. Verify CORS is enabled in backend
3. Check backend is deployed and running
4. Try rebuilding frontend:
   ```bash
   cd webapp && npm run build
   ```

---

## Production Checklist

### Before Launch

- [ ] Database backed up
- [ ] All environment variables set (especially JWT_SECRET_KEY)
- [ ] Migrations run successfully
- [ ] Health endpoint returns 200
- [ ] API docs accessible at /docs
- [ ] Frontend loads correctly
- [ ] Mobile Money tested (test transactions)
- [ ] SMS notifications tested
- [ ] Email notifications tested
- [ ] Photo upload tested (OCR working)
- [ ] User registration/login working
- [ ] All 9 AI agents tested
- [ ] Custom domain configured (if using)
- [ ] SSL certificate active
- [ ] Monitoring alerts set up

### After Launch

- [ ] Monitor error logs daily (first week)
- [ ] Check database size (upgrade if approaching limit)
- [ ] Monitor response times
- [ ] Set up regular backups (automated)
- [ ] Test mobile money transactions with real money
- [ ] Verify parent/teacher apps installable
- [ ] Check offline mode works
- [ ] Monitor Clarity API usage

---

## Cost Optimization

### Free Tier (Recommended for Testing)

- Database: 1GB storage
- Backend: 750 hours/month
- Frontend: Unlimited bandwidth
- **Total: $0/month**

### Starter Tier (Recommended for Production)

- Database: $7/month (10GB storage)
- Backend: $7/month (512MB RAM, always on)
- **Total: $14/month**

### Professional Tier (Large Schools)

- Database: $25/month (50GB storage, high availability)
- Backend: $25/month (2GB RAM, autoscaling)
- **Total: $50/month**

---

## Support & Resources

### Render Support
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Status: https://status.render.com

### Platform Support
- Email: nsubugacollin@gmail.com
- Docs: /COMPREHENSIVE_AUDIT.md
- Env Vars: /ENVIRONMENT_VARIABLES.md

### Community
- GitHub Issues: https://github.com/yourusername/angels-ai-school/issues

---

**Deployment Time**: 15-20 minutes  
**Cost**: Free tier available, $14/month recommended for production  
**Uptime**: 99.9% SLA (paid tiers)

🚀 **Ready to deploy!**

---

Last Updated: 2025-11-07  
Version: 1.0.0
