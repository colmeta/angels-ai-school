# Angels AI School - Environment Configuration

## Frontend (.env)
# Copy this to angels-ai-school/webapp/.env

# AI Mode (core, hybrid, or flash)
VITE_AI_MODE=hybrid
VITE_AI_DEFAULT_MODE=hybrid

# Supabase Configuration (for auth and metadata)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Cloudflare R2 Configuration (10GB Free Tier)
VITE_R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
VITE_R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
VITE_R2_BUCKET=angels-ai-results
VITE_R2_ACCESS_KEY_ID=your-access-key
VITE_R2_SECRET_ACCESS_KEY=your-secret-key

# Cloud AI Fallback (Flash Mode - Optional)
# Users can provide their own API keys
VITE_ALLOW_CLOUD_FALLBACK=true
VITE_CLOUD_FALLBACK_DEFAULT=false

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id

# Application
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Angels AI School

---

## Backend (.env)
# Copy this to angels-ai-school/api/.env

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/angels_ai
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here

# Cloudflare R2 (Backend Access)
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET=angels-ai-results

# JWT Secret
JWT_SECRET=your-ultra-secure-secret-key-256-bit

# WhatsApp Business API (Optional - for messaging)
WHATSAPP_API_KEY=optional
WHATSAPP_PHONE_NUMBER_ID=optional

# SMS Provider (Optional - for messaging)
AFRICA_TALKING_API_KEY=optional
AFRICA_TALKING_USERNAME=optional

---

## Setup Instructions

### 1. Cloudflare R2 (Free Tier - 10GB Storage, 1M requests/month)

1. Sign up at https://dash.cloudflare.com/
2. Go to R2 Object Storage
3. Create bucket: `angels-ai-results`
4. Generate API tokens
5. Update .env with credentials

**Benefits:**
- 10GB free storage (enough for 50,000+ schools)
- 1M free requests/month
- No egress fees
- S3-compatible API

### 2. Supabase (Free Tier - 500MB Database, 1GB bandwidth)

1. Sign up at https://supabase.com/
2. Create new project
3. Copy Project URL and Anon Key
4. Update .env

**Benefits:**
- PostgreSQL database
- Authentication built-in
- Realtime subscriptions
- Row Level Security

### 3. Google OAuth

1. Go to https://console.cloud.google.com/
2. Create OAuth 2.0 Client ID
3. Add authorized origins
4. Copy Client ID

---

## Cost Analysis

### Free Tier Limits

**Cloudflare R2:**
- Storage: 10 GB (enough for ~50,000 schools @ 200KB avg)
- Class A Operations: 1M/month (writes)
- Class B Operations: 10M/month (reads)
- Cost: $0

**Supabase:**
- Database: 500 MB
- Bandwidth: 1 GB/month
- Realtime: Unlimited connections
- Cost: $0

**Total Monthly Cost:**
- Infrastructure: $0
- API calls (optional): ~$0-10 if Flash fallback used
- WhatsApp/SMS (optional): ~$0.01-0.05 per message

---

## Scaling Plan

### When Free Tier Is Exceeded

**Option 1: Optimize Data**
- Prune old AI results (>90 days)
- Compress JSON storage
- Implement aggressive caching

**Option 2: Multi-Tenancy**
- Each school gets own R2 namespace
- They manage their own quota
- Federation model

**Option 3: Paid Tier (Revenue-Funded)**
- R2: $0.015/GB after 10GB
- Supabase Pro: $25/month for 8GB database
- Funded by grants/government partnerships

---

## Production Deployment

### Frontend (Vercel)
```bash
cd angels-ai-school/webapp
vercel --prod
```

### Backend (Render/Railway)
```bash
cd angels-ai-school/api
# Deploy to Render.com (free tier: 512MB RAM)
```

---

## Security

- All API keys in environment variables (never commit)
- JWT tokens for authentication
- R2 buckets with IAM policies
- Supabase Row Level Security (RLS)
- HTTPS only in production
