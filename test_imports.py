#!/usr/bin/env python
"""
Test if the app starts correctly
"""
import sys
import traceback

print("Testing app startup...")

try:
    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")
    
    print("2. Importing database config...")
    from config.db import Base, engine, SessionLocal
    print("   ✓ Database config imported")
    
    print("3. Importing models...")
    from models.file_model import User
    print("   ✓ Models imported")
    
    print("4. Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Tables created")
    
    print("5. Importing auth config...")
    from config.auth import hash_password, verify_password, create_access_token
    print("   ✓ Auth config imported")
    
    print("6. Importing dependencies...")
    from config.dependencies import get_current_user, get_db
    print("   ✓ Dependencies imported")
    
    print("7. Importing auth routes...")
    from routes import auth
    print("   ✓ Auth routes imported")
    
    print("8. Checking router...")
    if hasattr(auth, 'router'):
        print(f"   ✓ Router found: {auth.router}")
        print(f"   ✓ Router prefix: {auth.router.prefix}")
        print(f"   ✓ Router routes: {len(auth.router.routes)}")
        for route in auth.router.routes:
            if hasattr(route, 'path'):
                print(f"      - {route.path}")
    else:
        print("   ✗ Router not found!")
    
    print("\n" + "=" * 60)
    print("✓ ALL IMPORTS SUCCESSFUL")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
