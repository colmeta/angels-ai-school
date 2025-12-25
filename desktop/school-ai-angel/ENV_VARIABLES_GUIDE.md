# 🔐 ENVIRONMENT VARIABLES SETUP GUIDE

## 📋 QUICK CHECKLIST

You need accounts from:
- [ ] **Cloudflare** (R2 storage - 10GB free)
- [ ] **Supabase** (Database - 500MB free)
- [ ] **Google Cloud** (OAuth - free)

Total time: ~20 minutes
Total cost: **$0** (all free tiers)

---

## 1️⃣ CLOUDFLARE R2 SETUP (5 minutes)

### Step 1: Create Account
- Go to https://dash.cloudflare.com/sign-up
- Sign up (email verification required)
- Free tier: 10GB storage, 1M operations/month

### Step 2: Create R2 Bucket
1. In dashboard, click **R2** in sidebar
2. Click **Create bucket**
3. Bucket name: `angels-ai-results`
4. Location: **Automatic** (best performance)
5. Click **Create bucket**

### Step 3: Get API Tokens
1. Click **Manage R2 API Tokens**
2. Click **Create API token**
3. Token name: `angels-ai-production`
4. Permissions: **Object Read & Write**
5. Click **Create API token**
6. **SAVE THESE VALUES** (shown only once):
   - `Access Key ID`
   - `Secret Access Key`
   - `Account ID` (in dashboard URL: `dash.cloudflare.com/[ACCOUNT_ID]/r2`)
   - `Endpoint` (shown in token details)

### Your R2 Variables:
```bash
R2_ACCOUNT_ID=<your-cloudflare-account-id>
R2_ACCESS_KEY_ID=<your-access-key-from-step-3>
R2_SECRET_ACCESS_KEY=<your-secret-key-from-step-3>
R2_BUCKET=angels-ai-results
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
```

---

## 2️⃣ SUPABASE SETUP (5 minutes)

### Step 1: Create Project
- Go to https://supabase.com/dashboard
- Click **New project**
- Organization: Create new or select existing
- Project name: `angels-ai-school`
- Database password: **Generate strong password** (save it!)
- Region: **Choose closest to users** (e.g., South Africa for Africa)
- Pricing plan: **Free** (500MB database, 1GB bandwidth)
- Click **Create new project** (takes ~2 minutes)

### Step 2: Get API Keys
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (for frontend)
   - **service_role** key (for backend) - **Keep secret!**

### Your Supabase Variables:
```bash
# Frontend
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=<anon-public-key>

# Backend
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=<service-role-key>
DATABASE_URL=<shown in Settings → Database → Connection string>
```

---

## 3️⃣ GOOGLE OAUTH SETUP (10 minutes)

### Step 1: Create Project
1. Go to https://console.cloud.google.com/
2. Click **Select a project** → **New Project**
3. Project name: `Angels AI School`
4. Click **Create**

### Step 2: Configure OAuth Consent
1. Go to **APIs & Services** → **OAuth consent screen**
2. User Type: **External**
3. Click **Create**
4. Fill in:
   - App name: `Angels AI School`
   - User support email: Your email
   - Developer contact: Your email
5. Click **Save and Continue**
6. Scopes: Click **Save and Continue** (default is fine)
7. Test users: Add your email
8. Click **Save and Continue**

### Step 3: Create OAuth Client ID
1. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
2. Application type: **Web application**
3. Name: `Angels AI Production`
4. Authorized JavaScript origins:
   ```
   http://localhost:5173
   https://your-app.vercel.app
   ```
5. Authorized redirect URIs:
   ```
   http://localhost:5173/auth/callback
   https://your-app.vercel.app/auth/callback
   ```
6. Click **Create**
7. **SAVE** your `Client ID`

### Your Google OAuth Variable:
```bash
VITE_GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
```

---

## 4️⃣ GENERATE JWT SECRET

### Quick Generation:
```bash
# On your computer, run:
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

Or use online tool:
- https://generate-secret.vercel.app/64

### Your JWT Variable:
```bash
JWT_SECRET=<generated-64-character-hex-string>
```

---

## 5️⃣ COMPLETE ENVIRONMENT FILES

### Frontend: `angels-ai-school/webapp/.env`

```bash
# ============================================
# AI CONFIGURATION
# ============================================
VITE_AI_MODE=hybrid
VITE_AI_DEFAULT_MODE=hybrid
VITE_AI_SYNC_ENABLED=true
VITE_MAX_RAM_MB=512

# ============================================
# CLOUDFLARE R2 (Copy from Step 1)
# ============================================
VITE_R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
VITE_R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
VITE_R2_BUCKET=angels-ai-results
VITE_R2_ACCESS_KEY_ID=<your-r2-access-key>
VITE_R2_SECRET_ACCESS_KEY=<your-r2-secret-key>

# ============================================
# SUPABASE (Copy from Step 2)
# ============================================
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>

# ============================================
# GOOGLE OAUTH (Copy from Step 3)
# ============================================
VITE_GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com

# ============================================
# LANGUAGE SUPPORT
# ============================================
VITE_DEFAULT_LANGUAGE=en
VITE_SUPPORTED_LANGUAGES=en,lg,sw

# ============================================
# GENERAL
# ============================================
VITE_API_URL=https://your-backend.onrender.com
VITE_APP_NAME=Angels AI School
VITE_ENVIRONMENT=production
```

### Backend: `angels-ai-school/.env`

```bash
# ============================================
# DATABASE (Copy from Step 2)
# ============================================
DATABASE_URL=<supabase-connection-string>
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=<service-role-key>

# ============================================
# CLOUDFLARE R2 (Copy from Step 1)
# ============================================
R2_ACCOUNT_ID=<cloudflare-account-id>
R2_ACCESS_KEY_ID=<r2-access-key>
R2_SECRET_ACCESS_KEY=<r2-secret-key>
R2_BUCKET=angels-ai-results
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com

# ============================================
# JWT SECRET (Copy from Step 4)
# ============================================
JWT_SECRET=<generated-64-char-hex>

# ============================================
# MEMORY OPTIMIZATION (for Render 512MB)
# ============================================
WEB_CONCURRENCY=1
WORKERS=1
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
MAX_UPLOAD_SIZE_MB=2
PHOTO_QUALITY=85

# ============================================
# OPTIONAL SERVICES (Leave empty if not using)
# ============================================
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WHATSAPP_API_KEY=
AFRICA_TALKING_API_KEY=

# ============================================
# DEPLOYMENT
# ============================================
PORT=8000
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

---

## 6️⃣ VERIFY CONFIGURATION

### Test R2 Connection:
```bash
# In backend directory:
python -c "
import boto3
from botocore.client import Config

client = boto3.client(
    's3',
    endpoint_url='<your-r2-endpoint>',
    aws_access_key_id='<your-access-key>',
    aws_secret_access_key='<your-secret-key>',
    config=Config(signature_version='s3v4')
)

print(client.list_buckets())
"
```

### Test Supabase Connection:
```bash
# In webapp directory:
npm run dev
# Open browser, check Network tab for Supabase requests
```

---

## 7️⃣ DEPLOYMENT ENVIRONMENT VARIABLES

### Vercel (Frontend):
1. Go to https://vercel.com/new
2. Import your Git repository
3. Go to **Settings** → **Environment Variables**
4. Add ALL `VITE_*` variables from frontend `.env`

### Render (Backend):
1. Go to https://render.com/
2. Create **New Web Service**
3. Connect Git repository
4. In **Environment**, add ALL backend `.env` variables

---

## ✅ FINAL CHECKLIST

- [ ] Cloudflare R2 bucket created
- [ ] R2 API tokens generated
- [ ] Supabase project created
- [ ] Supabase API keys copied
- [ ] Google OAuth client created
- [ ] JWT secret generated
- [ ] Frontend `.env` file created
- [ ] Backend `.env` file created
- [ ] All variables copied correctly
- [ ] No placeholder values remaining
- [ ] Tested locally (`npm run dev`)
- [ ] Ready to deploy!

---

## 🆘 TROUBLESHOOTING

### "R2 Access Denied"
- Check endpoint URL format
- Verify API tokens are correct
- Ensure bucket name matches exactly

### "Supabase Connection Failed"
- Check Project URL is correct
- Verify anon key for frontend, service key for backend
- Ensure project is active (not paused)

### "Google OAuth Error"
- Add redirect URIs in Google Console
- Check Client ID is copied fully
- Clear browser cache

---

## 💰 COST SUMMARY

**Total Monthly Cost: $0**

- Cloudflare R2: $0 (10GB free)
- Supabase: $0 (500MB free)
- Google OAuth: $0 (unlimited)
- Vercel: $0 (free tier)
- Render: $0 (512MB free tier)

**When to Upgrade:**
- >10GB storage used
- >500MB database
- >100 concurrent users
- Mission-critical SLA needed

---

**You're ready to deploy! 🚀**
