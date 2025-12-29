# Angels AI School Platform - Quick Start Guide 🚀

Get your platform running in **under 10 minutes**.

## 🎯 Option 1: Deploy to Render (Recommended for Production)

### Step 1: Prepare Your Credentials
You'll need:
- GitHub account (already connected: `colmeta/angels-ai-school`)
- Clarity API key (you have this)
- Render account (free tier available)

### Step 2: One-Click Deploy

1. **Go to Render Dashboard**:
   ```
   https://dashboard.render.com/select-repo
   ```

2. **Connect Repository**:
   - Select: `colmeta/angels-ai-school`
   - Branch: `cursor/integrate-ai-agent-api-key-and-automate-services-ad91` or `main`

3. **Render will detect `render.yaml` and create**:
   - PostgreSQL database
   - Backend API service
   - All with correct settings

4. **Add Your API Key**:
   - In service settings → Environment
   - Set `CLARITY_API_KEY` to your key
   - Database URL is auto-configured

5. **Deploy**:
   - Click "Apply"
   - Wait 3-5 minutes
   - Your platform is live! 🎉

### Step 3: Run Migrations

1. Go to your service → **Shell** tab
2. Run:
   ```bash
   python run_migrations.py
   ```
3. You'll see: ✅ All migrations completed successfully!

### Step 4: Access Your Platform

Your API will be live at:
```
https://angels-ai-school-api.onrender.com
```

Visit `/docs` to see interactive API documentation.

---

## 🏠 Option 2: Run Locally (For Development)

### Prerequisites
- Python 3.11+
- PostgreSQL
- Node.js 18+

### Backend (5 minutes)

```bash
# 1. Clone (if you haven't already)
git clone https://github.com/colmeta/angels-ai-school.git
cd angels-ai-school

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and CLARITY_API_KEY

# 5. Run migrations
python run_migrations.py

# 6. Start backend
uvicorn api.main:app --reload --port 8000
```

Backend is now running at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend (3 minutes)

```bash
# In a new terminal
cd webapp

# 1. Install dependencies
npm install

# 2. Set environment
cp .env.example .env.local
# Edit if needed (defaults work for local dev)

# 3. Start frontend
npm run dev
```

Frontend is now running at: `http://localhost:5173`

---

## 🧪 Test Your Setup

### 1. Health Check
```bash
curl http://localhost:8000/api/health
# or
curl https://angels-ai-school-api.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T...",
  "clarity_enabled": true
}
```

### 2. Test Clarity Integration
```bash
curl -X POST http://localhost:8000/api/clarity/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Test school platform integration",
    "domain": "education"
  }'
```

### 3. Create Your First School
```bash
curl -X POST http://localhost:8000/api/schools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo School Uganda",
    "code": "DEMO001",
    "country": "Uganda",
    "email": "admin@demoschool.ug",
    "phone": "+256700000000"
  }'
```

---

## 📱 Install PWA

### On Mobile (After Deploy)
1. Open your deployed URL in browser
2. Tap "Add to Home Screen"
3. App installs like a native app!

### On Desktop
1. Open in Chrome/Edge
2. Look for install icon in address bar
3. Click to install

---

## 🎨 Customize Your School

### Set Branding
```bash
curl -X POST http://localhost:8000/api/schools/{school_id}/branding \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Your School Name",
    "primary_color": "#0B69FF",
    "accent_color": "#FFB400",
    "logo_url": "https://your-cdn.com/logo.png"
  }'
```

### Enable/Disable Features
```bash
curl -X POST http://localhost:8000/api/schools/{school_id}/feature-flags \
  -H "Content-Type: application/json" \
  -d '{
    "enable_mobile_money": true,
    "enable_parent_chatbot": true,
    "enable_offline_mode": true
  }'
```

---

## 🔑 Environment Variables Explained

### Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
  # Your PostgreSQL connection string
  # Render provides this automatically

CLARITY_API_KEY=your-clarity-key
  # Your Clarity Engine API key
  # This is what powers all AI agents
```

### Optional (Enhance Features)
```bash
# Fallback AI providers (if Clarity is down)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Mobile money (when ready)
MTN_MOBILE_MONEY_API_KEY=your-mtn-key
AIRTEL_MOBILE_MONEY_API_KEY=your-airtel-key

# Custom chatbot (when ready)
CHATBOT_API_KEY=your-chatbot-key
```

---

## 🆘 Troubleshooting

### "DATABASE_URL not set"
- Check `.env` file exists
- Verify `DATABASE_URL` is set correctly
- For Render: ensure env var is added in dashboard

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd webapp
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Migrations fail
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1;"

# Run migrations manually
python run_migrations.py
```

### PWA won't install
- Ensure you're using HTTPS (Render does this automatically)
- Check browser console for service worker errors
- Clear browser cache and try again

---

## 📞 Need Help?

- 📖 Full docs: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🐛 Issues: [GitHub Issues](https://github.com/colmeta/angels-ai-school/issues)
- 📧 Email: nsubugacollin@gmail.com
- 💬 API Docs: `/docs` on your deployed URL

---

## ✅ You're All Set!

You now have a **production-ready, AI-powered school management platform**:
- ✅ 9 AI agents powered by Clarity
- ✅ Offline-first PWA
- ✅ Multi-tenant white-labeling
- ✅ Mobile money integration
- ✅ Complete school management

**"I wish I had this yesterday!"** 🚀

---

Made with ❤️ in Uganda 🇺🇬
