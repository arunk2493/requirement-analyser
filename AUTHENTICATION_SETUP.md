# Authentication Module Setup - Complete Implementation

## Overview

The authentication system has been successfully implemented with JWT tokens, password hashing, and user-file linking. This document provides a complete guide to the setup and troubleshooting.

## Architecture Overview

```
Frontend (React)
    ↓
Login/Register → JWT Token → localStorage
    ↓
All API Requests → Bearer Token Header
    ↓
Backend (FastAPI)
    ↓
Verify Token → Extract user_id → Process Request
    ↓
Database (PostgreSQL)
```

## Components Implemented

### 1. Backend Authentication Module

#### File: `/backend/config/auth.py`
- **Password Hashing**: Uses `pbkdf2_sha256` (from passlib)
  - Truncates passwords to 72 bytes (security best practice)
  - Automatically salts and hashes passwords
  - Resistant to rainbow table attacks

- **JWT Token Management**:
  - Algorithm: HS256
  - Contains: `email` and `user_id`
  - Expiration: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
  - Secret Key: From `SECRET_KEY` environment variable

- **Key Functions**:
  - `hash_password(password)` → Hashed password string
  - `verify_password(plain, hashed)` → Boolean
  - `create_access_token(email, user_id)` → JWT token string
  - `verify_token(token)` → TokenData object with email and user_id
  - `get_current_user(credentials)` → Dependency for protected routes

#### File: `/backend/routes/auth.py`
- **POST /auth/register**: Register new user
  - Input: `{name, email, password}`
  - Returns: `{access_token, token_type}`
  - Validates unique email
  - Creates user with hashed password
  - Generates JWT with user_id

- **POST /auth/login**: Login existing user
  - Input: `{email, password}`
  - Returns: `{access_token, token_type}`
  - Verifies email and password
  - Generates JWT with user_id

- **POST /auth/verify-token**: Verify JWT token
  - Input: `{token}`
  - Returns: `{email, id}`
  - Used for session validation

### 2. Frontend Authentication

#### File: `/frontend/src/components/LoginPage.jsx`
- Dual-mode form: Register and Login tabs
- Registration fields: Name, Email, Password
- Login fields: Email, Password
- Stores JWT token and user email in localStorage
- Handles registration and login errors with user feedback

#### File: `/frontend/src/App.jsx`
- Main routing component
- Checks for token on component mount
- Conditionally renders LoginPage or Dashboard
- Passes authentication state down to components

#### File: `/frontend/src/api/api.js`
- Axios instance with interceptors
- Request interceptor: Adds `Authorization: Bearer {token}` header
- Response interceptor: Clears localStorage on 401 errors
- All API calls use this configured instance

#### File: `/frontend/src/components/Sidebar.jsx`
- Displays user email
- Logout button clears localStorage and redirects to login

### 3. Database Schema

#### File: `/backend/models/file_model.py`

**Users Table**:
```sql
users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    created_at TIMESTAMP
)
```

**Uploads Table** (Updated):
```sql
uploads (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255),
    content JSONB,
    confluence_page_id VARCHAR(50),
    vectorstore_id VARCHAR(255),
    created_at TIMESTAMP
)
```

## Setup Instructions

### Step 1: Run Database Migrations

```bash
cd /Users/arunkumaraswamy/Documents/Study/requirement-analyser

# Add name column to users table (if needed)
python3 migrate_users_table.py

# Add user_id column to uploads table
python3 migrate_uploads_user_id.py
```

**Expected Output**:
```
✓ Column added as nullable
✓ Existing records assigned to default user (ID: 1)
✓ Foreign key constraint added
✓ Column set to NOT NULL
✓ Migration completed successfully!
```

### Step 2: Environment Configuration

Ensure `/backend/.env` has:
```env
POSTGRES_URL=postgresql://user:password@localhost:5432/requirement_db
SECRET_KEY=your-secret-key-change-in-production
```

### Step 3: Start Backend

```bash
cd /Users/arunkumaraswamy/Documents/Study/requirement-analyser/backend
pip install -r requirements.txt
uvicorn app:app --reload
```

**Verify Backend**:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Step 4: Start Frontend

```bash
cd /Users/arunkumaraswamy/Documents/Study/requirement-analyser/frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

### Step 5: Test Authentication Flow

1. **Register a New User**:
   - Go to Login page → Click "Register" tab
   - Enter: Name, Email, Password
   - Click "Register"
   - Should redirect to Dashboard

2. **Login Existing User**:
   - Go to Login page → Click "Login" tab
   - Enter: Email, Password
   - Click "Login"
   - Should redirect to Dashboard

3. **Upload File**:
   - Click "Upload" in Sidebar
   - Select a PDF or DOCX file
   - File should be uploaded successfully with user_id

4. **Logout**:
   - Click "Logout" in Sidebar
   - Should clear localStorage and redirect to Login

## API Security

### Protected Routes

All routes (except `/auth/*`) require a valid JWT token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/endpoint
```

### Current Protected Routes

- **POST /upload**: Upload files (requires user_id)
- **GET /uploads**: List user's uploads
- **GET /epics**: Get epics for uploads
- **GET /stories**: Get stories for uploads
- **GET /qa**: Get QA items
- **GET /test-plans**: Get test plans
- All agent routes

### Dependency Injection

Protected routes use FastAPI's dependency injection:

```python
@router.get("/endpoint")
def endpoint(current_user: TokenData = Depends(get_current_user)):
    # current_user.email - User's email
    # current_user.user_id - User's ID in database
    pass
```

## Troubleshooting

### Issue 1: "user_id is None" on Upload

**Problem**: User gets error `null value in column "user_id"`

**Causes**:
1. Old JWT token cached in localStorage (doesn't have user_id field)
2. Database migration not run
3. Backend code not updated

**Solution**:
```bash
# 1. Clear browser localStorage
# Open browser console and run:
localStorage.clear()
window.location.reload()

# 2. Login again to get new JWT with user_id
# 3. Try upload again
```

### Issue 2: "Invalid or expired token"

**Problem**: Getting 401 Unauthorized on protected routes

**Causes**:
1. Token expired (30-minute expiration)
2. Token is malformed
3. JWT secret key mismatch

**Solution**:
```bash
# 1. Check SECRET_KEY matches between frontend and backend
# 2. Login again to get fresh token
# 3. Verify .env file has correct SECRET_KEY
```

### Issue 3: "Email already registered"

**Problem**: Cannot register with an email that exists

**Solution**: Either:
1. Use a different email
2. Or delete the user from database:
   ```sql
   DELETE FROM users WHERE email = 'existing@email.com';
   ```

### Issue 4: Database Connection Error

**Problem**: Backend can't connect to PostgreSQL

**Causes**:
1. PostgreSQL not running
2. POSTGRES_URL not set in .env
3. Credentials incorrect

**Solution**:
```bash
# Check PostgreSQL is running
# macOS:
brew services list | grep postgres
brew services start postgresql

# Verify POSTGRES_URL in .env
# Test connection:
python3 -c "from config.db import engine; print(engine)"
```

### Issue 5: CORS Errors

**Problem**: Frontend can't reach backend API

**Solution**: Verify backend includes CORS middleware:
```python
# In /backend/app.py - middleware is already configured
# Allow origins include: http://localhost:5173
```

## Token Structure

### Registration Flow

1. User submits: `{name, email, password}`
2. Backend:
   - Hashes password using pbkdf2_sha256
   - Creates user in database
   - Gets user.id
   - Creates JWT: `{email, user_id, exp}`
   - Returns token

3. Frontend:
   - Stores token in localStorage
   - Stores email in localStorage
   - Uses token for future requests

### JWT Token Contents

```json
{
  "email": "user@example.com",
  "user_id": 1,
  "exp": 1234567890
}
```

### Token Extraction

When a protected route is called:
1. Frontend sends `Authorization: Bearer <token>` header
2. Backend's `get_current_user` dependency:
   - Extracts token from Authorization header
   - Decodes JWT (verifies signature)
   - Creates TokenData object with email and user_id
   - Returns to route handler

## Files Created/Modified

### New Files Created:
1. `/backend/routes/auth.py` - Authentication endpoints
2. `/backend/config/auth.py` - JWT and password handling
3. `/frontend/src/components/LoginPage.jsx` - Login/Register UI
4. `/migrate_users_table.py` - Database migration for users
5. `/migrate_uploads_user_id.py` - Database migration for uploads

### Files Modified:
1. `/backend/app.py` - Added auth router registration
2. `/backend/models/file_model.py` - Added User model, updated Upload with user_id FK
3. `/frontend/src/App.jsx` - Added authentication state management
4. `/frontend/src/api/api.js` - Added Bearer token interceptor
5. `/frontend/src/components/Sidebar.jsx` - Added logout functionality
6. `/backend/routes/upload.py` - Uses current_user.user_id

## Testing Checklist

- [ ] Backend starts without errors: `uvicorn app:app --reload`
- [ ] Frontend starts without errors: `npm run dev`
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] Registration creates user with name, email, hashed password
- [ ] Registration returns valid JWT token
- [ ] Login validates credentials and returns JWT token
- [ ] JWT token contains user_id field
- [ ] File upload links file to authenticated user
- [ ] Old uploads have user_id=1 (from migration)
- [ ] Logout clears localStorage and redirects to login
- [ ] Cannot access protected routes without token
- [ ] 401 error redirects to login page

## Security Considerations

1. **Password Hashing**: Uses industry-standard pbkdf2_sha256
2. **Token Expiration**: 30 minutes (short-lived for security)
3. **JWT Secret**: Change `SECRET_KEY` in production
4. **HTTPS**: Use HTTPS in production (not just localhost)
5. **Token Storage**: localStorage is vulnerable to XSS - consider httpOnly cookies for production
6. **Password Truncation**: 72-byte limit matches bcrypt standard

## Next Steps

1. Run migrations: `python3 migrate_uploads_user_id.py`
2. Clear browser cache/localStorage
3. Login to get fresh JWT with user_id
4. Test file upload
5. Verify user_id is saved in database

## Additional Features to Consider

1. **Password Reset**: Add /auth/forgot-password endpoint
2. **Refresh Tokens**: Implement 7-day refresh tokens
3. **User Profile**: Add GET /auth/profile endpoint
4. **User Search**: Add ability to search/list users
5. **Role-Based Access Control**: Add user roles and permissions
6. **2FA**: Add two-factor authentication
7. **Session Management**: Track user login sessions
8. **Audit Logging**: Log all authentication events

## Support

For issues or questions:
1. Check backend logs: `tail -f /Users/arunkumaraswamy/Documents/Study/requirement-analyser/backend/backend.log`
2. Check browser console for frontend errors
3. Check database logs for schema errors
4. Review token contents: Use jwt.io to decode token
