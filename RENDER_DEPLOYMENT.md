# Deploy Full-Stack App to Render (Frontend + Backend + Database)

## Why Render?
✅ Free tier with generous limits
✅ PostgreSQL database included
✅ Automatic deployments from GitHub
✅ No credit card required initially
✅ Best for full-stack apps

---

## Part 1: Deploy PostgreSQL Database

### Step 1: Create Render Account
1. Go to https://render.com/
2. Click **"Sign up"** → **"Continue with GitHub"**
3. Authorize Render to access your GitHub

### Step 2: Create PostgreSQL Database
1. Go to Dashboard → Click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `requirement-analyser-db`
   - **Database**: `requirement_analyser`
   - **User**: `admin`
   - **Region**: Choose closest to you
   - **Version**: Latest
3. Click **"Create Database"**
4. Wait 2-3 minutes for creation
5. **Copy the connection string** (looks like `postgresql://admin:password@host:5432/db`)

### Step 3: Create Database Tables
1. In your local backend, update `config/db.py` or `config/config.py`:
```python
# Use the Render DATABASE_URL
import os
DATABASE_URL = os.getenv("DATABASE_URL")
```

2. Run migration script:
```bash
cd backend
export DATABASE_URL="postgresql://admin:password@host:5432/db"
python migrate_db.py
```

3. Verify tables are created in database

---

## Part 2: Deploy Backend (Python FastAPI)

### Step 1: Create Web Service
1. Go to Render Dashboard → Click **"New +"** → **"Web Service"**
2. Click **"Connect your GitHub repository"**
3. Select **`requirement-analyser`** repo
4. Fill in:
   - **Name**: `requirement-analyser-api`
   - **Region**: Same as database
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python app.py`

### Step 2: Add Environment Variables
Click **"Environment"** and add:

```
DATABASE_URL=postgresql://admin:password@host:5432/db
API_SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-key
FLASK_ENV=production
PORT=10000
```

### Step 3: Configure CORS
Update `backend/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Add this after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "http://localhost:3000",  # Alt local
        "https://your-frontend-url.onrender.com",  # Replace with actual frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Start the server
3. Wait 5-10 minutes for deployment
4. Copy the backend URL (looks like `https://requirement-analyser-api.onrender.com`)

---

## Part 3: Deploy Frontend (React + Vite)

### Step 1: Update Vite Config
Make sure `frontend/vite.config.js` has correct base path:

```javascript
export default defineConfig({
  plugins: [react()],
  base: "/",  // Change from "/requirement-analyser/" since not subdirectory
  server: {
    port: 5173,
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  }
});
```

### Step 2: Create Static Site
1. Go to Render Dashboard → Click **"New +"** → **"Static Site"**
2. Click **"Connect your GitHub repository"**
3. Select **`requirement-analyser`** repo
4. Fill in:
   - **Name**: `requirement-analyser`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

### Step 3: Add Environment Variables
1. Click **"Environment"**
2. Add: `VITE_API_BASE=https://requirement-analyser-api.onrender.com`
   (Replace with your actual backend URL from Step 2)

### Step 4: Deploy
1. Click **"Create Static Site"**
2. Wait 3-5 minutes
3. Your site will be live at: `https://requirement-analyser.onrender.com`

---

## Step 4: Update Frontend API Configuration

### Option A: Using Environment Variables
Create `frontend/.env.production`:
```
VITE_API_BASE=https://requirement-analyser-api.onrender.com
```

### Option B: Automatic Detection
The frontend will use the environment variable from Render's build settings.

---

## Complete Deployment Checklist

### Backend Setup
- [ ] PostgreSQL database created on Render
- [ ] Database connection string copied
- [ ] `backend/app.py` has CORS configured for frontend URL
- [ ] Web Service created with correct build/start commands
- [ ] All environment variables set (DATABASE_URL, API keys, etc.)
- [ ] Backend URL copied (e.g., `https://requirement-analyser-api.onrender.com`)

### Frontend Setup
- [ ] `frontend/vite.config.js` has `base: "/"`
- [ ] Static Site created with correct build command
- [ ] `VITE_API_BASE` set to backend URL
- [ ] Frontend URL copied (e.g., `https://requirement-analyser.onrender.com`)

### Testing
- [ ] Visit frontend URL in browser
- [ ] Try uploading a file
- [ ] Try generating epics → should see data in table
- [ ] Try generating stories → should see data in table
- [ ] Try generating QA → should see data in table
- [ ] Try generating test plan → should see data in table
- [ ] Check browser console for errors

---

## Important Files to Update

### 1. `backend/app.py` - CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://requirement-analyser.onrender.com",  # Your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. `backend/config/config.py` or `backend/config/db.py` - Database URL
```python
import os

# Use Render's DATABASE_URL environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/requirement_analyser"  # Fallback for local dev
)
```

### 3. `backend/requirements.txt` - Ensure Has All Dependencies
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-multipart
python-dotenv
google-generativeai
flask-cors
# ... other deps
```

---

## Troubleshooting

### Frontend shows 404
- [ ] Verify Static Site build command is: `cd frontend && npm install && npm run build`
- [ ] Check Publish Directory is: `frontend/dist`
- [ ] Hard refresh page (Cmd+Shift+R)

### API calls failing (CORS errors)
- [ ] Check backend CORS includes frontend URL
- [ ] Check `VITE_API_BASE` is set correctly in frontend environment
- [ ] Check backend is running (visit backend URL in browser)

### Backend won't start
- [ ] Check PostgreSQL database is created and DATABASE_URL is correct
- [ ] View logs: Click service → "Logs" tab
- [ ] Verify all environment variables are set

### Database connection failing
- [ ] Copy entire connection string from Render PostgreSQL dashboard
- [ ] Paste into DATABASE_URL environment variable (no quotes)
- [ ] Test locally first: `psql postgresql://admin:pwd@host:5432/db`

### File uploads not working
- [ ] Backend needs write permissions to storage directory
- [ ] Update `backend/routes/upload.py` to use `/tmp` for Render:
```python
UPLOAD_DIR = "/tmp/uploads"  # Use temp directory on Render
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

---

## After Deployment

### Access Your App
- **Frontend**: https://requirement-analyser.onrender.com
- **Backend API**: https://requirement-analyser-api.onrender.com

### Monitor & Logs
1. Go to Render Dashboard
2. Click on service (frontend or backend)
3. View **"Logs"** tab to see deployment or runtime errors

### Update Code
1. Push changes to GitHub
2. Render automatically redeploys
3. Watch "Deployments" tab to see progress

### Scale Your App
- As usage grows, upgrade from free tier
- Render gives you friendly upgrade prompts

---

## Free Tier Limits

| Resource | Limit |
|----------|-------|
| Web Services | 1 free instance (spins down after 15 min inactivity) |
| Static Sites | Unlimited |
| PostgreSQL | 256 MB free database |
| Bandwidth | Limited |
| Compute | Shared resources |

⚠️ **Note**: Web services spin down after 15 minutes of inactivity. First request after sleep takes 30 seconds to wake up.

---

## Next Steps

1. **Sign up at Render**: https://render.com/
2. **Create PostgreSQL database** (Part 1)
3. **Deploy backend** (Part 2)
4. **Deploy frontend** (Part 3)
5. **Test everything works**
6. **Share your live URL!**

---

## Support

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/

Happy deploying! 🚀
