from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import traceback

# Add backend directory to path to avoid import conflicts with root-level folders
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Initialize database first
try:
    from backend.config.db import Base, engine
    # Import all models so they're registered with Base
    from backend.models.file_model import User, Upload, Epic, Story, QA, AggregatedUpload
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as db_error:
        print(f"⚠ Warning: Could not create database tables: {db_error}")
        print("  The database might not be accessible. Check POSTGRES_URL in .env")
except Exception as e:
    print(f"✗ Database error: {e}")
    traceback.print_exc()

# Import routes after database is initialized
try:
    from backend.routes import auth
    from backend.routes import upload, generateEpics, generateStories, generateQA
    from backend.routes import getEpics, getStories, getQA, getTestPlan, download, agents_router
    print("✓ All routes imported successfully")
except Exception as e:
    print(f"✗ Route import error: {e}")
    traceback.print_exc()
    sys.exit(1)

app = FastAPI(title="Requirement Analyser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers - auth first
try:
    app.include_router(auth.router, tags=["Authentication"])
    app.include_router(agents_router.router)
    app.include_router(upload.router, tags=["Upload"])
    app.include_router(generateEpics.router, tags=["Epics"])
    app.include_router(generateStories.router, tags=["Stories"])
    app.include_router(generateQA.router, tags=["QA"])
    app.include_router(getEpics.router, tags=["Epics"])
    app.include_router(getStories.router, tags=["Stories"])
    app.include_router(getQA.router, tags=["QA"])
    app.include_router(getTestPlan.router, tags=["Test Plans"])
    app.include_router(download.router, tags=["Download"])
    print("✓ All routers registered successfully")
except Exception as e:
    print(f"✗ Router registration error: {e}")
    traceback.print_exc()

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Requirement Analyser API", "docs": "/docs"}

@app.get("/api/endpoints")
def list_endpoints():
    """List all registered endpoints"""
    endpoints = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return {"endpoints": endpoints}

@app.get("/debug/auth")
def debug_auth():
    """Debug endpoint to test authentication"""
    return {
        "message": "Auth debug endpoint",
        "cors_origins": ["http://localhost:5173", "http://localhost:5174"],
        "endpoints": {
            "auth": "/auth/register, /auth/login, /auth/refresh-token, /auth/me",
            "upload": "/upload (POST), /uploads (GET)",
            "epics": "/epics (GET), /generate-epics/:id (POST)",
            "stories": "/stories (GET), /generate-stories/:id (POST)",
            "qa": "/qa (GET), /generate-qa/:id (POST)",
            "testplans": "/testplans (GET)"
        }
    }

# Print registered routes at startup
print("\n=== Registered Routes ===")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = list(route.methods) if hasattr(route, 'methods') and route.methods else ['GET']
        print(f"  {', '.join(methods):8} {route.path}")
print("========================\n")
