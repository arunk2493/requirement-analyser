#!/usr/bin/env python
"""
Test if app.py can be imported without errors
"""
import sys
import traceback

print("Testing app.py import...")
try:
    import app
    print("✓ app.py imported successfully")
    print(f"✓ FastAPI app instance: {app.app}")
    print(f"✓ Routes registered: {len(app.app.routes)}")
    for route in app.app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.path}")
except Exception as e:
    print(f"✗ Failed to import app.py: {e}")
    traceback.print_exc()
    sys.exit(1)
