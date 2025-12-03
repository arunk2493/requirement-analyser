#!/usr/bin/env python3
"""
Test if routes/auth.py can be imported and router is created
"""
import sys
import traceback

print("Testing routes/auth.py import...")
try:
    from routes import auth
    print("✓ routes/auth.py imported successfully")
    
    if hasattr(auth, 'router'):
        print(f"✓ Auth router exists: {auth.router}")
        print(f"✓ Router prefix: {auth.router.prefix}")
        print(f"✓ Router tags: {auth.router.tags}")
        print(f"✓ Number of routes: {len(auth.router.routes)}")
        
        print("\n✓ Registered routes in auth router:")
        for route in auth.router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  - {route.path}: {list(route.methods)}")
            else:
                print(f"  - {route}")
    else:
        print("✗ Auth router not found!")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Failed to import routes/auth.py: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ AUTH ROUTER TEST PASSED")
print("=" * 60)
