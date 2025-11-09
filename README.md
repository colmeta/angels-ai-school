# Angels AI School Platform 🎓✨

**Complete Educational Revolution Platform** - An offline-first, AI-powered school management system designed for first-world efficiency in third-world environments.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🚀 Features

### 🤖 AI-Powered Agents
- **Digital CEO**: Strategic intelligence and executive dashboards
- **Command Intelligence Agent**: Natural language to actionable tasks
- **Document Intelligence**: OCR and automated data entry from photos
- **Parent Engagement Oracle**: 24/7 multilingual support
- **Financial Operations**: Automated treasurer with OODA loop
- **Academic Operations**: Predictive analytics and compliance
- **Teacher Liberation**: Administrative freedom through automation
- **Executive Assistant**: Ultimate administrative coordinator
- **Security & Safety Guardian**: Incident tracking and safety monitoring

### 📱 Offline-First PWA
- ✅ Works completely offline
- ✅ Installable on phones, tablets, and desktops
- ✅ Background sync when connection returns
- ✅ Low-data mode for limited bandwidth

### 💰 Mobile Money Integration
- **MTN Mobile Money** - Native integration
- **Airtel Money** - Native integration
- Queue payments offline, process when connected
- Automated fee collection and reconciliation

### 🎨 White-Label & Multi-Tenant
- Custom branding per school (logo, colors, name)
- Feature flags for enabling/disabling modules
- Isolated data per school
- Scalable for multiple institutions

### 📚 Complete School Management
- **Academic**: Attendance, assessments, timetables, performance tracking
- **Financial**: Fee management, expenses, budgets, mobile money payments
- **Support**: Incidents, inventory, health (sickbay), library, transport
- **Communication**: Parent-teacher messaging, notifications, in-app chatbot

### 🌍 Built for Africa
- Works in low-connectivity environments
- Mobile-first design (teachers use phones, not laptops)
- Photo-based data entry (snap attendance sheets, they auto-digitize)
- MTN & Airtel Money instead of Stripe/PayPal
- English/Luganda/Swahili support ready

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Frontend (React PWA)                    │
│  Offline Storage │ Service Worker │ Push Sync       │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────┐
│            Backend (FastAPI)                         │
│  REST API │ WebSocket │ Background Jobs             │
└────────────────────┬────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────┴────┐   ┌──────┴──────┐  ┌────┴────────┐
│PostgreSQL│   │Clarity Engine│  │ CrewAI Agents│
│ Database │   │ (Your API)  │  │ (9 Agents)   │
└──────────┘   └─────────────┘  └──────────────┘
```

## 📦 Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL (multi-tenant)
- CrewAI (agent orchestration)
- Psycopg2 (database)
- Httpx (API calls)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Query (data fetching)
- Zustand (state management)
- Workbox (service worker)

**AI/Intelligence:**
- Clarity Engine (your primary AI brain)
- Optional fallbacks: OpenAI, Anthropic, Gemini, Groq

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/angels-ai-school.git
cd angels-ai-school
```

### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python run_migrations.py

# Start backend
uvicorn api.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd webapp

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local if needed

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 4. Database Setup
Make sure PostgreSQL is running and create a database:
```bash
createdb angels_ai_school
```

Or use a cloud database (Render, Supabase, etc.)

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

### One-Click Deploy to Render
1. Click the "Deploy to Render" button above
2. Connect your GitHub repository
3. Set environment variables
4. Deploy!

### Manual Deploy
```bash
# Build frontend
cd webapp
npm run build

# Deploy backend (includes frontend)
# Push to Render, Railway, or your hosting provider
```

## 🔐 Environment Variables

### Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CLARITY_API_KEY=your-clarity-key
```

### Optional (Recommended)
```bash
# Fallback AI providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=...

# Mobile Money
MTN_MOBILE_MONEY_API_KEY=...
AIRTEL_MOBILE_MONEY_API_KEY=...

# Chatbot (when ready)
CHATBOT_API_KEY=...
```

See `.env.example` for complete list.

## 📖 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints
- `GET /api/health` - Health check
- `POST /api/clarity/analyze` - Clarity AI analysis
- `GET /api/schools/{school_id}/branding` - White-label config
- `POST /api/payments/mobile-money/initiate` - Start mobile money payment
- `POST /api/chatbot/query` - In-app chatbot

## 🧪 Testing

```bash
# Backend tests
pytest

# Frontend tests
cd webapp
npm run test

# Lint
npm run lint
```

## 📱 Mobile Money Setup

### MTN Mobile Money
1. Register at [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
2. Create subscription and get API key
3. Add to environment variables

### Airtel Money
1. Contact Airtel Business for API access
2. Get credentials
3. Add to environment variables

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 👥 Team

Built with ❤️ for African schools by [@nsubugacollin](mailto:nsubugacollin@gmail.com)

**Powered by:**
- [Clarity Engine](https://veritas-engine-zae0.onrender.com) - Primary AI intelligence
- [CrewAI](https://www.crewai.com/) - Agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework

## 🎯 Roadmap

- [x] Core platform with 9 AI agents
- [x] Offline-first PWA
- [x] Multi-tenant white-labeling
- [x] Mobile money integration
- [x] Photo-based data entry
- [ ] Voice commands (coming soon)
- [ ] SMS integration
- [ ] Advanced analytics dashboard
- [ ] Mobile native apps (iOS/Android)
- [ ] Multi-language support (Luganda, Swahili)

## 💬 Support

- Email: nsubugacollin@gmail.com
- Documentation: [/docs](/docs)
- Issues: [GitHub Issues](https://github.com/yourusername/angels-ai-school/issues)

## 🌟 Acknowledgments

Special thanks to:
- All schools in Uganda pushing education forward
- The open-source community
- Clarity Engine for powering the intelligence layer

---

**"I wish I had this yesterday"** - Every school administrator who sees this platform

Made with 🚀 in Uganda 🇺🇬
