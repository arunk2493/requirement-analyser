#!/usr/bin/env python
"""
Test if auth.py can be imported
"""
import sys
import traceback

print("Testing auth.py import...")
try:
    from routes.auth import router
    print(f"✓ auth.py imported successfully")
    print(f"✓ Router: {router}")
    print(f"✓ Router prefix: {router.prefix}")
    print(f"✓ Number of routes: {len(router.routes)}")
    for route in router.routes:
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            print(f"  {methods} {route.path}")
except Exception as e:
    print(f"✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)
