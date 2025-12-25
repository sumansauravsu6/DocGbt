# DocGPT Deployment Guide

Complete guide to deploy DocGPT with **Frontend on Vercel** and **Backend on Render**.

---

## 📋 Prerequisites

Before starting deployment, ensure you have:

1. ✅ GitHub account
2. ✅ Vercel account (sign up at https://vercel.com)
3. ✅ Render account (sign up at https://render.com)
4. ✅ All API keys ready:
   - Clerk (frontend + backend keys)
   - Supabase (URL + keys)
   - Qdrant Cloud (URL + API key)
   - Groq API key

---

## 🚀 Step 1: Prepare Your Code

### 1.1 Push to GitHub

```bash
cd C:\Users\Z005652D\Downloads\docGbt

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/docgpt.git
git branch -M main
git push -u origin main
```

### 1.2 Update Environment Variables for Production

**Backend (.env) - DON'T COMMIT THIS FILE**

Make sure your `backend/.env` has production-ready values:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<GENERATE_A_STRONG_SECRET_KEY>

# Supabase Configuration
SUPABASE_URL=https://vfylpboaeykymhcfogrs.supabase.co
SUPABASE_KEY=<YOUR_SUPABASE_ANON_KEY>
SUPABASE_SERVICE_KEY=<YOUR_SUPABASE_SERVICE_KEY>
SUPABASE_STORAGE_BUCKET=document

# Clerk Configuration
CLERK_SECRET_KEY=<YOUR_CLERK_SECRET_KEY>
CLERK_PUBLISHABLE_KEY=<YOUR_CLERK_PUBLISHABLE_KEY>

# Qdrant Cloud Configuration
QDRANT_URL=https://14f5ed9a-4f4e-449b-8c90-fee613457140.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=<YOUR_QDRANT_API_KEY>
QDRANT_COLLECTION_NAME=document_chunks

# Groq AI Configuration
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
GROQ_MODEL=llama-3.3-70b-versatile

# Server Configuration
HOST=0.0.0.0
PORT=5000
ALLOWED_ORIGINS=https://your-app.vercel.app
```

---

## 🖥️ Step 2: Deploy Backend to Render

### 2.1 Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `docGbt` repository

### 2.2 Configure Build Settings

**Basic Settings:**
- **Name:** `docgpt-backend`
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** 
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command:**
  ```bash
  gunicorn run:app
  ```

### 2.3 Add Environment Variables

Click **"Environment"** tab and add ALL variables from your `backend/.env`:

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<STRONG_SECRET_KEY>
SUPABASE_URL=https://vfylpboaeykymhcfogrs.supabase.co
SUPABASE_KEY=<YOUR_KEY>
SUPABASE_SERVICE_KEY=<YOUR_KEY>
SUPABASE_STORAGE_BUCKET=document
CLERK_SECRET_KEY=<YOUR_KEY>
CLERK_PUBLISHABLE_KEY=<YOUR_KEY>
QDRANT_URL=https://14f5ed9a-4f4e-449b-8c90-fee613457140.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=<YOUR_KEY>
QDRANT_COLLECTION_NAME=document_chunks
GROQ_API_KEY=<YOUR_KEY>
GROQ_MODEL=llama-3.3-70b-versatile
HOST=0.0.0.0
PORT=5000
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### 2.4 Add gunicorn to requirements.txt

Before deploying, add this to `backend/requirements.txt`:

```txt
gunicorn==21.2.0
```

### 2.5 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://docgpt-backend.onrender.com`

### 2.6 Update ALLOWED_ORIGINS

Once you have your Vercel URL (next step), update the `ALLOWED_ORIGINS` environment variable on Render:

```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app,https://your-app-preview.vercel.app
```

---

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Create New Project

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Select `docGbt`

### 3.2 Configure Project Settings

**Framework Preset:** Vite

**Root Directory:** `frontend`

**Build Command:** (leave default)
```bash
npm run build
```

**Output Directory:** `dist`

**Install Command:** (leave default)
```bash
npm install
```

### 3.3 Add Environment Variables

Click **"Environment Variables"** and add:

```
VITE_CLERK_PUBLISHABLE_KEY=<YOUR_CLERK_PUBLISHABLE_KEY>
VITE_API_URL=https://docgpt-backend.onrender.com/api
```

**Important:** Replace `https://docgpt-backend.onrender.com` with your actual Render backend URL!

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait for build (3-5 minutes)
3. Your app will be live at `https://your-app.vercel.app`

---

## 🔄 Step 4: Update Backend CORS

After getting your Vercel URL, go back to Render:

1. Open your backend service
2. Go to **"Environment"** tab
3. Update `ALLOWED_ORIGINS`:
   ```
   https://your-app.vercel.app
   ```
4. Click **"Save Changes"**
5. Service will auto-redeploy

---

## 🧪 Step 5: Test Your Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Sign in with Clerk
3. Upload a test PDF document
4. Create a chat session
5. Ask questions about the document
6. Verify:
   - ✅ PDF uploads successfully
   - ✅ Embeddings created in Qdrant
   - ✅ AI responses are generated
   - ✅ Markdown formatting works
   - ✅ Delete functionality works
   - ✅ Mobile responsive design

---

## 📱 Mobile Responsiveness

The UI is now fully responsive:

- **Mobile (< 640px):** 
  - Sidebar becomes overlay
  - Sessions list hidden
  - Full-width chat
  - Compact header

- **Tablet (640px - 1024px):**
  - Sidebar as overlay
  - Sessions visible
  - Responsive spacing

- **Desktop (> 1024px):**
  - Full layout with all panels
  - Maximum information density

---

## 🔧 Environment Variables Reference

### Backend (.env)

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Environment mode | Yes | `production` |
| `FLASK_DEBUG` | Debug mode | Yes | `False` |
| `SECRET_KEY` | Flask secret key | Yes | `your-secret-key` |
| `SUPABASE_URL` | Supabase project URL | Yes | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon key | Yes | `eyJ...` |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Yes | `eyJ...` |
| `CLERK_SECRET_KEY` | Clerk secret key | Yes | `sk_test_...` |
| `QDRANT_URL` | Qdrant cloud URL | Yes | `https://xxx.cloud.qdrant.io:6333` |
| `QDRANT_API_KEY` | Qdrant API key | Yes | `eyJ...` |
| `GROQ_API_KEY` | Groq API key | Yes | `gsk_...` |
| `ALLOWED_ORIGINS` | CORS allowed origins | Yes | `https://app.vercel.app` |

### Frontend (.env)

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk publishable key | Yes | `pk_test_...` |
| `VITE_API_URL` | Backend API URL | Yes | `https://api.onrender.com/api` |

---

## 🚨 Troubleshooting

### CORS Errors

**Problem:** Frontend can't connect to backend

**Solution:**
1. Check `ALLOWED_ORIGINS` in Render includes your Vercel URL
2. Must include protocol (`https://`)
3. No trailing slash
4. Include all Vercel preview URLs if needed

### Authentication Errors

**Problem:** Clerk authentication fails

**Solution:**
1. Ensure `VITE_CLERK_PUBLISHABLE_KEY` matches backend `CLERK_SECRET_KEY`
2. Check Clerk dashboard → allowed origins includes Vercel URL
3. Verify both keys are from same Clerk application

### Upload Failures

**Problem:** PDF uploads fail

**Solution:**
1. Check Supabase storage bucket exists (`document`)
2. Verify bucket is public or has proper policies
3. Check `SUPABASE_SERVICE_KEY` has storage permissions
4. Render free tier has 512MB disk - may fill up

### Slow Responses

**Problem:** AI responses take too long

**Solution:**
1. Render free tier spins down after inactivity (cold start ~1min)
2. Upgrade to paid plan for always-on service
3. Check Groq API limits/quota

### Qdrant Connection Errors

**Problem:** Can't connect to Qdrant

**Solution:**
1. Verify `QDRANT_URL` includes port `:6333`
2. Check `QDRANT_API_KEY` is correct
3. Ensure Qdrant cluster is running

---

## 💰 Cost Estimate

- **Vercel:** Free tier (Hobby) - $0/month
- **Render:** Free tier - $0/month (with cold starts)
- **Supabase:** Free tier - $0/month (500MB storage)
- **Qdrant Cloud:** Free tier - $0/month (1GB cluster)
- **Groq API:** Free tier - $0/month (limited requests)
- **Clerk:** Free tier - $0/month (10k MAU)

**Total: $0/month** (with free tier limitations)

### Upgrade Recommendations

For production use:
- **Render:** $7/month (no cold starts, always on)
- **Vercel:** Free tier sufficient for most use cases
- **Supabase:** $25/month (8GB storage, better performance)
- **Qdrant:** $95/month (better performance)

---

## 🔐 Security Checklist

Before going live:

- [ ] Change all default passwords/secrets
- [ ] Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Review Clerk security settings
- [ ] Limit CORS origins to production domains only
- [ ] Enable HTTPS only (Vercel/Render do this automatically)
- [ ] Review Supabase storage bucket permissions
- [ ] Set up error monitoring (Sentry)
- [ ] Configure rate limiting for API endpoints

---

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:

1. **Push to GitHub main branch**
2. **Vercel auto-deploys frontend**
3. **Render auto-deploys backend**

To disable auto-deploy:
- **Vercel:** Project Settings → Git → Disable
- **Render:** Service Settings → Auto-Deploy → Off

---

## 📊 Monitoring

### Backend (Render)

- Logs: https://dashboard.render.com → Your Service → Logs
- Metrics: CPU, Memory, Network usage
- Events: Deployments, restarts

### Frontend (Vercel)

- Analytics: https://vercel.com/analytics
- Logs: Project → Deployments → View Logs
- Performance: Real User Metrics (RUM)

### Database (Supabase)

- Dashboard: https://supabase.com/dashboard
- Storage usage, API calls, active connections
- Table editor, SQL editor

---

## 🎉 Success!

Your DocGPT is now deployed:

- **Frontend:** https://your-app.vercel.app
- **Backend:** https://docgpt-backend.onrender.com
- **Mobile Responsive:** ✅
- **Production Ready:** ✅

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Clerk Documentation](https://clerk.com/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Groq Documentation](https://console.groq.com/docs)

---

## 💡 Next Steps

1. Set up custom domain on Vercel
2. Configure error monitoring (Sentry)
3. Add analytics (Google Analytics, PostHog)
4. Implement rate limiting
5. Add more AI features
6. Optimize PDF processing
7. Add document OCR support
8. Multi-language support
