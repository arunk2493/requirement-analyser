"""
Google OAuth 2.0 Integration for Gmail SSO
"""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/auth/callback")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

SCOPES = [
    "openid",
    "email",
    "profile"
]


def get_google_login_url(state: str = None) -> str:
    """
    Generate Google OAuth login URL
    User should be redirected to this URL to initiate login
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise ValueError("Google OAuth credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI in .env")
    
    scope = " ".join(SCOPES)
    auth_url = (
        f"{GOOGLE_AUTH_URL}?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline"
    )
    
    if state:
        auth_url += f"&state={state}"
    
    return auth_url


def exchange_code_for_token(authorization_code: str) -> Optional[Dict[str, Any]]:
    """
    Exchange authorization code for access token
    """
    try:
        payload = {
            "code": authorization_code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(GOOGLE_TOKEN_URL, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error exchanging code for token: {e}")
        return None


def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Get user info from Google using access token
    Returns: {sub, email, email_verified, name, picture, ...}
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting user info: {e}")
        return None


def validate_id_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate Google ID token and extract claims
    """
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token
        
        request = google_requests.Request()
        claims = id_token.verify_oauth2_token(token, request, GOOGLE_CLIENT_ID)
        
        # Verify token is not expired
        if claims['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')
        
        return claims
    except Exception as e:
        print(f"Error validating ID token: {e}")
        return None
