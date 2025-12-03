# API Authentication & Route Documentation

## Overview
All API routes have been updated with JWT authentication. Users must obtain a valid token by logging in before accessing any protected endpoints.

## Authentication Flow

### 1. Register a New User
**Endpoint:** `POST /auth/register`
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com"
}
```

### 2. Login Existing User
**Endpoint:** `POST /auth/login`
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as register endpoint

### 3. Get Current User Profile
**Endpoint:** `GET /auth/me`
**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

### 4. Refresh Access Token
**Endpoint:** `POST /auth/refresh-token`
```json
{
  "refresh_token": "<refresh_token_from_login>"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com"
}
```

## Protected API Routes

All protected routes require the `Authorization: Bearer <access_token>` header.

### Upload Management

#### Upload a File
**Endpoint:** `POST /upload`
**Authentication:** Required ✅
**Headers:** `Authorization: Bearer <token>`
**Body:** Multipart form data with file

**Response:**
```json
{
  "message": "File uploaded successfully",
  "upload_id": 1,
  "vectorstore_id": "vs_abc123"
}
```

#### Get All User Uploads
**Endpoint:** `GET /uploads?page=1&page_size=10`
**Authentication:** Required ✅
**Query Parameters:**
- `page` (default: 1) - Page number
- `page_size` (default: 10) - Items per page (max: 100)

**Response:**
```json
{
  "message": "Uploads retrieved successfully",
  "total_uploads": 5,
  "current_page": 1,
  "page_size": 10,
  "total_pages": 1,
  "uploads": [
    {
      "id": 1,
      "filename": "requirements.pdf",
      "created_at": "2025-01-15T10:30:00",
      "confluence_page_url": "https://confluence.example.com/pages/viewpage.action?pageId=123"
    }
  ]
}
```

### Epic Management

#### Generate Epics from Upload
**Endpoint:** `POST /generate-epics/{upload_id}`
**Authentication:** Required ✅
**Parameters:**
- `upload_id` - ID of the upload to generate epics from

**Response:**
```json
{
  "message": "Epics and test plans generated with Confluence pages",
  "upload_id": 1,
  "upload_folder_page_id": "123456",
  "epics": [
    {
      "id": 1,
      "name": "Epic_20250115_103000",
      "confluence_page_id": "789012",
      "test_plans": [
        {
          "id": 1,
          "content": { "title": "Test Plan", ... },
          "confluence_page_id": "345678"
        }
      ]
    }
  ]
}
```

#### Get Epics by Upload
**Endpoint:** `GET /epics/{upload_id}`
**Authentication:** Required ✅

**Response:**
```json
{
  "message": "Epics retrieved successfully",
  "upload_id": 1,
  "total_epics": 3,
  "epics": [
    {
      "id": 1,
      "name": "Epic_20250115_103000",
      "content": { "name": "Epic title", "description": "...", ... },
      "confluence_page_id": "123456",
      "confluence_page_url": "https://confluence.example.com/pages/viewpage.action?pageId=123456",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

#### Get All User Epics (Paginated)
**Endpoint:** `GET /epics?page=1&page_size=10&sort_by=created_at&sort_order=desc`
**Authentication:** Required ✅
**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 10, max: 100)
- `sort_by` (default: created_at) - Options: `id`, `created_at`
- `sort_order` (default: desc) - Options: `asc`, `desc`

#### Get Epic Details
**Endpoint:** `GET /epics/{upload_id}/{epic_id}`
**Authentication:** Required ✅

### Story Management

#### Generate Stories from Epic
**Endpoint:** `POST /generate-stories/{epic_id}`
**Authentication:** Required ✅
**Parameters:**
- `epic_id` - ID of the epic to break down into stories

**Response:**
```json
{
  "message": "Stories generated",
  "epic_id": 1,
  "stories": [
    {
      "id": 1,
      "story": {
        "name": "User story title",
        "type": "feature",
        "description": "As a user...",
        "acceptanceCriteria": ["criterion 1", "criterion 2"],
        "implementationDetails": "..."
      }
    }
  ]
}
```

#### Get Stories by Epic
**Endpoint:** `GET /stories/{epic_id}`
**Authentication:** Required ✅

**Response:**
```json
{
  "message": "Stories retrieved successfully",
  "epic_id": 1,
  "total_stories": 5,
  "stories": [
    {
      "id": 1,
      "name": "Story title",
      "content": { ... },
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

#### Get All User Stories (Paginated)
**Endpoint:** `GET /stories?page=1&page_size=10&sort_by=created_at&sort_order=desc`
**Authentication:** Required ✅

#### Get Story Details
**Endpoint:** `GET /stories/{epic_id}/{story_id}`
**Authentication:** Required ✅

### QA/Test Case Management

#### Generate QA Test Cases from Story
**Endpoint:** `POST /generate-qa/{story_id}`
**Authentication:** Required ✅
**Parameters:**
- `story_id` - ID of the story to generate QA test cases for

**Response:**
```json
{
  "message": "QA generated",
  "story_id": 1,
  "qa": [
    {
      "id": 1,
      "content": {
        "title": "Test Case 1",
        "apiEndpoint": "/api/endpoint",
        "method": "POST",
        "request": { ... },
        "response": { ... },
        "validationSteps": ["step 1", "step 2"],
        "automationScript": "..."
      }
    }
  ]
}
```

#### Get QA Tests by Story
**Endpoint:** `GET /qa/{story_id}`
**Authentication:** Required ✅

**Response:**
```json
{
  "message": "QA test cases retrieved successfully",
  "story_id": 1,
  "total_qa_tests": 3,
  "qa_tests": [
    {
      "id": 1,
      "content": { ... },
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

#### Get All User QA Tests (Paginated)
**Endpoint:** `GET /qa?page=1&page_size=10&sort_by=created_at&sort_order=desc`
**Authentication:** Required ✅

#### Get QA Test Details
**Endpoint:** `GET /qa/{story_id}/{qa_id}`
**Authentication:** Required ✅

### Test Plan Management

#### Get Test Plans by Epic
**Endpoint:** `GET /testplans/{epic_id}`
**Authentication:** Required ✅

**Response:**
```json
{
  "message": "Test plans retrieved successfully",
  "epic_id": 1,
  "total_test_plans": 2,
  "test_plans": [
    {
      "id": 1,
      "content": {
        "title": "Test Plan Title",
        "objective": "...",
        "preconditions": [...],
        "testScenarios": [...],
        "risks": [...],
        "mitigationStrategies": [...]
      },
      "confluence_page_id": "123456",
      "confluence_page_url": "https://confluence.example.com/pages/viewpage.action?pageId=123456",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

#### Get All User Test Plans (Paginated)
**Endpoint:** `GET /testplans?page=1&page_size=10&sort_by=created_at&sort_order=desc`
**Authentication:** Required ✅

#### Get Test Plan Details
**Endpoint:** `GET /testplans/{epic_id}/{testplan_id}`
**Authentication:** Required ✅

### Download & Export

#### Download Aggregated Data
**Endpoint:** `GET /download/{upload_id}?format=json`
**Authentication:** Required ✅
**Query Parameters:**
- `format` (default: json) - Options: `json`, `pdf`

**Response:** File download (application/json or application/pdf)

## Data Isolation

All API routes are protected and data-scoped to the authenticated user:

- **Uploads**: Only show uploads created by the current user
- **Epics**: Only show epics from the current user's uploads
- **Stories**: Only show stories from the current user's epics
- **QA**: Only show test cases from the current user's stories
- **Test Plans**: Only show test plans from the current user's epics
- **Downloads**: Only allow downloading files from the current user's uploads

### Example: Security Flow

```
User A logs in → Gets Token A
User A uploads file → File saved with user_id = A
User B logs in → Gets Token B
User B tries to access User A's file using `/uploads`
  → Only sees User B's uploads (isolation enforced)
```

## Token Details

### Access Token
- **Duration**: 30 minutes
- **Used for**: Accessing protected endpoints
- **Format**: JWT (JSON Web Token) with HS256 signature

### Refresh Token
- **Duration**: 7 days
- **Used for**: Obtaining new access tokens
- **Format**: JWT with HS256 signature

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing the issue"
}
```

## Testing with cURL

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'

# Get current user (replace TOKEN with actual token)
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN"

# Get uploads
curl -X GET "http://localhost:8000/uploads?page=1&page_size=10" \
  -H "Authorization: Bearer TOKEN"

# Upload file
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@/path/to/file.pdf"

# Generate epics
curl -X POST http://localhost:8000/generate-epics/1 \
  -H "Authorization: Bearer TOKEN"
```

## Changes Made

### Files Updated

1. **backend/routes/upload.py**
   - Added authentication to `/upload` (POST)
   - Added authentication to `/uploads` (GET)
   - Added `user_id` filtering for data isolation

2. **backend/routes/generateEpics.py**
   - Added authentication to `/generate-epics/{upload_id}` (POST)
   - Added user_id validation

3. **backend/routes/generateStories.py**
   - Added authentication to `/generate-stories/{epic_id}` (POST)
   - Added user_id validation

4. **backend/routes/generateQA.py**
   - Added authentication to `/generate-qa/{story_id}` (POST)
   - Added user_id validation

5. **backend/routes/getEpics.py**
   - Added authentication to all GET endpoints
   - Implemented user-scoped data filtering

6. **backend/routes/getStories.py**
   - Added authentication to all GET endpoints
   - Implemented user-scoped data filtering

7. **backend/routes/getQA.py**
   - Added authentication to all GET endpoints
   - Implemented user-scoped data filtering

8. **backend/routes/getTestPlan.py**
   - Added authentication to all GET endpoints
   - Implemented user-scoped data filtering

9. **backend/routes/download.py**
   - Added authentication to `/download/{upload_id}` (GET)
   - Added user_id validation

10. **app.py**
    - Registered all backend route modules
    - Added proper route prefixes and tags

11. **models/file_model.py**
    - Added `user_id` field to Upload model
    - Added foreign key relationship to User model

## Summary

✅ **Authentication**: All routes now require valid JWT tokens
✅ **Data Isolation**: Each user only sees their own data
✅ **Token Management**: Support for access and refresh tokens
✅ **User Tracking**: All uploads and generated content tracked by user
✅ **Error Handling**: Proper 401/403 responses for auth failures
✅ **Documentation**: Complete API documentation with examples
