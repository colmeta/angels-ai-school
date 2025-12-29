# 🎓 Angels AI School - Frontend

Complete educational revolution platform for African schools - **Frontend Application**

---

## 🚀 **Quick Start**

### **Local Development**
```bash
npm install
npm run dev
```
Visit: `http://localhost:5173`

### **Production Build**
```bash
npm run build
npm run preview
```

---

## 🌐 **Deploy to Vercel (2 Minutes)**

### **Method 1: One-Click Deploy**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/colmeta/angels-ai-school&root-directory=webapp)

### **Method 2: Vercel Dashboard**

1. Go to: https://vercel.com/new
2. Import `colmeta/angels-ai-school`
3. Set **Root Directory:** `webapp`
4. Click **Deploy**

✅ That's it! Your app will be live in 2-3 minutes.

---

## 📱 **Features**

✅ **Progressive Web App (PWA)**
- Install on phone/desktop
- Works offline
- Auto-sync when online

✅ **5 User Portals**
- Teacher Workspace
- Parent Portal
- Student Dashboard
- Admin Panel
- Support Operations

✅ **AI-Powered**
- Voice commands
- Natural language input
- Intelligent chatbot
- Automated workflows

✅ **Ugandan Context**
- MTN Mobile Money
- Airtel Money
- Multi-language support
- UNEB integration

---

## 🔗 **API Connection**

**Backend URL:** `https://angels-ai-school.onrender.com`

**API Docs:** `https://angels-ai-school.onrender.com/docs`

Already configured in `vercel.json` and `.env.production`

---

## 📂 **Project Structure**

```
webapp/
├── src/
│   ├── pages/              # Main application pages
│   │   ├── TeacherWorkspace.tsx
│   │   ├── ParentPortal.tsx
│   │   ├── StudentPulse.tsx
│   │   ├── AdminDashboard.tsx
│   │   └── SupportOps.tsx
│   ├── components/         # Reusable components
│   │   ├── AppShell.tsx
│   │   ├── VoiceInput.tsx
│   │   └── RoleSwitcher.tsx
│   ├── lib/               # API clients
│   │   ├── apiClient.ts
│   │   ├── chatbot.ts
│   │   └── payments.ts
│   ├── hooks/             # React hooks
│   └── stores/            # State management
├── public/                # Static assets
│   ├── manifest.webmanifest
│   └── sw.js
└── vercel.json           # Deployment config
```

---

## 🛠️ **Tech Stack**

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Routing:** React Router v6
- **State:** Zustand + React Query
- **Styling:** Tailwind CSS
- **PWA:** Workbox + Service Workers
- **Deployment:** Vercel

---

## 🔐 **Environment Variables**

Create `.env.local` for development:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=20000
VITE_ENABLE_PWA=true
VITE_ENABLE_OFFLINE_MODE=true
```

Production variables are auto-configured in Vercel.

---

## 📱 **Install as PWA**

### **On Mobile (Android/iOS)**
1. Open in Chrome/Safari
2. Tap menu (⋮)
3. Select "Add to Home Screen"
4. App icon appears on home screen

### **On Desktop (Chrome/Edge)**
1. Click install icon in address bar
2. Or go to Menu → Install App
3. App opens in its own window

---

## 🎨 **White-labeling**

Schools can customize:
- School name
- Primary colors
- Logo
- Features enabled

Configure in Admin Dashboard or database.

---

## 🐛 **Troubleshooting**

### **Build Fails**
```bash
rm -rf node_modules dist
npm install
npm run build
```

### **API Not Connecting**
- Check `VITE_API_BASE_URL` is set
- Verify backend is running
- Check browser console for errors

### **PWA Not Installing**
- Must use HTTPS
- Service Worker must register successfully
- Check `manifest.webmanifest` is accessible

---

## 📊 **Performance**

- **First Paint:** < 1.5s
- **Time to Interactive:** < 3s
- **Lighthouse Score:** 95+
- **Bundle Size:** < 500KB (gzipped)

---

## 🔗 **Links**

- **Live Frontend:** `https://angels-ai-school.vercel.app`
- **Live Backend:** `https://angels-ai-school.onrender.com`
- **API Docs:** `https://angels-ai-school.onrender.com/docs`
- **GitHub:** `https://github.com/colmeta/angels-ai-school`

---

## 📄 **License**

Proprietary - © 2025 Angels AI

---

**Built with ❤️ for African Schools**
