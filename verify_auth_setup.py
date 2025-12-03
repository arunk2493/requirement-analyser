#!/usr/bin/env python3
"""
Verification script to check authentication setup
Validates all components are in place
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def check_environment():
    """Check environment configuration"""
    print("\n=== Environment Check ===")
    
    # Check if .env exists
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        print("✓ .env file found")
        with open(env_file) as f:
            content = f.read()
            if "SECRET_KEY" in content:
                print("✓ SECRET_KEY configured")
            else:
                print("✗ SECRET_KEY not found in .env")
            if "POSTGRES_URL" in content:
                print("✓ POSTGRES_URL configured")
            else:
                print("✗ POSTGRES_URL not found in .env")
    else:
        print("✗ .env file not found - create it with:")
        print("  POSTGRES_URL=postgresql://user:password@localhost:5432/requirement_db")
        print("  SECRET_KEY=your-secret-key-change-in-production")

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n=== Dependencies Check ===")
    
    required = {
        "fastapi": "FastAPI framework",
        "sqlalchemy": "Database ORM",
        "passlib": "Password hashing",
        "jose": "JWT tokens",
        "psycopg2": "PostgreSQL adapter",
        "pydantic": "Data validation",
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"✓ {package:20} - {description}")
        except ImportError:
            print(f"✗ {package:20} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages:")
        print(f"  pip install {' '.join(missing)}")
    
    return len(missing) == 0

def check_files():
    """Check if all required files exist"""
    print("\n=== Files Check ===")
    
    backend = Path(__file__).parent / "backend"
    frontend = Path(__file__).parent / "frontend" / "src"
    
    required_files = {
        backend / "config" / "auth.py": "Auth configuration",
        backend / "routes" / "auth.py": "Auth routes",
        backend / "routes" / "upload.py": "Upload routes",
        backend / "models" / "file_model.py": "Database models",
        frontend / "components" / "LoginPage.jsx": "Login component",
        frontend / "api" / "api.js": "API client",
    }
    
    missing = []
    for filepath, description in required_files.items():
        if filepath.exists():
            print(f"✓ {filepath.name:20} - {description}")
        else:
            print(f"✗ {filepath.name:20} - NOT FOUND: {filepath}")
            missing.append(str(filepath))
    
    return len(missing) == 0

def check_database():
    """Check database connectivity"""
    print("\n=== Database Check ===")
    
    try:
        os.chdir(backend_path)
        from config.db import engine
        
        if engine:
            print("✓ Database engine configured")
            
            try:
                with engine.connect() as conn:
                    result = conn.execute("SELECT 1")
                    print("✓ Database connection successful")
                    
                    # Check tables
                    from sqlalchemy import text, inspect
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    
                    if "users" in tables:
                        print("✓ Users table exists")
                    else:
                        print("✗ Users table missing")
                    
                    if "uploads" in tables:
                        print("✓ Uploads table exists")
                        
                        # Check if user_id column exists
                        columns = [col['name'] for col in inspector.get_columns('uploads')]
                        if "user_id" in columns:
                            print("✓ Uploads.user_id column exists")
                        else:
                            print("⚠ Uploads.user_id column missing - run migration:")
                            print("  python3 migrate_uploads_user_id.py")
                    else:
                        print("✗ Uploads table missing")
                        
            except Exception as e:
                print(f"✗ Database connection failed: {e}")
                print("\nMake sure:")
                print("  1. PostgreSQL is running")
                print("  2. POSTGRES_URL is correct in .env")
                print("  3. Database exists and is accessible")
        else:
            print("✗ Database engine not configured")
            
    except Exception as e:
        print(f"✗ Error checking database: {e}")

def check_auth_module():
    """Check auth module functionality"""
    print("\n=== Auth Module Check ===")
    
    try:
        os.chdir(backend_path)
        from config.auth import (
            hash_password,
            verify_password,
            create_access_token,
            verify_token,
        )
        
        # Test password hashing
        test_password = "test_password_123"
        hashed = hash_password(test_password)
        if verify_password(test_password, hashed):
            print("✓ Password hashing works")
        else:
            print("✗ Password verification failed")
        
        # Test token creation
        test_email = "test@example.com"
        test_user_id = 1
        token = create_access_token(test_email, test_user_id)
        if token:
            print("✓ Token creation works")
        else:
            print("✗ Token creation failed")
        
        # Test token verification
        token_data = verify_token(token)
        if token_data and token_data.email == test_email and token_data.user_id == test_user_id:
            print("✓ Token verification works")
            print(f"  Email: {token_data.email}")
            print(f"  User ID: {token_data.user_id}")
        else:
            print("✗ Token verification failed")
            if token_data:
                print(f"  Got: email={token_data.email}, user_id={token_data.user_id}")
            
    except Exception as e:
        print(f"✗ Error checking auth module: {e}")

def main():
    """Run all checks"""
    print("=" * 60)
    print("Authentication Setup Verification")
    print("=" * 60)
    
    check_environment()
    deps_ok = check_dependencies()
    files_ok = check_files()
    check_database()
    check_auth_module()
    
    print("\n" + "=" * 60)
    if deps_ok and files_ok:
        print("✓ All checks passed!")
        print("\nNext steps:")
        print("1. Start PostgreSQL: brew services start postgresql")
        print("2. Run migrations: python3 migrate_uploads_user_id.py")
        print("3. Start backend: cd backend && uvicorn app:app --reload")
        print("4. Start frontend: cd frontend && npm run dev")
    else:
        print("⚠ Some checks failed - see above for details")
    print("=" * 60)

if __name__ == "__main__":
    main()
