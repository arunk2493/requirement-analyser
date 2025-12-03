#!/usr/bin/env python
"""
Test script to verify auth endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING AUTH ENDPOINTS")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Auth health check
print("\n2. Testing /auth/health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/auth/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Register new user
print("\n3. Testing POST /auth/register...")
try:
    payload = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"   ✓ Access token received: {access_token[:20]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Login with credentials
print("\n4. Testing POST /auth/login...")
try:
    payload = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
