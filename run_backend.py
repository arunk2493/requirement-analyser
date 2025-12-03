#!/usr/bin/env python3
"""
Run the FastAPI backend server with proper configuration.
"""
import os
import sys

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

# Run uvicorn
if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting backend from: {os.getcwd()}")
    print(f"Python: {sys.executable}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
