# 🔐 Authentication System - Visual Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     REQUIREMENT ANALYSER                         │
│                   WITH JWT AUTHENTICATION                        │
└─────────────────────────────────────────────────────────────────┘

                          USER BROWSER
                              │
                              │
                    ┌─────────▼─────────┐
                    │   Login Page      │
                    │  (React Component)│
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Register/Login   │
                    │   /auth routes    │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
       ┌────▼────┐      ┌─────▼────┐      ┌───▼────┐
       │Register │      │  Login   │      │ Refresh│
       │  Token  │      │  Token   │      │ Token  │
       └────┬────┘      └─────┬────┘      └───┬────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  localStorage     │
                    │ - access_token    │
                    │ - refresh_token   │
                    │ - user info       │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Axios Interceptor│
                    │ Auto-add headers  │
                    │ Auto-refresh      │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼──────────────────┐
                    │   Protected API Calls      │
                    │ Authorization: Bearer ... │
                    └─────────┬──────────────────┘
                              │
                  ┌───────────┴───────────┐
                  │                       │
            ┌─────▼─────┐         ┌──────▼──────┐
            │ FastAPI   │         │  Database   │
            │ Backend   │         │  (Users)    │
            │           │         │             │
            │ Auth      │         │  id, email, │
            │ Dependencies        │  password,  │
            │           │         │  is_active  │
            └─────┬─────┘         └──────┬──────┘
                  │                       │
            ┌─────▼─────────────────────┐│
            │  JWT Token Verification    ││
            │  Password Validation       ││
            │  Database Lookups          ││
            └────────────────────────────┘│
                                           │
                      ┌────────────────────┘
                      │
            ┌─────────▼──────────┐
            │  Protected Routes  │
            │  - /epics          │
            │  - /stories        │
            │  - /qa             │
            │  - /upload         │
            │  - /generate-*     │
            │  (all require token)
            └────────────────────┘
```

---

## Authentication Flow Sequence

### 1. Registration Flow
```
User                    Frontend              Backend
  │                       │                      │
  ├──Enter Details───────>│                      │
  │                       │──POST /auth/register│
  │                       │─────────────────────>│
  │                       │                      ├─Hash Password (bcrypt)
  │                       │                      ├─Create User in DB
  │                       │                      ├─Generate JWT Tokens
  │                       │<──Tokens + User ID──│
  │                       │                      │
  │<──Tokens Stored───────│                      │
  │                       │                      │
  │<──Redirect Dashboard──│                      │
  │                       │                      │
```

### 2. Login Flow
```
User                    Frontend              Backend
  │                       │                      │
  ├──Enter Credentials──->│                      │
  │                       │──POST /auth/login───>│
  │                       │                      ├─Lookup User
  │                       │                      ├─Verify Password
  │                       │                      ├─Generate Tokens
  │                       │<──Tokens + User ID──│
  │                       │                      │
  │<──Tokens Stored───────│                      │
  │                       │                      │
  │<──Redirect Dashboard──│                      │
  │                       │                      │
```

### 3. Protected API Call (Fresh Token)
```
User              Frontend          Interceptor        Backend
  │                  │                  │                │
  ├─Make API Call──>│                  │                │
  │                  │──Add Authorization:───────────>│
  │                  │  Bearer {token}  │                │
  │                  │                  │──Verify Token──│
  │                  │                  │<─Valid────────│
  │                  │<──Response───────────────────────│
  │<─Data Displayed──│                  │                │
  │                  │                  │                │
```

### 4. Protected API Call (Expired Token)
```
User              Frontend          Interceptor        Backend
  │                  │                  │                │
  ├─Make API Call──>│                  │                │
  │                  │──Add Old Token──────────────────>│
  │                  │                  │──Verify Token──│
  │                  │                  │<─401 Error────│
  │                  │<──401 Response──────────────────│
  │                  │                  │                │
  │                  │─Catch 401─────->│                │
  │                  │                  │──POST /refresh─│
  │                  │                  │─Refresh Token─>│
  │                  │                  │<─New Tokens────│
  │                  │                  │                │
  │                  │──Retry Request─────New Token────>│
  │                  │                  │──Verify Token──│
  │                  │                  │<─Valid────────│
  │                  │<──Response───────────────────────│
  │<─Data Displayed──│                  │                │
  │                  │                  │                │
```

### 5. Logout Flow
```
User                 Frontend              Backend
  │                    │                      │
  ├──Click Logout────->│                      │
  │                    │                      │
  │                    ├─Clear localStorage   │
  │                    │ - access_token       │
  │                    │ - refresh_token      │
  │                    │ - user info          │
  │                    │                      │
  │<──Redirect Login───│                      │
  │                    │                      │
```

---

## Technology Stack

### Backend
```
FastAPI          - Web framework
SQLAlchemy       - ORM for database
PyJWT (python-jose) - JWT token generation/validation
Passlib + Bcrypt - Password hashing
Pydantic         - Data validation
HTTPBearer       - Security scheme
```

### Frontend
```
React            - UI framework
React Router     - Navigation
Axios            - HTTP client
localStorage     - Token persistence
Tailwind CSS     - Styling
React Icons      - Icons
```

### Database
```
PostgreSQL       - Primary database
SQLAlchemy ORM   - Query builder
User table       - Stores user accounts
```

---

## File Dependency Graph

```
┌──────────────────────────────────────────────┐
│         AUTHENTICATION DEPENDENCIES           │
└──────────────────────────────────────────────┘

app.py
  │
  ├─── routes/auth.py
  │      ├─── config/auth.py (JWT utilities)
  │      ├─── models/file_model.py (User model)
  │      └─── config/db.py (Database connection)
  │
  ├─── config/dependencies.py
  │      ├─── config/auth.py (Token verification)
  │      └─── models/file_model.py (User lookup)
  │
  └─── routes/*.py (all other routes)
         └─── config/dependencies.py (Protection)

frontend/src/App.jsx
  ├─── components/LoginPage.jsx
  │      └─── api/api.js (Login/Register calls)
  │
  ├─── components/Sidebar.jsx
  │      └─── api/api.js (Logout function)
  │
  └─── api/api.js
         ├─── Axios interceptors
         ├─── localStorage management
         └─── Auth endpoints
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

---

## Token Structure

### JWT Payload (Access Token - 30 min)
```json
{
    "user_id": 1,
    "email": "user@example.com",
    "exp": 1703001600,
    "iat": 1702998000
}
```

### JWT Payload (Refresh Token - 7 days)
```json
{
    "user_id": 1,
    "email": "user@example.com",
    "exp": 1703603200,
    "iat": 1702998000
}
```

---

## Error Handling

```
┌─────────────────────────────────────────┐
│          ERROR RESPONSES                 │
└─────────────────────────────────────────┘

400: Email already registered
     Invalid email/password format
     
401: Invalid email or password
     Invalid or expired token
     User not found or inactive
     
403: User account is inactive
     
422: Validation error
     Missing required fields
     
500: Server error
     Database error
     Unexpected exception
```

---

## Security Measures

```
┌─────────────────────────────────────────┐
│       SECURITY IMPLEMENTATION           │
└─────────────────────────────────────────┘

✅ Password Hashing
   Algorithm: Bcrypt
   Cost Factor: 12
   Salted: Automatic

✅ Token Security
   Algorithm: HS256
   Signed: Yes
   Encrypted: Signing key secret

✅ Token Expiry
   Access: 30 minutes
   Refresh: 7 days
   Prevents: Indefinite access

✅ Route Protection
   Pattern: Dependency injection
   Validation: Per request
   Scope: All non-auth endpoints

✅ Password Validation
   On Login: Bcrypt verification
   On Register: Email check

✅ User Status
   Active Check: Per request
   Inactive: Returns 403
   Deactivation: Set is_active=0
```

---

## Deployment Architecture

```
┌────────────────────────────────────────────┐
│          PRODUCTION DEPLOYMENT             │
└────────────────────────────────────────────┘

Production Environment:
  │
  ├── Frontend (React)
  │   ├── Hosted on: Vercel/Netlify/AWS
  │   ├── Environment: NODE_ENV=production
  │   └── API Base: https://api.yourdomain.com
  │
  ├── Backend (FastAPI)
  │   ├── Hosted on: AWS/Heroku/DigitalOcean
  │   ├── Server: Gunicorn + Uvicorn
  │   ├── Environment: PYTHONENV=production
  │   └── SECRET_KEY: From environment variable
  │
  └── Database (PostgreSQL)
      ├── Hosted on: AWS RDS/DigitalOcean
      ├── Backups: Daily
      └── Replication: Enabled

Security:
  ✅ HTTPS Only
  ✅ Strong SECRET_KEY (production)
  ✅ Environment variables
  ✅ Firewall rules
  ✅ Rate limiting
  ✅ CORS configured
```

---

## Monitoring & Logging

```
Areas to Monitor:
  ├── Failed login attempts
  ├── Token refresh rate
  ├── API response times
  ├── Database connection pool
  ├── Error rates
  └── User registration rate

Recommended Tools:
  ├── Sentry (error tracking)
  ├── LogRocket (frontend monitoring)
  ├── Datadog (infrastructure)
  ├── New Relic (APM)
  └── CloudFlare (CDN + WAF)
```

---

## Performance Notes

```
Optimization Points:
  ├── Token validation: O(1) - cryptographic verification
  ├── User lookup: O(1) - indexed email column
  ├── Password verification: O(n) - bcrypt operation
  ├── Token refresh: Fast - no DB query needed
  └── Route protection: O(1) - dependency injection

Caching Opportunities:
  ├── User info: Redis cache (optional)
  ├── Token blacklist: Redis (logout security)
  └── User roles: Cache if using RBAC

Bottlenecks (if any):
  ├── Bcrypt password hashing (by design)
  ├── Database user lookups (solved by index)
  └── Token refresh requests (rare - 30min expiry)
```

---

This architecture provides **enterprise-grade security** with **excellent user experience**.

**Next Steps:**
1. ✅ Implementation complete
2. → Test the system
3. → Deploy to staging
4. → Configure for production
5. → Add Gmail OAuth (optional future enhancement)
