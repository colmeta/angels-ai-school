# 🚀 Vercel Frontend Deployment Guide

## ✅ **Prerequisites**
- ✅ Backend deployed on Render: `https://angels-ai-school.onrender.com`
- ✅ Vercel account (free tier works perfectly)
- ✅ GitHub repository connected

---

## 📋 **Quick Deploy (5 Minutes)**

### **Option 1: Deploy via Vercel Dashboard (Recommended)**

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/new
   - Click "Import Project"

2. **Import from GitHub**
   - Select repository: `colmeta/angels-ai-school`
   - Root Directory: `webapp`
   - Framework Preset: `Vite`

3. **Environment Variables** (Automatically set from `vercel.json`)
   ```
   VITE_API_BASE_URL=https://angels-ai-school.onrender.com/api
   ```

4. **Deploy Settings**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
   - Node Version: `18.x`

5. **Click "Deploy"**
   - Vercel will build and deploy automatically
   - You'll get a URL like: `https://angels-ai-school.vercel.app`

---

### **Option 2: Deploy via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to webapp directory
cd webapp

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Follow the prompts:
# Set up and deploy? Y
# Which scope? [Your account]
# Link to existing project? N
# Project name? angels-ai-school
# Directory? ./
# Override settings? N
```

---

## 🔧 **Configuration Files Created**

### **1. vercel.json**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://angels-ai-school.onrender.com/api/:path*"
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "https://angels-ai-school.onrender.com/api"
  }
}
```

### **2. .env.production**
```env
VITE_API_BASE_URL=https://angels-ai-school.onrender.com/api
VITE_API_TIMEOUT=20000
VITE_ENABLE_PWA=true
VITE_ENABLE_OFFLINE_MODE=true
```

---

## ✅ **Post-Deployment Checklist**

After deployment, test these URLs:

1. **Homepage**
   ```
   https://your-app.vercel.app
   ```

2. **API Health Check**
   ```
   https://your-app.vercel.app/api/health/simple
   ```
   Should return: `{"status":"ok"}`

3. **API Documentation**
   ```
   https://angels-ai-school.onrender.com/docs
   ```

4. **Test Login/Signup**
   - Go to your Vercel URL
   - Try creating a test account
   - Verify API calls work

---

## 🔐 **Environment Variables on Vercel**

If you need to add more environment variables later:

1. Go to: `https://vercel.com/your-project/settings/environment-variables`
2. Add variables:
   - `VITE_API_BASE_URL` → `https://angels-ai-school.onrender.com/api`
   - `VITE_CLARITY_PEARL_ENABLED` → `true`
   - `VITE_WHATSAPP_ENABLED` → `true`

3. Redeploy:
   ```bash
   vercel --prod
   ```

---

## 🌐 **Custom Domain (Optional)**

1. **Add Custom Domain**
   - Go to: Project Settings → Domains
   - Add your domain: `school.yourdomain.com`
   - Update DNS records as instructed

2. **SSL Certificate**
   - Vercel automatically provisions SSL certificates
   - HTTPS is enabled by default

---

## 🎨 **Features Enabled**

✅ **Progressive Web App (PWA)**
- Installable on mobile/desktop
- Offline mode supported
- Service Worker configured

✅ **Performance Optimizations**
- Code splitting
- Static asset caching
- Gzip compression
- CDN delivery

✅ **API Proxy**
- `/api/*` routes automatically proxy to Render backend
- CORS issues automatically handled
- No additional configuration needed

---

## 🐛 **Troubleshooting**

### **Build Fails**
```bash
# Clear cache and redeploy
vercel --prod --force
```

### **API Not Connecting**
1. Check environment variables are set
2. Verify backend is running: `https://angels-ai-school.onrender.com`
3. Check browser console for CORS errors

### **PWA Not Installing**
1. Must be accessed via HTTPS
2. Check `manifest.webmanifest` is accessible
3. Verify Service Worker is registered

---

## 📊 **Expected Build Output**

```
✓ Building for production
✓ Transforming...
✓ Rendering...
✓ Computing gzip size...

dist/index.html                   1.2 kB
dist/assets/index-abc123.css     12.4 kB │ gzip: 3.1 kB
dist/assets/index-def456.js     245.8 kB │ gzip: 78.2 kB
dist/assets/vendor-ghi789.js    156.3 kB │ gzip: 52.1 kB

✓ Built in 23s
```

---

## 🎯 **Next Steps After Deployment**

1. ✅ Test all features work end-to-end
2. ✅ Set up custom domain (optional)
3. ✅ Configure CORS on backend if needed
4. ✅ Enable analytics (Vercel Analytics)
5. ✅ Set up monitoring/error tracking

---

## 💰 **Vercel Free Tier Limits**

✅ **Included Free:**
- 100 GB bandwidth/month
- 6,000 build minutes/month
- Unlimited static requests
- Automatic SSL certificates
- Global CDN
- Unlimited team members

**Perfect for testing and initial deployment!**

---

## 🚀 **You're All Set!**

Your frontend will be live at: `https://angels-ai-school.vercel.app`

Connected to backend: `https://angels-ai-school.onrender.com`

**Full stack platform is now LIVE!** 🎉
