# Deploy Full-Stack to Render - Step-by-Step Guide

> **Best Open-Source Choice: Render.com**
> - ✅ Free tier for frontend + backend + database
> - ✅ Automatic GitHub deployments
> - ✅ PostgreSQL included
> - ✅ No credit card required initially
> - ✅ Generous free limits

---

## 🚀 Quick Deploy (5 minutes)

### 1. Sign Up on Render
```bash
# Go to https://render.com/
# Click "Sign up" → "GitHub" → Authorize
```

### 2. Deploy Everything at Once
```bash
# Go to: https://render.com/
# Click "Dashboard" → "New +" → "Blueprint"
# Enter GitHub repo: arunk2493/requirement-analyser
# Select branch: host-web or login-dev
# Render will auto-deploy from render.yaml ✨
```

### 3. Wait for Deployment
- PostgreSQL database: ~1 minute
- Backend API: ~3-5 minutes  
- Frontend: ~2-3 minutes
- **Total**: ~5-10 minutes

### 4. Access Your App
- **Frontend**: https://requirement-analyser.onrender.com
- **Backend API**: https://requirement-analyser-api.onrender.com
- **Database**: Managed by Render

---

## 📋 Manual Step-by-Step (If Blueprint Doesn't Work)

### STEP 1: Create Render Account
1. Go to https://render.com/
2. Click **"Sign up"** → **"Continue with GitHub"**
3. Authorize Render to access your repositories
4. Verify email

---

### STEP 2: Deploy PostgreSQL Database

**Create Database:**
1. Dashboard → **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `requirement-analyser-db`
   - **Database**: `requirement_analyser`
   - **User**: `admin`
   - **Region**: Pick closest to your location (e.g., Oregon)
   - **PostgreSQL Version**: Latest
3. Click **"Create Database"**
4. **⏳ Wait 2-3 minutes** for database to spin up

**Copy Connection String:**
1. Once created, go to database details page
2. Copy the **"Internal Database URL"** (not External URL)
   - Format: `postgresql://admin:password@host:5432/requirement_analyser`
3. **Save this somewhere safe!** You'll need it for backend

---

### STEP 3: Deploy Backend API

**Create Web Service:**
1. Dashboard → **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"**
3. **"Connect your GitHub repository"**
4. Search and select: **`arunk2493/requirement-analyser`**
5. Fill in:
   - **Name**: `requirement-analyser-api`
   - **Region**: `Same as database` (important!)
   - **Branch**: `host-web`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn -w 4 -b 0.0.0.0:10000 app:app`

**Add Environment Variables:**
1. Click **"Environment"** tab
2. Add these variables:
   ```
   KEY: DATABASE_URL
   VALUE: postgresql://admin:PASSWORD@HOST:5432/requirement_analyser
   (from Step 2)
   
   KEY: GEMINI_API_KEY
   VALUE: your-actual-gemini-key
   
   KEY: PYTHON_VERSION
   VALUE: 3.11.0
   ```

3. Click **"Create Web Service"**
4. **⏳ Wait 5-10 minutes** for deployment

**Verify Backend:**
1. Once deployed, copy the service URL (e.g., `https://requirement-analyser-api.onrender.com`)
2. Visit: `https://requirement-analyser-api.onrender.com/docs`
   - Should show FastAPI Swagger UI ✅

---

### STEP 4: Deploy Frontend

**Create Static Site:**
1. Dashboard → **"New +"** → **"Static Site"**
2. Click **"Build and deploy from a Git repository"**
3. **"Connect your GitHub repository"**
4. Select: **`arunk2493/requirement-analyser`**
5. Fill in:
   - **Name**: `requirement-analyser`
   - **Region**: `Same as others`
   - **Branch**: `host-web`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

**Add Environment Variables:**
1. Click **"Environment"** tab
2. Add:
   ```
   KEY: VITE_API_BASE
   VALUE: https://requirement-analyser-api.onrender.com
   (your backend URL from Step 3)
   ```

3. Click **"Create Static Site"**
4. **⏳ Wait 3-5 minutes** for build and deployment

**Access Frontend:**
1. Copy the site URL (e.g., `https://requirement-analyser.onrender.com`)
2. Visit in browser ✅

---

## ✅ Verification Checklist

### Backend API is Working
- [ ] Visit `https://requirement-analyser-api.onrender.com/docs`
- [ ] See Swagger UI with API endpoints
- [ ] No error in browser console

### Frontend is Loading
- [ ] Visit `https://requirement-analyser.onrender.com`
- [ ] See the full application UI
- [ ] No 404 or blank page

### Frontend Can Connect to Backend
1. Open frontend in browser
2. Open Developer Tools (F12) → **Network** tab
3. Try uploading a file
4. Check requests go to `requirement-analyser-api.onrender.com` ✅

### Full Feature Test
- [ ] Upload PDF/DOCX file → should work
- [ ] Generate Epics → should appear in table
- [ ] Generate Stories → should appear in table
- [ ] Generate QA → should appear in table
- [ ] Generate Test Plan → should appear in table
- [ ] All with Confluence links

---

## 🔧 Configuration Details

### Files Updated for Render Deployment

**1. `backend/app.py`**
- Added production frontend URL to CORS:
  ```python
  "https://requirement-analyser.onrender.com",
  ```

**2. `backend/requirements.txt`**
- Changed `psycopg2` → `psycopg2-binary` (works on Render)
- Added `gunicorn` for production server

**3. `frontend/vite.config.js`**
- Changed `base: "/requirement-analyser/"` → `base: "/"`
- Since Render hosts on root, not subdirectory

**4. `render.yaml`** (NEW)
- Blueprint configuration for one-click deployment
- Automatically creates DB, backend, and frontend

---

## 🐛 Troubleshooting

### Frontend shows blank page / 404
**Solution:**
1. Check build succeeded: Dashboard → Select static site → **"Builds"** tab
2. If failed, click build to see error logs
3. Common fixes:
   - Delete `node_modules/` and `package-lock.json` locally
   - Commit and push to GitHub
   - Redeploy on Render

### Backend shows error on startup
**Solution:**
1. Go to Dashboard → Select web service → **"Logs"** tab
2. Scroll to see error messages
3. Check DATABASE_URL is correct:
   ```bash
   # Should be Internal URL, not External URL
   postgresql://admin:PASSWORD@HOST/requirement_analyser
   ```
4. Verify all environment variables are set

### API calls return 404 / CORS errors
**Solution:**
1. Check `VITE_API_BASE` is set correctly in frontend environment
2. Check backend CORS includes frontend URL:
   - `https://requirement-analyser.onrender.com`
3. Check backend is actually running:
   - Visit `https://requirement-analyser-api.onrender.com/docs` in browser

### Database won't connect
**Solution:**
1. Copy **Internal Database URL** from Render PostgreSQL dashboard (NOT external)
2. Paste into backend `DATABASE_URL` environment variable
3. Restart backend service: Dashboard → Web service → **"Manual Deploy"** → **"Deploy latest commit"**

### Deployment is slow / hanging
**Solution:**
1. Free tier services may be slow
2. First deployment takes longer (dependency downloads)
3. Subsequent deployments are faster (~1-2 min)
4. Consider upgrading to paid plan for production

### File uploads not working
**Solution:**
Update `backend/routes/upload.py` to use `/tmp`:
```python
import os
UPLOAD_DIR = "/tmp/uploads"  # Render's temp storage
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

---

## 📊 What's Included in Render Free Tier

| Resource | Limit | Notes |
|----------|-------|-------|
| PostgreSQL Database | 256 MB | Free tier, sufficient for testing |
| Web Service | 1 free instance | Spins down after 15 min inactivity |
| Static Sites | Unlimited | No limits, instant deployment |
| Compute | Shared resources | Good for development/small projects |
| Bandwidth | ~100 GB/month | Should be plenty |

⚠️ **Note:** Free web services spin down after 15 minutes of no requests. First request after sleep takes ~30 seconds to wake up. For production, upgrade to paid tier.

---

## 🔐 Important: API Keys & Secrets

Never commit real API keys to GitHub! 

**For Local Development:**
1. Create `backend/.env`:
   ```
   DATABASE_URL=postgresql://localhost/requirement_analyser
   GEMINI_API_KEY=your-actual-key
   ```

2. Add to `.gitignore`:
   ```
   .env
   .env.local
   ```

**For Render Production:**
1. Go to Web Service → **"Environment"**
2. Add sensitive values there (not in code)
3. Render keeps them secure

---

## 📈 Next Steps After Deployment

### 1. Share Your App
- Frontend: https://requirement-analyser.onrender.com
- Let others use it!

### 2. Monitor Performance
- Dashboard → Click service → **"Logs"** and **"Metrics"** tabs
- Watch for errors or performance issues

### 3. Update Code
```bash
git push origin host-web
# Render automatically redeploys! ✨
```

### 4. Scale Later
- As usage grows, upgrade services to paid plans
- Upgrade database size if needed

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **React/Vite Docs**: https://vitejs.dev/

---

## 🎉 You're Done!

Your full-stack application is now live on Render! 

**Share your URLs:**
- 🌐 Frontend: https://requirement-analyser.onrender.com
- 🔌 Backend: https://requirement-analyser-api.onrender.com

Happy deploying! 🚀
