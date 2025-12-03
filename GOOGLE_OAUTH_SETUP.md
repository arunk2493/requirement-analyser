# 🔐 Gmail SSO Setup Guide

## Overview

This guide helps you set up Google OAuth 2.0 (Gmail SSO) for your application.

---

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 1.2 Create or Select a Project

1. Click **Select a Project** (top left)
2. Click **NEW PROJECT**
3. Enter project name: `requirement-analyser`
4. Click **CREATE**
5. Wait for creation to complete (may take 1-2 minutes)

### 1.3 Enable Google+ API

1. In the search bar, search for **"Google+ API"**
2. Click **Google+ API**
3. Click **ENABLE**

### 1.4 Create OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** (for testing)
3. Click **CREATE**
4. Fill in:
   - **App name:** `Requirement Analyser`
   - **User support email:** Your email
   - **Developer contact email:** Your email
5. Click **SAVE AND CONTINUE**
6. Click **SAVE AND CONTINUE** on Scopes page
7. Click **SAVE AND CONTINUE** on Test users page
8. Review and click **BACK TO DASHBOARD**

### 1.5 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Select **Web application**
4. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:5173/auth/callback
   http://localhost:5173/login
   ```
5. Click **CREATE**
6. A popup shows your credentials:
   - Copy **Client ID**
   - Copy **Client Secret**
   - Click **OK**

---

## Step 2: Add Credentials to `.env`

Edit `.env` file and add:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
```

**Example with real values:**
```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123xyz
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
```

---

## Step 3: Verify Backend is Running

The backend should automatically use the credentials from `.env`:

```bash
# Terminal 1 - Backend
python -m uvicorn app:app --reload

# Should see in logs:
# INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## Step 4: Test Gmail Login

### 4.1 Start Frontend

```bash
# Terminal 2 - Frontend
cd frontend
npm run dev

# Should see:
# Local: http://localhost:5173
```

### 4.2 Test Login Flow

1. Open browser to `http://localhost:5173`
2. Click **Login** (or it redirects automatically)
3. Click **Continue with Google** button
4. You should see **Google Login Page**
5. Enter your Google account email
6. Enter your Google account password
7. Click **Allow** to authorize
8. You should be **redirected back to dashboard**
9. Check localStorage for tokens:
   - Open DevTools → Application → localStorage
   - Should see: `access_token`, `refresh_token`, `user`

### 4.3 Verify Success

- Dashboard loads ✅
- User email shows in sidebar ✅
- Can access protected routes ✅
- Logout works ✅

---

## Troubleshooting

### ❌ "Failed to initiate Google login"

**Cause:** Google credentials not set in `.env`

**Fix:**
```bash
# Check .env has these values
grep GOOGLE_ .env

# If missing, add them (see Step 2)
```

### ❌ "Invalid Client ID"

**Cause:** Wrong Client ID copied

**Fix:**
1. Go back to Google Cloud Console
2. Go to **APIs & Services** → **Credentials**
3. Click your OAuth 2.0 client
4. Copy the correct **Client ID** again
5. Update `.env`

### ❌ Redirects to Google but then shows error

**Cause:** Redirect URI mismatch

**Fix:**
1. Go to Google Cloud Console → **Credentials**
2. Click your OAuth client
3. Ensure **Authorized redirect URIs** includes:
   ```
   http://localhost:5173/auth/callback
   ```
4. Click **SAVE**

### ❌ "Redirect URI mismatch" error from Google

**Cause:** Frontend redirect URI doesn't match Google settings

**Solutions:**
1. **For localhost development:**
   - In Google Console: `http://localhost:5173/auth/callback`
   - In `.env`: `GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback`

2. **For production:**
   - In Google Console: `https://yourdomain.com/auth/callback`
   - In `.env`: `GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback`

### ❌ Backend logs show "Google credentials not configured"

**Fix:**
```bash
# Verify .env exists and has values
cat .env | grep GOOGLE

# Restart backend
# Terminal 1:
# Kill: Ctrl+C
# Restart: python -m uvicorn app:app --reload
```

### ❌ Frontend blank page with console errors

**Fix:**
1. Open DevTools → Console
2. Look for errors
3. If "Cannot read property 'login_url'":
   - Backend not running
   - Or Google credentials missing
   - **Solution:** Check backend logs

### ❌ "User account is inactive"

**Cause:** User created but marked inactive in database

**Fix:**
```bash
# In postgres:
UPDATE users SET is_active = TRUE WHERE email = 'your@email.com';
```

---

## API Reference

### Get Google Login URL

**Endpoint:** `GET /auth/google/login-url`

**Response:**
```json
{
  "login_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&..."
}
```

**Error Response (500):**
```json
{
  "detail": "Google OAuth credentials not configured..."
}
```

---

### Handle Google Callback

**Endpoint:** `POST /auth/google/callback`

**Request:**
```json
{
  "code": "4/0AY-..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@gmail.com"
}
```

**Error Response (400):**
```json
{
  "detail": "Failed to exchange authorization code with Google..."
}
```

---

## Production Deployment

### Prerequisites

1. **Domain name** (e.g., `app.example.com`)
2. **SSL certificate** (HTTPS required)
3. **Updated Google credentials**

### Steps

1. **Update Google Console**
   ```
   Authorized redirect URIs:
   - https://app.example.com/auth/callback
   ```

2. **Update `.env` on server**
   ```env
   GOOGLE_CLIENT_ID=your_production_client_id
   GOOGLE_CLIENT_SECRET=your_production_secret
   GOOGLE_REDIRECT_URI=https://app.example.com/auth/callback
   ```

3. **Update frontend config** (optional, if hardcoded)
   ```javascript
   const API_BASE = "https://api.example.com";
   ```

4. **Restart services**
   ```bash
   # Backend
   gunicorn app:app

   # Frontend
   npm run build
   # Serve via nginx or similar
   ```

---

## Testing Checklist

- [ ] Google credentials added to `.env`
- [ ] Backend running (`python -m uvicorn app:app --reload`)
- [ ] Frontend running (`npm run dev`)
- [ ] Can see "Continue with Google" button
- [ ] Clicking button redirects to Google login
- [ ] Can login with Google account
- [ ] Redirected back to dashboard
- [ ] Tokens stored in localStorage
- [ ] User email shows in sidebar
- [ ] Can access protected routes
- [ ] Can logout successfully
- [ ] Login again works

---

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. Click "Continue with Google"
       │ GET /auth/google/login-url
       ↓
┌────────────────────┐        2. Redirect to Google
│   Your Backend     │─────────→ accounts.google.com
└────────────────────┘
       ↑
       │ 5. Return tokens
       │ POST /auth/google/callback
       │
┌──────────────┐
│   Google     │
│   OAuth      │──────→ User enters credentials
│   Server     │        and grants permission
└──────────────┘
       │
       │ 3. Authorization code
       ↓
    Browser ──→ 4. POST /callback with code
```

---

## Common Issues & Solutions

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| "Failed to initiate Google login" | Missing .env credentials | Add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET |
| "Redirect URI mismatch" | URI mismatch in Google Console | Update Google Console + .env to match |
| Blank page after Google login | Backend not running | Verify `python -m uvicorn app:app --reload` |
| "Invalid Client ID" | Wrong credentials copied | Recopy from Google Console |
| "User not found" | New user first login | Database auto-creates on first Google login |

---

## Support

If you encounter issues:

1. **Check backend logs:** Look for error messages in terminal running `uvicorn`
2. **Check frontend console:** DevTools → Console tab
3. **Check Google Console:** Verify credentials and redirect URIs
4. **Check .env:** Ensure all GOOGLE_* variables are set
5. **Check database:** Verify user was created: `SELECT * FROM users;`

---

## Next Steps

✅ Gmail SSO is now enabled!

**Try:**
- Register with email/password
- Login with Gmail
- Switch between both methods
- Test token refresh (wait 30+ min)
- Test logout and re-login

Happy authenticating! 🎉
