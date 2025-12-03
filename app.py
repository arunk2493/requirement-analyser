from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import traceback

# Initialize database first
try:
    from config.db import Base, engine
    # Import all models so they're registered with Base
    from models.file_model import User, Upload, Epic, Story, QA, AggregatedUpload
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
except Exception as e:
    print(f"✗ Database error: {e}")
    traceback.print_exc()

# Import routes after database is initialized
try:
    from routes import upload, generateStories, generateEpics, generateQA, listFiles, generateTestPlan, getEpics, getStories, getQA, getTestPlan, auth
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
    app.include_router(auth.router)
    app.include_router(upload.router)
    app.include_router(generateStories.router)
    app.include_router(generateEpics.router)
    app.include_router(generateQA.router)
    app.include_router(listFiles.router)
    app.include_router(generateTestPlan.router)
    app.include_router(getEpics.router)
    app.include_router(getStories.router)
    app.include_router(getQA.router)
    app.include_router(getTestPlan.router)
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
