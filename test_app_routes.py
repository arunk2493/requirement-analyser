#!/usr/bin/env python3
"""
Test if app.py can be imported and all routes are registered
"""
import sys
import traceback

print("=" * 60)
print("TESTING APP IMPORT AND ROUTE REGISTRATION")
print("=" * 60)

try:
    print("\n1. Importing app...")
    from app import app
    print("✓ app.py imported successfully")
    
    print("\n2. Checking registered routes...")
    print(f"Total routes: {len(app.routes)}")
    
    print("\n3. All registered endpoints:")
    for i, route in enumerate(app.routes):
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else ['N/A']
            print(f"  {i+1}. {route.path:30} {str(methods):40}")
        else:
            print(f"  {i+1}. {route}")
    
    print("\n4. Checking for specific endpoints:")
    endpoints_to_check = ['/health', '/auth/register', '/auth/login', '/auth/me']
    for endpoint in endpoints_to_check:
        found = any(hasattr(route, 'path') and route.path == endpoint for route in app.routes)
        status = "✓" if found else "✗"
        print(f"  {status} {endpoint}")
    
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ APP IMPORT TEST PASSED")
print("=" * 60)
