# 🔐 Complete Environment Variables Guide

**Last Updated**: 2025-11-07
**Platform**: Angels AI School Management System

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Core Variables (REQUIRED)](#core-variables-required)
3. [Authentication (REQUIRED)](#authentication-required)
4. [AI Engine (REQUIRED)](#ai-engine-required)
5. [Mobile Money (RECOMMENDED)](#mobile-money-recommended)
6. [Notifications (RECOMMENDED)](#notifications-recommended)
7. [OCR Services (RECOMMENDED)](#ocr-services-recommended)
8. [Optional Integrations](#optional-integrations)
9. [Branding & Features](#branding--features)
10. [Production Checklist](#production-checklist)
11. [Cost Breakdown](#cost-breakdown)

---

## Quick Start

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Fill in REQUIRED variables (marked with ⚠️)
3. Add RECOMMENDED variables for full features
4. Keep OPTIONAL variables blank unless needed

---

## Core Variables (REQUIRED)

### Database
**Variable**: `DATABASE_URL`  
**Required**: ⚠️ YES  
**Format**: `postgresql://user:password@host:port/database`  
**Cost**: FREE (with free tier providers)  
**Examples**:
```bash
# Local development
DATABASE_URL=postgresql://localhost:5432/angels_ai

# Render PostgreSQL
DATABASE_URL=postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/angels_ai

# Supabase
DATABASE_URL=postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres

# Heroku Postgres
DATABASE_URL=postgres://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/dbname
```

**Setup**:
- **Render**: Create PostgreSQL database (free tier: 1GB)
- **Supabase**: Create project (free tier: 500MB)
- **Local**: `createdb angels_ai`

---

## Authentication (REQUIRED)

### JWT Secret Key
**Variable**: `JWT_SECRET_KEY`  
**Required**: ⚠️ YES  
**Format**: Random 32+ character string  
**Cost**: FREE  
**Example**:
```bash
JWT_SECRET_KEY=your-super-secret-key-change-in-production-use-random-64-chars
```

**Generate**:
```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Token Expiration
**Variable**: `ACCESS_TOKEN_EXPIRE_MINUTES`  
**Required**: NO  
**Default**: 60  
**Cost**: FREE  
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Variable**: `REFRESH_TOKEN_EXPIRE_DAYS`  
**Required**: NO  
**Default**: 30  
**Cost**: FREE  
```bash
REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

## AI Engine (REQUIRED)

### Clarity Engine (Primary)
**Variable**: `CLARITY_API_KEY`  
**Required**: ⚠️ YES (you own this)  
**Cost**: FREE (your own API)  
```bash
CLARITY_API_KEY=your-clarity-key
CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com
```

### Fallback LLM Keys (Optional)
**Variables**:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`

**Required**: NO  
**Cost**: Pay-per-use (only if used)  
**Recommendation**: Keep blank, Clarity is primary

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

---

## Mobile Money (RECOMMENDED)

### MTN Mobile Money
**Variables**:
```bash
MTN_MOBILE_MONEY_API_KEY=your-mtn-api-key
MTN_MOBILE_MONEY_BASE_URL=https://api.mtn.com/mobilemoney
MTN_SUBSCRIPTION_KEY=your-subscription-key
```

**Required**: NO (but recommended for Uganda)  
**Cost**: FREE API (transaction fees apply)  
**Setup**:
1. Go to https://momodeveloper.mtn.com/
2. Register account
3. Create subscription
4. Get API key + Subscription key

### Airtel Money
**Variables**:
```bash
AIRTEL_MOBILE_MONEY_API_KEY=your-airtel-api-key
AIRTEL_MOBILE_MONEY_BASE_URL=https://openapi.airtel.africa/mobile-money
AIRTEL_CLIENT_ID=your-client-id
AIRTEL_CLIENT_SECRET=your-client-secret
```

**Required**: NO (but recommended for Uganda)  
**Cost**: FREE API (transaction fees apply)  
**Setup**:
1. Contact Airtel Business: business@airtel.ug
2. Request API access
3. Get credentials

---

## Notifications (RECOMMENDED)

### Africa's Talking (Primary SMS for Africa)
**Variables**:
```bash
AFRICAS_TALKING_API_KEY=your-api-key
AFRICAS_TALKING_USERNAME=sandbox  # or your username
AFRICAS_TALKING_SENDER_ID=AngelsAI
```

**Required**: NO (but recommended)  
**Cost**: 
- FREE tier: 100 SMS for testing
- Paid: ~$0.01 per SMS in Uganda
**Setup**:
1. Go to https://africastalking.com/
2. Create account
3. Get API key from dashboard
4. Start with sandbox for free testing

### Twilio (Backup SMS)
**Variables**:
```bash
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

**Required**: NO  
**Cost**: 
- FREE trial: $15 credit
- Paid: ~$0.0075 per SMS
**Setup**:
1. Go to https://www.twilio.com/
2. Sign up for trial
3. Get credentials from console

### SendGrid (Email)
**Variables**:
```bash
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@your-domain.com
SENDGRID_FROM_NAME=Angels AI School
```

**Required**: NO  
**Cost**: FREE tier (100 emails/day)  
**Setup**:
1. Go to https://sendgrid.com/
2. Create account
3. Create API key
4. Verify sender email

### Web Push Notifications (VAPID)
**Variables**:
```bash
VAPID_PUBLIC_KEY=your-public-key
VAPID_PRIVATE_KEY=your-private-key
VAPID_EMAIL=admin@your-domain.com
```

**Required**: NO  
**Cost**: FREE  
**Generate**:
```bash
# Using web-push library
npx web-push generate-vapid-keys
```

---

## OCR Services (RECOMMENDED)

### Google Cloud Vision (Primary OCR)
**Variable**: `GOOGLE_APPLICATION_CREDENTIALS`  
**Required**: NO (but highly recommended)  
**Cost**: 
- FREE tier: 1,000 images/month
- Paid: $1.50 per 1,000 images
**Format**: Path to service account JSON file

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Setup**:
1. Go to https://console.cloud.google.com/
2. Create project
3. Enable Cloud Vision API
4. Create service account
5. Download JSON key
6. Upload to server and set path

**Alternative** (for Render/cloud deployment):
```bash
# Base64 encode the JSON and store inline
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

---

## Optional Integrations

### External Chatbot (If not using Clarity)
**Variables**:
```bash
CHATBOT_API_KEY=your-chatbot-key
CHATBOT_API_BASE_URL=https://your-chatbot-provider.com/api
```

**Required**: NO  
**Cost**: Varies by provider  
**Note**: Platform uses Clarity by default

### Cloud Storage (AWS S3)
**Variables**:
```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=angels-ai-uploads
```

**Required**: NO  
**Cost**: FREE tier (5GB)  
**Use Case**: Store uploaded photos/documents

---

## Branding & Features

### Default Branding
**Variables**:
```bash
DEFAULT_BRAND_NAME=Angels AI School
DEFAULT_BRAND_PRIMARY_COLOR=#0B69FF
DEFAULT_BRAND_ACCENT_COLOR=#FFB400
DEFAULT_BRAND_LOGO_URL=https://example.com/logo.png
```

**Required**: NO  
**Cost**: FREE  
**Note**: Per-school branding stored in database overrides these

### Feature Flags
**Variables**:
```bash
ENABLE_BACKGROUND_SYNC=true
ENABLE_PARENT_CHATBOT=true
ENABLE_MOBILE_MONEY=true
ENABLE_SMS_NOTIFICATIONS=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_PHOTO_UPLOAD=true
ENABLE_OFFLINE_MODE=true
```

**Required**: NO  
**Cost**: FREE  
**Note**: Per-school flags in database override these

---

## Production Checklist

### ⚠️ CRITICAL (Must Change)

- [ ] `JWT_SECRET_KEY` - Generate strong random key
- [ ] `DATABASE_URL` - Use production database (not localhost)
- [ ] `CLARITY_API_KEY` - Your production Clarity key

### ✅ RECOMMENDED (Add for Full Features)

- [ ] `MTN_MOBILE_MONEY_API_KEY` - Enable mobile money
- [ ] `AIRTEL_MOBILE_MONEY_API_KEY` - Enable mobile money
- [ ] `AFRICAS_TALKING_API_KEY` - Enable SMS notifications
- [ ] `SENDGRID_API_KEY` - Enable email notifications
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Enable photo OCR

### 🔧 OPTIONAL (Add if Needed)

- [ ] `TWILIO_ACCOUNT_SID` - Backup SMS
- [ ] `VAPID_PUBLIC_KEY` - Web push notifications
- [ ] `OPENAI_API_KEY` - Fallback AI (if Clarity down)
- [ ] `AWS_ACCESS_KEY_ID` - Cloud storage

---

## Cost Breakdown

### 💰 FREE (Total: $0/month)

| Service | Tier | Limits |
|---------|------|--------|
| Database (Render) | Free | 1GB storage |
| Database (Supabase) | Free | 500MB storage |
| Clarity Engine | Free | Unlimited (your API) |
| SendGrid Email | Free | 100 emails/day |
| Google Cloud Vision | Free | 1,000 images/month |
| AWS S3 | Free | 5GB storage (first year) |

**Total: $0/month** for development & small schools

### 💵 PAID (Recommended for Production)

| Service | Cost | What You Get |
|---------|------|--------------|
| Database (Render) | $7/month | 10GB storage, better performance |
| Africa's Talking SMS | ~$10/month | 1,000 SMS in Uganda |
| MTN/Airtel Mobile Money | FREE API | Pay only transaction fees (~1%) |
| Google Cloud Vision | $15/month | 10,000 images |

**Total: ~$32/month** for production (100-500 students)

### 🚀 ENTERPRISE (Large Schools)

| Service | Cost | What You Get |
|---------|------|--------------|
| Database (Render) | $25/month | 50GB storage, high availability |
| Africa's Talking SMS | $50/month | 5,000 SMS |
| Google Cloud Vision | $50/month | 30,000 images |

**Total: ~$125/month** for large schools (1000+ students)

---

## Environment Variable Template

Copy this template to your `.env` file:

```bash
# ===================================
# REQUIRED - Must be set
# ===================================

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Authentication
JWT_SECRET_KEY=generate-a-strong-random-key-here

# Clarity Engine (Your AI)
CLARITY_API_KEY=your-clarity-key
CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com

# ===================================
# RECOMMENDED - For full features
# ===================================

# Mobile Money (Uganda)
MTN_MOBILE_MONEY_API_KEY=
MTN_MOBILE_MONEY_BASE_URL=https://api.mtn.com/mobilemoney
AIRTEL_MOBILE_MONEY_API_KEY=
AIRTEL_MOBILE_MONEY_BASE_URL=https://openapi.airtel.africa/mobile-money

# SMS & Email Notifications
AFRICAS_TALKING_API_KEY=
AFRICAS_TALKING_USERNAME=sandbox
AFRICAS_TALKING_SENDER_ID=AngelsAI
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@your-domain.com

# Web Push Notifications
VAPID_PUBLIC_KEY=
VAPID_PRIVATE_KEY=
VAPID_EMAIL=admin@your-domain.com

# OCR (Photo Processing)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# ===================================
# OPTIONAL - Advanced features
# ===================================

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Fallback AI (if Clarity down)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=

# External Chatbot (if not using Clarity)
CHATBOT_API_KEY=
CHATBOT_API_BASE_URL=

# Cloud Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_BUCKET_NAME=angels-ai-uploads

# Branding Defaults
DEFAULT_BRAND_NAME=Angels AI School
DEFAULT_BRAND_PRIMARY_COLOR=#0B69FF
DEFAULT_BRAND_ACCENT_COLOR=#FFB400
DEFAULT_BRAND_LOGO_URL=https://example.com/logo.png

# Feature Flags
ENABLE_BACKGROUND_SYNC=true
ENABLE_PARENT_CHATBOT=true
ENABLE_MOBILE_MONEY=true
ENABLE_SMS_NOTIFICATIONS=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_PHOTO_UPLOAD=true
ENABLE_OFFLINE_MODE=true
```

---

## Quick Setup Scripts

### Development (Minimal)
```bash
# Only what you NEED to start development
export DATABASE_URL="postgresql://localhost:5432/angels_ai"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export CLARITY_API_KEY="your-clarity-key"
export CLARITY_BASE_URL="https://veritas-engine-zae0.onrender.com"
```

### Production (Recommended)
```bash
# Full production setup
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export CLARITY_API_KEY="your-production-clarity-key"
export CLARITY_BASE_URL="https://veritas-engine-zae0.onrender.com"
export MTN_MOBILE_MONEY_API_KEY="your-mtn-key"
export AIRTEL_MOBILE_MONEY_API_KEY="your-airtel-key"
export AFRICAS_TALKING_API_KEY="your-at-key"
export SENDGRID_API_KEY="your-sendgrid-key"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

---

## Troubleshooting

### Error: "Database connection failed"
- Check `DATABASE_URL` format
- Ensure database exists
- Check firewall rules (production databases)
- Run `python run_migrations.py`

### Error: "Invalid JWT token"
- Check `JWT_SECRET_KEY` is set
- Ensure key hasn't changed (invalidates all tokens)
- Check token expiration settings

### Error: "Clarity API key invalid"
- Verify `CLARITY_API_KEY` is correct
- Check `CLARITY_BASE_URL` is accessible
- Test: `curl https://veritas-engine-zae0.onrender.com/instant/health`

### Mobile Money not working
- Verify API keys are correct
- Check you're using correct base URLs
- Ensure phone numbers are in correct format (+256...)
- Test with small amounts first

### SMS not sending
- Check Africa's Talking balance
- Verify `AFRICAS_TALKING_SENDER_ID` is approved
- Ensure phone numbers are in E.164 format

---

**Questions?**  
Email: nsubugacollin@gmail.com

**Last Updated**: 2025-11-07  
**Version**: 1.0.0
