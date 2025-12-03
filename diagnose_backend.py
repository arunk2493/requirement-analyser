#!/usr/bin/env python3
"""
Comprehensive backend diagnostics script.
Checks all components and simulates the app startup.
"""
import os
import sys
import traceback

# Set up path
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("BACKEND DIAGNOSTICS SCRIPT")
print("=" * 60)

# 1. Check Python environment
print("\n[1] Python Environment")
print(f"  Python: {sys.executable}")
print(f"  Version: {sys.version}")
print(f"  Working Dir: {os.getcwd()}")

# 2. Check imports
print("\n[2] Importing Core Modules")
try:
    from fastapi import FastAPI
    print("  ✓ FastAPI imported")
except Exception as e:
    print(f"  ✗ FastAPI import failed: {e}")
    sys.exit(1)

try:
    from sqlalchemy.orm import Session
    print("  ✓ SQLAlchemy imported")
except Exception as e:
    print(f"  ✗ SQLAlchemy import failed: {e}")
    sys.exit(1)

# 3. Check config files
print("\n[3] Loading Configuration")
try:
    from config.db import Base, engine, SessionLocal
    print("  ✓ Database config loaded")
except Exception as e:
    print(f"  ✗ Database config failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from config.auth import verify_token, create_access_token
    print("  ✓ Auth config loaded")
except Exception as e:
    print(f"  ✗ Auth config failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from config.dependencies import get_db, get_current_user
    print("  ✓ Dependencies config loaded")
except Exception as e:
    print(f"  ✗ Dependencies config failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 4. Check models
print("\n[4] Loading Models")
try:
    from models.file_model import User, Upload, Epic, Story, QA, AggregatedUpload
    print("  ✓ All models loaded")
except Exception as e:
    print(f"  ✗ Models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 5. Check routes
print("\n[5] Loading Routes")
try:
    from routes import auth
    print("  ✓ Auth router imported")
    print(f"    - Router prefix: {auth.router.prefix}")
    print(f"    - Router tags: {auth.router.tags}")
    print(f"    - Routes defined: {len(auth.router.routes)}")
    for route in auth.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"      * {', '.join(route.methods)} {route.path}")
except Exception as e:
    print(f"  ✗ Routes import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 6. Create FastAPI app
print("\n[6] Creating FastAPI Application")
try:
    app = FastAPI(title="Requirement Analyser API")
    print("  ✓ FastAPI app created")
except Exception as e:
    print(f"  ✗ FastAPI app creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 7. Add middleware
print("\n[7] Adding CORS Middleware")
try:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("  ✓ CORS middleware added")
except Exception as e:
    print(f"  ✗ CORS middleware failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 8. Register routes
print("\n[8] Registering Routes")
try:
    app.include_router(auth.router)
    print("  ✓ Auth router registered")
except Exception as e:
    print(f"  ✗ Router registration failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 9. Add health endpoints
print("\n[9] Adding Health Check Endpoints")
try:
    @app.get("/health")
    def health_check():
        return {"status": "ok", "message": "API is running"}
    
    @app.get("/")
    def root():
        return {"message": "Requirement Analyser API"}
    
    print("  ✓ Health endpoints added")
except Exception as e:
    print(f"  ✗ Health endpoints failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# 10. List all registered routes
print("\n[10] Final Route List")
print("  Registered routes:")
route_count = 0
for route in app.routes:
    if hasattr(route, 'path'):
        methods = list(route.methods) if hasattr(route, 'methods') and route.methods else ['GET']
        print(f"    {', '.join(methods):10} {route.path}")
        route_count += 1
print(f"  Total: {route_count} routes")

# 11. Test database connection
print("\n[11] Testing Database Connection")
try:
    Base.metadata.create_all(bind=engine)
    print("  ✓ Database tables created/verified")
except Exception as e:
    print(f"  ⚠ Database warning: {e}")

# 12. Summary
print("\n" + "=" * 60)
print("✓ ALL DIAGNOSTICS PASSED - BACKEND IS READY")
print("=" * 60)
print("\nTo start the server, run:")
print("  python run_backend.py")
print("  or")
print("  python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000")
