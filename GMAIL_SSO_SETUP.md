# Gmail SSO Setup Guide

## Overview

Your application now supports Gmail Single Sign-On (SSO) integration using Google OAuth 2.0. Users can log in with their Gmail accounts instead of creating a new password.

## Features

✅ **Gmail Login Button** - Prominent "Continue with Google" button on login page
✅ **Automatic Account Creation** - First-time Google login automatically creates account
✅ **Zero Password Required** - Google users don't need to set passwords
✅ **Seamless Integration** - Works alongside email/password authentication
✅ **Secure Token Exchange** - OAuth 2.0 authorization code flow
✅ **User Profile Import** - Imports name and email from Google

## Prerequisites

1. Google Cloud Console account
2. Created Google OAuth 2.0 credentials
3. Frontend running on `http://localhost:5173`
4. Backend running on `http://localhost:8000`

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 1.2 Create a New Project

```
1. Click on the project dropdown at the top
2. Click "NEW PROJECT"
3. Enter project name: "Requirement Analyzer"
4. Click "CREATE"
5. Wait for project to be created (usually takes a minute)
```

### 1.3 Enable Google+ API

```
1. In the left sidebar, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it
4. Click "ENABLE"
```

### 1.4 Create OAuth 2.0 Credentials

```
1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. You might see: "You will need to create a consent screen first"
   - Click "CREATE CONSENT SCREEN"
   - Select "External"
   - Click "CREATE"
```

### 1.5 Configure OAuth Consent Screen

```
1. Fill in the form:
   - App name: "Requirement Analyzer"
   - User support email: your@email.com
   - Developer contact: your@email.com
2. Click "SAVE AND CONTINUE"
3. Skip "Scopes" (click "SAVE AND CONTINUE")
4. Skip "Test users" (click "SAVE AND CONTINUE")
5. Review and click "BACK TO DASHBOARD"
```

### 1.6 Create OAuth 2.0 Client ID

```
1. Go back to "Credentials" tab
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. Select "Web application"
4. Fill in:
   - Name: "Requirement Analyzer Web"
5. Under "Authorized redirect URIs", add:
   - http://localhost:5173/auth/callback
   - http://localhost:8000/auth/google/callback (optional for future)
6. Click "CREATE"
7. Copy the credentials (you'll need them next)
```

## Step 2: Configure Your Application

### 2.1 Update `.env` File

Create or update `.env` file in project root:

```bash
# Existing variables
POSTGRES_URL="postgresql://user:password@localhost/dbname"
GEMINI_API_KEY="your_gemini_key"

# Add Google OAuth variables
GOOGLE_CLIENT_ID="YOUR_CLIENT_ID_FROM_GOOGLE_CLOUD"
GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET_FROM_GOOGLE_CLOUD"
GOOGLE_REDIRECT_URI="http://localhost:5173/auth/callback"
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `google-auth-oauthlib` - Google OAuth library
- `google-auth-httplib2` - HTTP utilities
- `google-auth` - Google authentication
- `PyJWT` - JWT token handling

## Step 3: Backend Implementation

Your backend already includes:

✅ **`config/google_oauth.py`** - Google OAuth utility functions
- `get_google_login_url()` - Generates login URL
- `exchange_code_for_token()` - Exchanges auth code for tokens
- `get_user_info()` - Retrieves user profile from Google
- `validate_id_token()` - Validates ID token (optional)

✅ **Updated `routes/auth.py`** - New endpoints
- `GET /auth/google/login-url` - Returns login URL
- `POST /auth/google/callback` - Handles OAuth callback

✅ **Updated `models/file_model.py`** - User model
- Users created via Google have empty `hashed_password`
- Name and email imported from Google

## Step 4: Frontend Implementation

Your frontend already includes:

✅ **Updated `LoginPage.jsx`**
- "Continue with Google" button
- Google OAuth flow handling
- Auto-redirect on successful login

✅ **Updated `api/api.js`**
- `getGoogleLoginUrl()` - Fetches login URL
- `googleCallback()` - Handles callback

✅ **Updated `App.jsx`**
- Added `/auth/callback` route
- Passes `setIsAuthenticated` to LoginPage

## Step 5: Testing Gmail SSO

### 5.1 Start Backend and Frontend

**Terminal 1 - Backend:**
```bash
cd /Users/arunkumaraswamy/Documents/Study/requirement-analyser
python -m uvicorn app:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd /Users/arunkumaraswamy/Documents/Study/requirement-analyser/frontend
npm run dev
```

### 5.2 Test Login Flow

```
1. Open http://localhost:5173/login
2. Click "Continue with Google" button
3. Sign in with your Gmail account
4. Authorize the application
5. Auto-redirected to dashboard
6. User info stored in localStorage
```

### 5.3 Verify in Browser DevTools

```javascript
// Open DevTools Console and run:
console.log(localStorage.getItem('access_token'));
console.log(localStorage.getItem('user'));

// Should show:
// {
//   "user_id": 1,
//   "email": "your@gmail.com"
// }
```

## Troubleshooting

### "Invalid redirect URI"

**Problem:** You see error after clicking Google button

**Solution:**
1. Go to Google Cloud Console
2. Credentials → OAuth 2.0 Client IDs
3. Edit your web client
4. Make sure redirect URI matches exactly:
   - `http://localhost:5173/auth/callback` (local development)
   - `https://yourdomain.com/auth/callback` (production)

### "Client ID not configured"

**Problem:** Backend can't find `GOOGLE_CLIENT_ID` in environment

**Solution:**
```bash
# Make sure .env file exists in project root
cat .env | grep GOOGLE

# Should show:
# GOOGLE_CLIENT_ID=your_id
# GOOGLE_CLIENT_SECRET=your_secret
# GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
```

### "User email not verified"

**Problem:** Error during OAuth callback

**Solution:**
1. Make sure you're using a real Gmail account
2. Verify email in Google Account settings
3. Clear browser cache and try again

### "Redirect loop"

**Problem:** Redirecting back to login after OAuth

**Solution:**
1. Check browser console for error messages
2. Verify tokens stored in localStorage
3. Check backend logs for auth errors

## How It Works

### OAuth 2.0 Authorization Code Flow

```
1. User clicks "Continue with Google"
   ↓
2. Frontend fetches login URL from backend
   GET /auth/google/login-url
   ↓
3. Redirect to Google login page
   https://accounts.google.com/o/oauth2/v2/auth?...
   ↓
4. User logs in with Gmail credentials
   ↓
5. Google redirects back to app with authorization code
   http://localhost:5173/auth/callback?code=XXXX
   ↓
6. Frontend sends code to backend
   POST /auth/google/callback with {code}
   ↓
7. Backend exchanges code for Google access token
   ↓
8. Backend gets user profile from Google
   ↓
9. Backend finds or creates user in database
   ↓
10. Backend returns app tokens (JWT)
    ↓
11. Frontend stores tokens in localStorage
    ↓
12. User logged in, redirected to dashboard
```

### Database Changes

When a user logs in via Google:

```sql
-- New user created automatically
INSERT INTO users (email, full_name, hashed_password, is_active, created_at)
VALUES ('user@gmail.com', 'User Name', '', TRUE, NOW());

-- hashed_password is empty for Google users (no password auth)
-- is_active set to TRUE automatically
```

Subsequent Google logins:

```sql
-- Existing user is found and logged in
SELECT * FROM users WHERE email = 'user@gmail.com';
-- Return JWT tokens, user stays logged in
```

## Security Notes

### What's Protected

✅ Authorization code is short-lived (valid for ~10 minutes)
✅ Backend securely exchanges code for tokens
✅ Google access token never sent to frontend
✅ App generates own JWT tokens (can be short-lived)
✅ Refresh tokens stored securely in localStorage

### Best Practices

1. **Environment Variables** - Never hardcode credentials
2. **HTTPS in Production** - Always use HTTPS for OAuth
3. **Validate Redirect URIs** - Google strictly validates redirects
4. **Token Expiration** - Set reasonable token lifetimes
5. **Refresh Tokens** - Implement token refresh for long sessions

## Production Deployment

### Changes Needed for Production

1. **Update Redirect URI**
   ```
   GOOGLE_REDIRECT_URI="https://yourdomain.com/auth/callback"
   ```

2. **Update Credentials**
   - Add production domain to Google Cloud Console
   - Create separate OAuth client for production

3. **Enable HTTPS**
   ```
   # Google requires HTTPS for OAuth (except localhost)
   https://yourdomain.com/auth/callback
   ```

4. **Update CORS**
   ```python
   # In app.py
   origins = [
       "https://yourdomain.com",
       "https://www.yourdomain.com",
   ]
   ```

5. **Use Environment Secrets**
   ```
   # Use environment variables in production
   GOOGLE_CLIENT_SECRET stored in secure vault
   Not in code or .env file
   ```

## API Reference

### Get Login URL

**Endpoint:** `GET /auth/google/login-url`

**Response:**
```json
{
  "login_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=..."
}
```

### Google OAuth Callback

**Endpoint:** `POST /auth/google/callback`

**Request:**
```json
{
  "code": "authorization_code_from_google"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@gmail.com"
}
```

**Errors:**
```json
{
  "detail": "Failed to exchange authorization code"
}
```

## Advanced: Linking Gmail to Existing Account

To allow users to link Gmail to existing email/password account:

```python
# Future enhancement in routes/auth.py
@router.post("/auth/google/link")
def link_google_account(request: GoogleLoginRequest, current_user: TokenData = Depends(get_current_user)):
    """Link Google account to existing user"""
    user_info = get_user_info(access_token)
    
    # Link Google email to existing user
    # Prevents duplicate accounts
    
    return {"message": "Google account linked successfully"}
```

## Summary

✅ Gmail SSO fully integrated
✅ Frontend login page updated with Google button
✅ Backend OAuth 2.0 flow implemented
✅ Automatic account creation on first login
✅ Secure token exchange and validation
✅ User profile imported from Google

**Next Steps:**
1. Get Google OAuth credentials (see Step 1)
2. Add credentials to `.env` file (see Step 2)
3. Test login flow (see Step 5)
4. Deploy with production settings

**Support:** Refer to troubleshooting section above for common issues.
