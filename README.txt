# 🚀 Angels AI - Complete Educational Revolution Platform

## MVP Deployment Status: ✅ READY

### Quick Start (5 Minutes)

1. **Fork this repo** on GitHub
2. **Set up Supabase** (free tier):
   - Go to [supabase.com](https://supabase.com)
   - Create project
   - Run the schema from `angels_ai_schema.sql`
   - Copy connection string

3. **Configure Secrets** in GitHub:
   - Go to Settings → Secrets → Actions
   - Add `DATABASE_URL`
   - Add `OPENAI_API_KEY`
   - Add `CLARITY_API_KEY`
   - Optional: `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`
   - Optional: `MTN_MOBILE_MONEY_API_KEY`, `AIRTEL_MOBILE_MONEY_API_KEY`
   - Optional: `CHATBOT_API_KEY`

4. **Deploy**:
   - Push to main branch
   - GitHub Actions will auto-deploy
   - API will be live in ~3 minutes

### API Endpoints

**Base URL**: `https://your-app.onrender.com`

#### Health
- `GET /api/health` - Health check
- `GET /api/health/database` - Database check

#### Students
- `POST /api/students/register` - Register student
- `GET /api/students/enrollment/{school_id}` - Get stats
- `GET /api/students/dashboard/{school_id}` - Dashboard

#### Fees
- `GET /api/fees/ooda-loop/{school_id}` - Run OODA loop
- `GET /api/fees/report/{school_id}` - Financial report

#### Parents
- `POST /api/parents/reminders/{school_id}` - Send reminders
- `POST /api/parents/event-broadcast/{school_id}` - Broadcast

#### AI Agents
- `GET /api/agents/daily-operations/{school_id}` - Run daily ops
- `GET /api/agents/ceo-briefing/{school_id}` - CEO briefing
- `POST /api/agents/fee-collection-campaign/{school_id}` - Launch campaign

### Test It
```bash
curl https://your-app.onrender.com/api/health
```

### Frontend PWA

```bash
cd webapp
npm install
npm run dev
```
Use `VITE_API_BASE_URL` in `webapp/.env` to point to your backend (defaults to `http://localhost:8000/api`).

### Mobile Money & Chatbot Integrations

- Create the tables `mobile_money_transactions`, `school_branding`, and `school_feature_flags` using your preferred migration tool.
- Mobile money works without live keys (queued/manual mode). Populate `MTN_MOBILE_MONEY_API_KEY` / `AIRTEL_MOBILE_MONEY_API_KEY` when ready for live APIs.
- Chatbot falls back to Clarity if `CHATBOT_API_KEY` is not provided.

### Support Operations Data Tables

Create the following tables (or equivalent views) before deploying the new support module:

- `incidents`
- `inventory_items`
- `inventory_transactions`
- `health_visits`
- `library_transactions`
- `transport_logs`

Each insert automatically captures metadata JSON payloads for Clarity-powered summaries.

### Documentation
Visit `/docs` for interactive API documentation (Swagger UI)
