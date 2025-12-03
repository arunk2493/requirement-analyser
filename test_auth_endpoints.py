#!/usr/bin/env python3
"""
Quick diagnostic to check if auth endpoints are properly registered
"""

import sys
sys.path.insert(0, '/Users/arunkumaraswamy/Documents/Study/requirement-analyser')

try:
    print("1. Checking imports...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")
    
    from config.auth import Token, TokenData
    print("   ✓ Token models imported")
    
    from routes import auth
    print("   ✓ Auth routes imported")
    
    print("\n2. Checking router...")
    print(f"   Router prefix: {auth.router.prefix}")
    print(f"   Router tags: {auth.router.tags}")
    
    print("\n3. Listing auth routes...")
    for route in auth.router.routes:
        print(f"   - {route.path} [{route.methods}]")
    
    print("\n4. Expected endpoint: /auth/register")
    print("\n✅ All imports successful!")
    print("\nIf you still see 404:")
    print("  1. Make sure backend is restarted")
    print("  2. Check POSTGRES_URL is set in .env")
    print("  3. Make sure database table 'users' exists")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
