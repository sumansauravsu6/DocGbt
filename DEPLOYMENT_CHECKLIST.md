# Quick Deployment Checklist

## ✅ Pre-Deployment

- [ ] All code pushed to GitHub
- [ ] Environment variables ready
- [ ] `gunicorn` in `backend/requirements.txt`
- [ ] Production `.env` files configured
- [ ] Test locally one more time

## 🖥️ Backend (Render)

1. [ ] Create new Web Service
2. [ ] Connect GitHub repository
3. [ ] Set Root Directory: `backend`
4. [ ] Set Build Command: `pip install -r requirements.txt`
5. [ ] Set Start Command: `gunicorn run:app`
6. [ ] Add all environment variables
7. [ ] Deploy
8. [ ] Copy backend URL (e.g., `https://docgpt-backend.onrender.com`)

## 🌐 Frontend (Vercel)

1. [ ] Create new Project
2. [ ] Import GitHub repository
3. [ ] Set Root Directory: `frontend`
4. [ ] Framework: Vite
5. [ ] Add environment variables:
   - `VITE_CLERK_PUBLISHABLE_KEY`
   - `VITE_API_URL` (use Render backend URL)
6. [ ] Deploy
7. [ ] Copy Vercel URL (e.g., `https://your-app.vercel.app`)

## 🔄 Update CORS

1. [ ] Go back to Render backend service
2. [ ] Update `ALLOWED_ORIGINS` environment variable with Vercel URL
3. [ ] Save and redeploy

## 🧪 Testing

1. [ ] Visit Vercel URL
2. [ ] Sign in works
3. [ ] Upload PDF works
4. [ ] Chat works
5. [ ] AI responses work
6. [ ] Delete works
7. [ ] Mobile responsive (test on phone)

## 🎉 Done!

Your DocGPT is live!

---

## 📝 Important URLs

**Frontend:** https://your-app.vercel.app
**Backend:** https://docgpt-backend.onrender.com
**Supabase:** https://supabase.com/dashboard
**Qdrant:** https://cloud.qdrant.io
**Clerk:** https://dashboard.clerk.com

---

## 🚨 Common Issues

### CORS Error
- Update `ALLOWED_ORIGINS` on Render with exact Vercel URL
- Include `https://` protocol
- No trailing slash

### 500 Server Error
- Check Render logs
- Verify all environment variables are set
- Check Qdrant/Supabase connections

### Cold Start (Render Free)
- First request takes 30-60 seconds
- Upgrade to paid plan ($7/mo) for instant responses

---

## 💡 Tips

1. **Free Tier Limitations:**
   - Render: Spins down after 15 min inactivity
   - Vercel: Limited bandwidth per month
   - Keep within free tier limits initially

2. **Monitor Usage:**
   - Check Render dashboard for resource usage
   - Monitor Supabase storage
   - Track Groq API usage

3. **Security:**
   - Never commit `.env` files
   - Use strong secret keys
   - Enable RLS on Supabase
   - Review Clerk settings

4. **Performance:**
   - Render free tier has cold starts
   - Consider upgrading for better UX
   - Optimize PDF chunk size if needed
