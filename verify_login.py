#!/usr/bin/env python
"""
Verification script to check if the login module is properly set up
"""
import sys
import traceback

print("=" * 60)
print("LOGIN MODULE VERIFICATION")
print("=" * 60)

# Check imports
print("\n1. Checking imports...")
try:
    from config.auth import (
        hash_password, verify_password, 
        create_access_token, create_refresh_token, 
        verify_token, Token, TokenData
    )
    print("   ✓ config/auth.py imports successful")
except Exception as e:
    print(f"   ✗ config/auth.py error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from config.dependencies import get_current_user, get_db
    print("   ✓ config/dependencies.py imports successful")
except Exception as e:
    print(f"   ✗ config/dependencies.py error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from routes import auth
    print("   ✓ routes/auth.py imports successful")
except Exception as e:
    print(f"   ✗ routes/auth.py error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Check database setup
print("\n2. Checking database setup...")
try:
    from config.db import Base, engine, SessionLocal
    from models.file_model import User
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("   ✓ Database tables created successfully")
    
    # Check if User table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'users' in tables:
        print("   ✓ Users table exists in database")
        columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"   ✓ User columns: {', '.join(columns)}")
    else:
        print("   ✗ Users table NOT found in database")
        print(f"   Available tables: {', '.join(tables)}")
except Exception as e:
    print(f"   ✗ Database error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Check auth router
print("\n3. Checking auth routes...")
try:
    if hasattr(auth, 'router'):
        print("   ✓ Auth router exists")
        
        # Check routes
        routes = [route.path for route in auth.router.routes if hasattr(route, 'path')]
        expected = ['/auth/register', '/auth/login', '/auth/refresh-token', '/auth/me']
        
        for route in expected:
            if route in routes:
                print(f"   ✓ Route {route} registered")
            else:
                print(f"   ✗ Route {route} NOT found")
    else:
        print("   ✗ Auth router not found")
except Exception as e:
    print(f"   ✗ Auth routes error: {e}")
    traceback.print_exc()

# Check token functions
print("\n4. Checking token functions...")
try:
    # Test password hashing
    test_pwd = "testpassword123"
    hashed = hash_password(test_pwd)
    verified = verify_password(test_pwd, hashed)
    
    if verified:
        print("   ✓ Password hashing/verification works")
    else:
        print("   ✗ Password verification failed")
except Exception as e:
    print(f"   ✗ Password functions error: {e}")
    traceback.print_exc()

try:
    # Test token generation
    token = create_access_token(user_id=1, email="test@example.com")
    verified_token = verify_token(token)
    
    if verified_token and verified_token.user_id == 1 and verified_token.email == "test@example.com":
        print("   ✓ Token generation/verification works")
    else:
        print("   ✗ Token verification failed")
except Exception as e:
    print(f"   ✗ Token functions error: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nTo test the API:")
print("1. Start backend: python -m uvicorn app:app --reload")
print("2. Test register: POST http://localhost:8000/auth/register")
print("3. Test login: POST http://localhost:8000/auth/login")
print("=" * 60)
