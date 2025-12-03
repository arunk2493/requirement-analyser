# Login Module Setup Complete

## Overview
Complete email/password authentication system has been set up with JWT tokens.

## Backend Components

### 1. **config/auth.py** - Authentication Utilities
- `hash_password()` - Bcrypt password hashing (72-byte limit safe)
- `verify_password()` - Bcrypt password verification
- `create_access_token()` - 30-minute JWT access tokens
- `create_refresh_token()` - 7-day JWT refresh tokens
- `verify_token()` - JWT token validation
- `Token` and `TokenData` models

### 2. **config/dependencies.py** - Route Protection
- `get_current_user()` - Extracts and validates Bearer token from Authorization header
- `get_current_user_with_db()` - Extends above with database User lookup
- `get_db()` - Database session dependency
- Uses FastAPI's HTTPBearer security scheme

### 3. **routes/auth.py** - Authentication Endpoints
```
POST /auth/register - Register new user
POST /auth/login - Login user  
POST /auth/refresh-token - Refresh access token
GET /auth/me - Get current user profile
```

### 4. **models/file_model.py** - User Model
```python
User(
  id: int (Primary Key)
  email: str (Unique)
  hashed_password: str
  full_name: str (Optional)
  is_active: bool (Default: True)
  created_at: timestamp
  updated_at: timestamp
)
```

## Frontend Components

### 1. **src/components/LoginPage.jsx** - Login/Register UI
- Email/password login and registration
- Form tab switching
- Error message display
- Loading states
- Responsive design with Tailwind CSS

### 2. **src/api/api.js** - API Client with Token Management
- `setAuthToken()` - Store token in localStorage and axios headers
- `clearAuthToken()` - Remove token from storage and headers
- Request interceptor - Automatically adds Bearer token
- Response interceptor - Auto-refresh on 401 errors
- Auth endpoints: `registerUser()`, `loginUser()`, `getCurrentUser()`

### 3. **src/App.jsx** - Protected Routes
- ProtectedRoute wrapper component
- Authentication check on app load
- Login page for unauthenticated users
- Redirect to login on 401 errors

### 4. **src/components/Sidebar.jsx** - User Info & Logout
- Display logged-in user email
- Logout button with token cleanup
- Dark mode toggle
- Version info

## Database
- PostgreSQL with SQLAlchemy ORM
- `users` table auto-created on app startup
- Cascading deletes for data integrity

## Security Features
- **Password Hashing**: Bcrypt with 12 salt rounds
- **JWT Tokens**: HS256 algorithm with secret key
- **Token Refresh**: 7-day refresh tokens for extended sessions
- **Bearer Authentication**: Standard HTTP Authorization header
- **Password Limits**: 72-byte truncation (bcrypt requirement)
- **Unique Emails**: Enforced at database level

## Flow

### Registration
1. User fills email, password, full name
2. Backend hashes password with bcrypt
3. Creates User in database
4. Returns access_token + refresh_token
5. Frontend stores tokens in localStorage
6. Axios interceptors automatically add Bearer token to requests
7. Redirects to dashboard

### Login
1. User provides email and password
2. Backend verifies against hashed password in DB
3. Returns access_token + refresh_token
4. Frontend stores tokens and redirects

### Token Refresh
1. Access token expires (30 minutes)
2. Axios interceptor detects 401 response
3. Automatically calls refresh endpoint with refresh token
4. Gets new access_token
5. Retries original request
6. Falls back to login if refresh fails

### Protected Routes
1. All API endpoints require valid Bearer token
2. Frontend routes protected by authentication check
3. Unauthenticated users redirected to /login

## Environment Setup Required
```bash
# Backend requires these installed:
pip install python-jose[cryptography] bcrypt email-validator PyJWT

# These are in requirements.txt already
```

## Testing the System

### 1. Start Backend
```bash
python -m uvicorn app:app --reload
```
Expected output:
- ✓ Database tables created successfully
- ✓ All routes imported successfully
- ✓ All routers registered successfully

### 2. Start Frontend
```bash
npm run dev
```

### 3. Test Registration
1. Navigate to http://localhost:5173/login
2. Click "Create Account" tab
3. Fill email, password, name
4. Click "Create Account"
5. Should redirect to dashboard

### 4. Test Login
1. Click "Sign In" tab
2. Use same email/password from registration
3. Should redirect to dashboard

### 5. Test Logout
1. Click "Logout" button in sidebar
2. Should redirect to /login

### 6. Test Token Refresh
- Close app, clear localStorage manually
- Login again
- Wait for access token to expire (30 min)
- Next API call should auto-refresh
- Or manually set token to expire and make request

## All Protected Routes
The following endpoints now require authentication:
- POST /upload
- GET /uploads
- GET /epics
- GET /epics/{id}
- POST /generate-epics/{upload_id}
- GET /stories
- GET /stories/{epic_id}
- POST /generate-stories/{epic_id}
- GET /qa
- GET /qa/{story_id}
- POST /generate-qa/{story_id}
- GET /testplans
- POST /generate-testplan/{epic_id}
- And all other protected endpoints

## Troubleshooting

### "Invalid or expired token"
- Check token in localStorage
- Verify it hasn't expired
- Try logging in again

### "Email already registered"
- Use different email for registration
- Or login with existing email

### "Bearer token not found"
- Check Authorization header is being sent
- Verify axios interceptor is running
- Check localStorage has 'token' key

### Database errors
- Verify POSTGRES_URL is set in .env
- Check database is running
- Run: `python -m uvicorn app:app --reload` to recreate tables

## Notes
- Secret key in config/auth.py should be changed in production
- Token expiry times can be adjusted in config/auth.py
- Password complexity requirements can be added to registration validation
- Email verification can be added later if needed
- MFA support can be added in future updates
