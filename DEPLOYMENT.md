# Angels AI School Platform - Deployment Guide

Complete guide for deploying the full-stack platform to production.

## 🚀 Quick Deploy to Render

### Prerequisites
1. GitHub account with this repository
2. Render account (free tier works)
3. PostgreSQL database (Render provides free tier)

### Step 1: Database Setup

1. Create a PostgreSQL database on Render:
   - Go to Render Dashboard → New → PostgreSQL
   - Name: `angels-ai-school-db`
   - Region: Choose closest to your users (e.g., Frankfurt for Europe, Singapore for Africa/Asia)
   - Plan: Free (or paid for production)
   - Copy the **Internal Database URL** after creation

2. Run migrations:
```bash
# Set your database URL
export DATABASE_URL="postgresql://..."

# Run migrations
python run_migrations.py
```

Or use the Render Shell after deployment:
```bash
cd /opt/render/project/src
python run_migrations.py
```

### Step 2: Backend API Deployment

1. Create a new Web Service on Render:
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub repository
   - Configure:
     - **Name**: `angels-ai-school-api`
     - **Region**: Same as database
     - **Branch**: `main` or `cursor/integrate-ai-agent-api-key-and-automate-services-ad91`
     - **Root Directory**: Leave empty (or `.` )
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

2. Add Environment Variables:
```
DATABASE_URL=<your-render-postgres-internal-url>
CLARITY_API_KEY=<your-clarity-key>
CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com
DEFAULT_BRAND_NAME=Angels AI School
DEFAULT_BRAND_PRIMARY_COLOR=#0B69FF
DEFAULT_BRAND_ACCENT_COLOR=#FFB400
ENABLE_BACKGROUND_SYNC=true
ENABLE_PARENT_CHATBOT=true
```

Optional (add when ready):
```
OPENAI_API_KEY=<optional>
ANTHROPIC_API_KEY=<optional>
GEMINI_API_KEY=<optional>
GROQ_API_KEY=<optional>
MTN_MOBILE_MONEY_API_KEY=<when-ready>
MTN_MOBILE_MONEY_BASE_URL=https://api.mtn.com/mobilemoney
AIRTEL_MOBILE_MONEY_API_KEY=<when-ready>
AIRTEL_MOBILE_MONEY_BASE_URL=https://openapi.airtel.africa/mobile-money
CHATBOT_API_KEY=<when-ready>
CHATBOT_API_BASE_URL=<when-ready>
```

3. Deploy:
   - Click "Create Web Service"
   - Wait for build and deployment (2-5 minutes)
   - Your API will be live at: `https://angels-ai-school-api.onrender.com`

### Step 3: Frontend PWA Deployment

Option A: Deploy frontend to Render Static Site

1. Create a new Static Site on Render:
   - Go to Render Dashboard → New → Static Site
   - Connect your GitHub repository
   - Configure:
     - **Name**: `angels-ai-school-webapp`
     - **Root Directory**: `webapp`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `webapp/dist`

2. Add Environment Variable:
```
VITE_API_URL=https://angels-ai-school-api.onrender.com
```

3. Deploy and your PWA will be live!

Option B: Serve frontend from backend (simpler for single deployment)

Update `api/main.py` to serve static files:
```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="webapp/dist", html=True), name="static")
```

Build frontend first:
```bash
cd webapp
npm install
npm run build
```

Then deploy only the backend (it will serve both API and frontend).

### Step 4: Post-Deployment Setup

1. **Run Migrations** (if not done in Step 1):
   - Go to your Render service → Shell tab
   - Run: `python run_migrations.py`

2. **Create First School**:
```bash
# Using curl or Postman
curl -X POST https://angels-ai-school-api.onrender.com/api/schools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo School Uganda",
    "code": "DEMO001",
    "country": "Uganda",
    "email": "admin@demoschool.ug",
    "phone": "+256700000000"
  }'
```

3. **Test API Health**:
```bash
curl https://angels-ai-school-api.onrender.com/api/health
```

4. **Test Clarity Integration**:
```bash
curl -X POST https://angels-ai-school-api.onrender.com/api/clarity/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Test integration",
    "domain": "education"
  }'
```

### Step 5: Configure Custom Domain (Optional)

1. In Render Dashboard → Your Service → Settings
2. Add custom domain (e.g., `school.yourdomain.com`)
3. Update DNS records as instructed by Render
4. SSL certificate is automatic (Let's Encrypt)

## 🔒 Security Checklist

- ✅ All API keys stored as environment variables (never in code)
- ✅ Database uses internal URL (not public)
- ✅ CORS configured for your domain only
- ✅ Rate limiting enabled on sensitive endpoints
- ✅ SQL injection protection via parameterized queries
- ✅ Input validation on all endpoints

## 📊 Monitoring

1. **Render Dashboard** - Monitor service health, logs, metrics
2. **Database Metrics** - Track connections, query performance
3. **API Health Endpoint** - `/api/health` for uptime monitoring

## 🔄 CI/CD

Render auto-deploys on git push to connected branch:
- Push to `main` → automatic deployment
- Rollback available in Render dashboard
- View deployment logs in real-time

## 🚨 Troubleshooting

### "DATABASE_URL not set"
- Check environment variables in Render dashboard
- Ensure DATABASE_URL uses internal URL, not external

### "Module not found" errors
- Check `requirements.txt` has all dependencies
- Rebuild service in Render dashboard

### Migrations fail
- Connect to database directly: `psql $DATABASE_URL`
- Run migrations manually from Render Shell
- Check database logs for permission issues

### PWA not installing
- Ensure HTTPS is enabled (Render does this automatically)
- Check `manifest.webmanifest` is accessible
- Verify service worker registration in browser DevTools

### Mobile money not working
- Verify you've added MTN/Airtel API keys
- Check API base URLs are correct
- Test endpoints in Postman first

## 📱 Mobile Money Setup

### MTN Mobile Money

1. Sign up at [MTN Developer Portal](https://momodeveloper.mtn.com/)
2. Create API user and get credentials
3. Add to Render environment variables:
```
MTN_MOBILE_MONEY_API_KEY=your_key
MTN_MOBILE_MONEY_BASE_URL=https://api.mtn.com/mobilemoney
```

### Airtel Money

1. Contact Airtel Business for API access
2. Get API credentials
3. Add to Render environment variables:
```
AIRTEL_MOBILE_MONEY_API_KEY=your_key
AIRTEL_MOBILE_MONEY_BASE_URL=https://openapi.airtel.africa/mobile-money
```

## 🎯 Production Optimization

### Performance
- Enable Render autoscaling for high traffic
- Use Render Redis for caching (paid feature)
- Optimize database indexes (already done in migrations)
- Enable CDN for static assets

### Reliability
- Set up health check pings (UptimeRobot, Pingdom)
- Configure backup schedule for database
- Monitor error rates and set up alerts
- Keep deployment logs for debugging

### Cost Management
- Start with free tiers (sufficient for small schools)
- Upgrade database first when needed
- Scale backend instances based on traffic
- Use Render's suspend feature for staging environments

## 📞 Support

For deployment issues:
- Check Render documentation: https://render.com/docs
- Review deployment logs in Render dashboard
- Contact: nsubugacollin@gmail.com

---

**Deployment Status**: Ready for production
**Last Updated**: 2025-11-07
**Version**: 0.1.0
