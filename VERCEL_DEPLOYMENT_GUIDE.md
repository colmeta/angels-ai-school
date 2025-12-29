# 🚀 Vercel Deployment Guide - Frontend Setup

## Problem You're Experiencing

Your Render backend is awake and responding, but when you click "Register" on the Vercel frontend, it fails because:

1. **Frontend uses relative URL**: The code was calling `/api/schools/register` (same domain as frontend)
2. **Backend is on different domain**: Your API is at `https://your-app.onrender.com`
3. **CORS not configured**: Backend needs to allow requests from Vercel domain

**✅ FIXED**: I've updated the code to use environment variables.

---

## Step-by-Step Deployment Instructions

### Step 1: Get Your Render Backend URL

1. Go to your Render dashboard
2. Find your backend service
3. Copy the full URL (should look like: `https://angels-ai-school.onrender.com`)

### Step 2: Configure Environment Variables in Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project (the frontend)
3. Go to **Settings** → **Environment Variables**
4. Add the following variables:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `VITE_API_URL` | `https://your-app.onrender.com` | Production |
| `VITE_GOOGLE_CLIENT_ID` | Your Google OAuth Client ID (if using) | Production |

**IMPORTANT**: Replace `your-app.onrender.com` with your actual Render URL!

### Step 3: Configure Backend CORS (Render)

Your backend needs to allow requests from Vercel:

1. Go to your Render dashboard
2. Select your backend service
3. Go to **Environment** → **Environment Variables**
4. Add or update:

| Variable Name | Value |
|--------------|-------|
| `FRONTEND_URL` | `https://your-app.vercel.app` |
| `ALLOWED_BRAND_DOMAINS` | `your-app.vercel.app` (without https://) |

**IMPORTANT**: Replace `your-app.vercel.app` with your actual Vercel URL!

### Step 4: Deploy Updated Code

We've updated the frontend code to use environment variables. Now deploy:

```bash
# From the project root
cd webapp
git add .
git commit -m "fix: use environment variable for API URL"
git push origin main
```

Vercel will automatically deploy the new version.

### Step 5: Verify the Fix

1. **Wait 2-3 minutes** for both Vercel and Render to redeploy
2. Open browser **Developer Tools** (F12)
3. Go to **Network** tab
4. Visit your Vercel URL and click "Register School"
5. Check the network request - it should now call `https://your-render-app.onrender.com/api/schools/register`

---

## Troubleshooting

### Issue: Still getting errors?

**Check CORS in browser console:**
- If you see "CORS policy" error → Backend CORS not configured correctly
- If you see "Failed to fetch" → Backend might be asleep (wait 30 seconds)
- If you see "404 Not Found" → API URL is wrong

**Solution:**
1. Verify `FRONTEND_URL` in Render includes your Vercel domain
2. Restart your Render service
3. Clear browser cache and try again

### Issue: Environment variables not working?

**Vercel needs to rebuild:**
1. Go to Vercel dashboard → Deployments
2. Click "Redeploy" on the latest deployment
3. Wait for build to complete

---

## No, You Don't Need UptimeRobot for Vercel!

**UptimeRobot is only for Render (backend)** ✅

- **Render Free Tier**: Sleeps after 15 minutes of inactivity → needs UptimeRobot to ping it
- **Vercel**: Never sleeps, always instant → **no monitoring needed**

Your current setup is correct:
- ✅ UptimeRobot pings Render backend every 5 minutes
- ✅ Vercel frontend is always awake (no action needed)

---

## Quick Reference

**Frontend (Vercel):**
- URL: `https://your-app.vercel.app`
- Environment Variable: `VITE_API_URL=https://your-render-app.onrender.com`

**Backend (Render):**
- URL: `https://your-render-app.onrender.com`
- Environment Variable: `FRONTEND_URL=https://your-app.vercel.app`

**UptimeRobot:**
- Monitor: Render backend only (`https://your-render-app.onrender.com/health`)
- Ping: Every 5 minutes ✅

---

## Next Steps

1. ✅ Push the code changes (done above)
2. ⏳ Configure environment variables in Vercel
3. ⏳ Configure environment variables in Render  
4. ⏳ Wait for both to redeploy (2-3 minutes)
5. ✅ Test registration on your Vercel URL

**After these steps, your frontend and backend will be properly connected!** 🎉
